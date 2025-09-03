import os
import subprocess
from typing import List, Tuple

SRC_ROOT = '/tmp/百世_src'
PYC_ROOT = '/tmp/百世_extracted/PYZ-00_extracted'
PYCDC = '/tmp/pycdc/build/pycdc'


def find_failed() -> List[str]:
    failed_notes: List[str] = []
    for base, _, files in os.walk(SRC_ROOT):
        for fn in files:
            if fn.endswith('.FAILED.txt'):
                failed_notes.append(os.path.join(base, fn))
    return failed_notes


def find_failed_from_report(report_path: str = '/tmp/recheck_report.txt') -> List[str]:
    failed_py_files: List[str] = []
    if not os.path.exists(report_path):
        return failed_py_files
    try:
        with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('FAILED_RECHECK:'):
                    continue
                # format: FAILED_RECHECK: <py_path> | decompyle3_err=..., uncompyle6_err=...
                try:
                    left = line.split('|', 1)[0]
                    py_path = left.split(':', 1)[1].strip()
                    if py_path:
                        failed_py_files.append(py_path)
                except Exception:
                    continue
    except Exception:
        pass
    return failed_py_files


def map_failed_to_pyc(failed_note: str) -> Tuple[str, str]:
    # failed_note is something like /tmp/百世_src/pkg/mod.py.FAILED.txt
    py_path = failed_note[:-11]  # strip .FAILED.txt
    rel = os.path.relpath(py_path, SRC_ROOT)
    pyc_rel = rel[:-3] + '.pyc'
    pyc_path = os.path.join(PYC_ROOT, pyc_rel)
    return py_path, pyc_path


def try_decompyle3(pyc_path: str, out_dir: str) -> bool:
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:" + env.get('PATH', '')
    r = subprocess.run(['decompyle3', '-o', out_dir, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return r.returncode == 0


def try_uncompyle6(pyc_path: str, out_dir: str) -> bool:
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~')}/.local/bin:" + env.get('PATH', '')
    r = subprocess.run(['uncompyle6', '-o', out_dir, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return r.returncode == 0


def try_pycdc(pyc_path: str, out_py: str) -> bool:
    r = subprocess.run([PYCDC, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode == 0 and r.stdout:
        with open(out_py, 'wb') as w:
            w.write(r.stdout)
        return True
    return False


def _safe_remove(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def main() -> None:
    failures = find_failed()
    fixed = 0
    still_failed = 0
    force_pycdc_only = os.environ.get('FORCE_PYCDC_ONLY') == '1'

    # Case 1: has .FAILED.txt markers
    for note in failures:
        print(f"Retrying: {note}")
        py_path, pyc_path = map_failed_to_pyc(note)
        out_dir = os.path.dirname(py_path)
        if not os.path.exists(pyc_path):
            still_failed += 1
            continue
        if force_pycdc_only:
            if try_pycdc(pyc_path, py_path):
                _safe_remove(note)
                fixed += 1
                continue
        else:
            if try_decompyle3(pyc_path, out_dir):
                _safe_remove(note)
                fixed += 1
                continue
            if try_uncompyle6(pyc_path, out_dir):
                _safe_remove(note)
                fixed += 1
                continue
            if try_pycdc(pyc_path, py_path):
                _safe_remove(note)
                fixed += 1
                continue
        still_failed += 1

    # Case 2: fall back to parsing /tmp/recheck_report.txt
    if not failures:
        failed_py_list = find_failed_from_report()
        for py_path in failed_py_list:
            rel = os.path.relpath(py_path, SRC_ROOT)
            pyc_path = os.path.join(PYC_ROOT, rel[:-3] + '.pyc')
            out_dir = os.path.dirname(py_path)
            print(f"Retrying(from report): {pyc_path} -> {py_path}")
            if not os.path.exists(pyc_path):
                still_failed += 1
                continue
            if force_pycdc_only:
                if try_pycdc(pyc_path, py_path):
                    fixed += 1
                    continue
            else:
                if try_decompyle3(pyc_path, out_dir):
                    fixed += 1
                    continue
                if try_uncompyle6(pyc_path, out_dir):
                    fixed += 1
                    continue
                if try_pycdc(pyc_path, py_path):
                    fixed += 1
                    continue
            still_failed += 1

        print(f"Retried(from report): {len(failed_py_list)}, Fixed: {fixed}, Remaining: {still_failed}")
    else:
        print(f"Retried: {len(failures)}, Fixed: {fixed}, Remaining: {still_failed}")


if __name__ == '__main__':
    main()
