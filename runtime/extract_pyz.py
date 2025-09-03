import os
import sys
import zlib
import struct
import marshal


def extract_pyz(pyz_path: str, out_dir: str) -> None:
    with open(pyz_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'PYZ\0':
            raise RuntimeError('Not a PYZ file')

        pyc_magic = f.read(4)
        # Read TOC position
        (toc_pos,) = struct.unpack('!i', f.read(4))
        f.seek(toc_pos, os.SEEK_SET)
        toc = marshal.load(f)
        if isinstance(toc, list):
            toc = dict(toc)

        for key, (is_pkg, pos, length) in toc.items():
            try:
                name = key.decode('utf-8') if isinstance(key, (bytes, bytearray)) else str(key)
            except Exception:
                name = str(key)

            safe_name = name.replace('..', '__').replace('.', os.path.sep)
            if is_pkg == 1:
                rel_path = os.path.join(safe_name, '__init__.pyc')
            else:
                rel_path = safe_name + '.pyc'

            abs_path = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            f.seek(pos, os.SEEK_SET)
            data = f.read(length)
            try:
                data = zlib.decompress(data)
            except Exception:
                with open(abs_path + '.encrypted', 'wb') as w:
                    w.write(data)
                continue

            # Prepend pyc header (pyinstxtractor behavior)
            with open(abs_path, 'wb') as w:
                w.write(pyc_magic)
                # PEP 552 deterministic pycs header fields
                w.write(b'\0' * 4)
                w.write(b'\0' * 8)
                w.write(data)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: extract_pyz.py <PYZ file> [output_dir]')
        sys.exit(1)

    pyz_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(pyz_path)[0] + '_extracted'
    os.makedirs(out_dir, exist_ok=True)
    extract_pyz(pyz_path, out_dir)
    print(f'Extracted: {pyz_path} -> {out_dir}')


if __name__ == '__main__':
    main()


