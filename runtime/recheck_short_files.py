import os
import subprocess
from typing import List, Tuple


SRC_ROOT = '/tmp/百世_src'
PYC_ROOT = '/tmp/百世_extracted/PYZ-00_extracted'
PYCDC = '/tmp/pycdc/build/pycdc'
MIN_LINES = 20  # 阈值：过短文件重试
PY_VERSIONS = ['3.10']  # 固定为 Python 3.10


def count_lines(path: str) -> int:
    try:
        with open(path, 'rb') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def find_short_py_files(root: str, min_lines: int) -> List[str]:
    out: List[str] = []
    for base, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.py'):
                continue
            p = os.path.join(base, fn)
            if count_lines(p) < min_lines:
                out.append(p)
    return out


def decompyle3_rebuild_any(pyc_path: str, out_dir: str) -> Tuple[bool, str]:
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:" + env.get('PATH', '')
    last_err = ''
    for ver in PY_VERSIONS:
        r = subprocess.run(['decompyle3', '-p', ver, '-o', out_dir, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if r.returncode == 0:
            return True, ''
        last_err = r.stderr.decode('utf-8', errors='ignore')
    return False, last_err


def uncompyle6_rebuild_any(pyc_path: str, out_dir: str) -> Tuple[bool, str]:
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:" + env.get('PATH', '')
    last_err = ''
    for ver in PY_VERSIONS:
        r = subprocess.run(['uncompyle6', f'--py={ver}', '-o', out_dir, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if r.returncode == 0:
            return True, ''
        last_err = r.stderr.decode('utf-8', errors='ignore')
    return False, last_err


def pycdc_rebuild(pyc_path: str, out_file: str) -> bool:
    r = subprocess.run([PYCDC, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode == 0 and r.stdout:
        with open(out_file, 'wb') as w:
            w.write(r.stdout)
        return True
    return False


def map_py_to_pyc(py_path: str) -> str:
    rel = os.path.relpath(py_path, SRC_ROOT)
    return os.path.join(PYC_ROOT, rel[:-3] + '.pyc')


def main() -> None:
    short_files = find_short_py_files(SRC_ROOT, MIN_LINES)
    fixed = 0
    checked = 0
    report: List[str] = []
    for py in short_files:
        checked += 1
        pyc = map_py_to_pyc(py)
        if not os.path.exists(pyc):
            report.append(f'NO_PYC: {py}')
            continue
        out_dir = os.path.dirname(py)
        print(f'Checking: {pyc} {py}')
        # 顺序：decompyle3(多版本) -> uncompyle6(多版本) -> pycdc
        ok, err1 = decompyle3_rebuild_any(pyc, out_dir)
        if ok:
            fixed += 1
            continue
        ok, err2 = uncompyle6_rebuild_any(pyc, out_dir)
        if ok:
            fixed += 1
            continue
        if pycdc_rebuild(pyc, py):
            fixed += 1
            continue
        report.append(f'FAILED_RECHECK: {py} | decompyle3_err={len(err1)}B, uncompyle6_err={len(err2)}B')

    summary = f'Checked={checked}, Fixed={fixed}, Remaining={len(report)}'
    print(summary)
    if report:
        with open('/tmp/recheck_report.txt', 'w', encoding='utf-8') as w:
            w.write('\n'.join(report) + '\n' + summary + '\n')
        print('Report: /tmp/recheck_report.txt')


if __name__ == '__main__':
    main()


