import os
import sys
import ast
import shutil
import subprocess
from typing import Set, List, Tuple, Optional, Deque
from collections import deque


PYC_MAIN = '/tmp/百世_extracted/main.pyc'
SRC_TREE = '/tmp/百世_src'
OUT_ROOT = '/tmp/百世_main'
PYCDC = '/tmp/pycdc/build/pycdc'


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def decompile_main(pyc_path: str, out_py: str) -> None:
    ensure_dir(os.path.dirname(out_py))
    res = subprocess.run([PYCDC, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or not res.stdout:
        raise RuntimeError(f'pycdc failed: {res.stderr.decode(errors="ignore")[:200]}')
    with open(out_py, 'wb') as w:
        w.write(res.stdout)


def parse_imports(py_path: str) -> Set[str]:
    with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    tree = ast.parse(code, filename=py_path)
    modules: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    # 记录完整模块名与顶级名，提升解析命中率
                    modules.add(alias.name)
                    modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
                modules.add(node.module.split('.')[0])
    return modules


def resolve_module_paths(module: str, src_root: str) -> Tuple[Optional[str], Optional[str]]:
    # 返回 (模块文件路径, 包目录路径)
    rel_file = module.replace('.', '/') + '.py'
    rel_pkg = module.replace('.', '/')
    src_file = os.path.join(src_root, rel_file)
    src_pkg = os.path.join(src_root, rel_pkg)
    return (src_file if os.path.isfile(src_file) else None,
            src_pkg if os.path.isdir(src_pkg) else None)


def copy_module(module: str, src_root: str, out_root: str, copied: Set[str]) -> Tuple[bool, List[str]]:
    if module in copied:
        return True, []
    src_file, src_pkg = resolve_module_paths(module, src_root)
    collected_files: List[str] = []

    if src_file:
        rel_file = module.replace('.', '/') + '.py'
        dst_file = os.path.join(out_root, rel_file)
        ensure_dir(os.path.dirname(dst_file))
        shutil.copy2(src_file, dst_file)
        collected_files.append(dst_file)
        copied.add(module)
        return True, collected_files
    if src_pkg:
        rel_pkg = module.replace('.', '/')
        dst_pkg = os.path.join(out_root, rel_pkg)
        ensure_dir(os.path.dirname(dst_pkg))
        if os.path.exists(dst_pkg):
            shutil.rmtree(dst_pkg)
        shutil.copytree(src_pkg, dst_pkg)
        # 尝试加入 __init__.py 作为后续解析入口
        init_py = os.path.join(dst_pkg, '__init__.py')
        if os.path.isfile(init_py):
            collected_files.append(init_py)
        copied.add(module)
        return True, collected_files
    return False, []


def main() -> None:
    ensure_dir(OUT_ROOT)
    main_py = os.path.join(OUT_ROOT, 'main.py')
    decompile_main(PYC_MAIN, main_py)

    # 递归解析：从 main.py 出发，逐层收集依赖
    to_visit_files: Deque[str] = deque([main_py])
    seen_files: Set[str] = set()
    copied: Set[str] = set()
    missing: List[str] = []

    while to_visit_files:
        cur = to_visit_files.popleft()
        if cur in seen_files:
            continue
        seen_files.add(cur)
        try:
            mods = parse_imports(cur)
        except Exception:
            continue

        for mod in sorted(mods):
            ok, new_files = copy_module(mod, SRC_TREE, OUT_ROOT, copied)
            if not ok:
                # 仅记录在源码树中不存在的模块；标准库与三方库可能无须复制
                src_file, src_pkg = resolve_module_paths(mod, SRC_TREE)
                if not src_file and not src_pkg:
                    missing.append(mod)
                continue
            for nf in new_files:
                if nf not in seen_files:
                    to_visit_files.append(nf)

    # write a summary
    with open(os.path.join(OUT_ROOT, '_DEPENDENCY_SUMMARY.txt'), 'w', encoding='utf-8') as w:
        w.write('Collected modules from main.py imports (recursive)\n')
        w.write(f'Files scanned: {len(seen_files)}\n')
        w.write(f'Copied modules/packages: {len(copied)}\n')
        if missing:
            w.write('Missing (not found in extracted src tree):\n')
            for m in missing:
                w.write(f'- {m}\n')

    print(f'Done. OUT={OUT_ROOT}, copied={len(copied)}, missing={len(missing)}, scanned_files={len(seen_files)}')


if __name__ == '__main__':
    main()


