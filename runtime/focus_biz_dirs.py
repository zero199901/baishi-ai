import os
import shutil
import subprocess
from typing import List, Tuple


SRC_TREE = '/tmp/百世_src'
PYC_TREE = '/tmp/百世_extracted/PYZ-00_extracted'
OUT_ROOT = '/tmp/百世_focus'
PYCDC = '/tmp/pycdc/build/pycdc'
TARGET_DIRS = ['api', 'services']


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def decompile_pyc(pyc_path: str) -> Tuple[bool, bytes, bytes]:
    res = subprocess.run([PYCDC, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and bool(res.stdout), res.stdout, res.stderr


def process_dir(name: str) -> Tuple[int, int, int]:
    src_dir = os.path.join(SRC_TREE, name)
    pyc_dir = os.path.join(PYC_TREE, name)
    out_dir = os.path.join(OUT_ROOT, name)
    ensure_dir(out_dir)

    copied_py = 0
    decompiled_ok = 0
    fallback_pyc = 0

    # 1) 直接拷贝已经还原的 .py 源码
    if os.path.isdir(src_dir):
        for base, _, files in os.walk(src_dir):
            for fn in files:
                if not fn.endswith('.py'):
                    continue
                src = os.path.join(base, fn)
                rel = os.path.relpath(src, src_dir)
                dst = os.path.join(out_dir, rel)
                ensure_dir(os.path.dirname(dst))
                shutil.copy2(src, dst)
                copied_py += 1

    # 2) 针对缺失的 .py，尝试用 pycdc 从 .pyc 反编译
    if os.path.isdir(pyc_dir):
        for base, _, files in os.walk(pyc_dir):
            for fn in files:
                if not fn.endswith('.pyc'):
                    continue
                pyc_path = os.path.join(base, fn)
                rel_pyc = os.path.relpath(pyc_path, pyc_dir)
                rel_py = rel_pyc[:-4] + '.py'
                out_py = os.path.join(out_dir, rel_py)
                if os.path.exists(out_py):
                    continue
                ensure_dir(os.path.dirname(out_py))
                ok, stdout, stderr = decompile_pyc(pyc_path)
                if ok:
                    with open(out_py, 'wb') as w:
                        w.write(stdout)
                    decompiled_ok += 1
                else:
                    # 3) 反编译失败则附带 .pyc 与失败说明
                    fallback = out_py + '.pyc'
                    shutil.copy2(pyc_path, fallback)
                    with open(out_py + '.FAILED.txt', 'wb') as w:
                        w.write(stderr or b'empty output')
                    fallback_pyc += 1

    return copied_py, decompiled_ok, fallback_pyc


def main() -> None:
    ensure_dir(OUT_ROOT)
    summary_lines: List[str] = []
    total_copied = total_decompiled = total_fallback = 0
    for name in TARGET_DIRS:
        c, d, f = process_dir(name)
        total_copied += c
        total_decompiled += d
        total_fallback += f
        summary_lines.append(f'{name}: copied_py={c}, decompiled_ok={d}, fallback_pyc={f}')

    with open(os.path.join(OUT_ROOT, '_SUMMARY.txt'), 'w', encoding='utf-8') as w:
        w.write('\n'.join(summary_lines) + '\n')
        w.write(f'TOTAL copied_py={total_copied}, decompiled_ok={total_decompiled}, fallback_pyc={total_fallback}\n')

    print(f'Done. OUT={OUT_ROOT}; TOTAL copied={total_copied}, decompiled={total_decompiled}, fallback={total_fallback}')


if __name__ == '__main__':
    main()


