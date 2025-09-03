import os
import sys
import traceback
from typing import Optional


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def find_pyc_files(root: str):
    for base, _, files in os.walk(root):
        for fn in files:
            if fn.endswith('.pyc'):
                yield os.path.join(base, fn)


def try_decompile_with_decompyle3(src_pyc: str, dst_py: str) -> bool:
    try:
        import decompyle3
        # decompyle3 API stability varies; use "main" facade if present
        try:
            from decompyle3.main import decompile
            with open(dst_py, 'w', encoding='utf-8') as w:
                ok = decompile(src_pyc, out=w)
            return bool(ok)
        except Exception:
            # Fallback to decompile_file if exposed
            try:
                from decompyle3.main import decompile_file
                with open(dst_py, 'w', encoding='utf-8') as w:
                    decompile_file(src_pyc, out=w)
                return True
            except Exception:
                return False
    except Exception:
        return False


def try_decompile_with_uncompyle6(src_pyc: str, dst_py: str) -> bool:
    try:
        import uncompyle6
        try:
            from uncompyle6.main import decompile
            with open(dst_py, 'w', encoding='utf-8') as w:
                decompile(src_pyc, out=w)
            return True
        except Exception:
            try:
                from uncompyle6.api import decompile_file
                with open(dst_py, 'w', encoding='utf-8') as w:
                    decompile_file(src_pyc, outstream=w)
                return True
            except Exception:
                return False
    except Exception:
        return False


def decompile_one(src_pyc: str, out_root: str, in_root: str) -> bool:
    rel = os.path.relpath(src_pyc, in_root)[:-4] + '.py'
    dst = os.path.join(out_root, rel)
    ensure_dir(os.path.dirname(dst))

    if try_decompile_with_decompyle3(src_pyc, dst):
        return True
    if try_decompile_with_uncompyle6(src_pyc, dst):
        return True

    # If both failed, write a stub note with traceback for manual follow-up
    try:
        with open(dst + '.FAILED.txt', 'w', encoding='utf-8') as w:
            w.write(f'Failed to decompile: {src_pyc}\n')
    except Exception:
        pass
    return False


def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: decompile_pyc_batch.py <pyc_root> <out_root>')
        sys.exit(1)

    pyc_root = os.path.abspath(sys.argv[1])
    out_root = os.path.abspath(sys.argv[2])
    ensure_dir(out_root)

    total = 0
    ok = 0
    for pyc_path in find_pyc_files(pyc_root):
        total += 1
        if decompile_one(pyc_path, out_root, pyc_root):
            ok += 1

    print(f'Decompiled OK: {ok}/{total}. Output: {out_root}')


if __name__ == '__main__':
    main()


