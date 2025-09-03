"""
最终修补torch __init__.py文件
"""

import os

def patch_torch_init_final():
    """最终修补torch __init__.py文件"""
    
    torch_init_path = "site-packages/torch/__init__.py"
    
    if not os.path.exists(torch_init_path):
        print(f"文件不存在: {torch_init_path}")
        return False
    
    # 读取原文件
    with open(torch_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在文件开头添加虚拟_C模块导入
    patch_code = '''# 导入虚拟_C模块以绕过C扩展问题
try:
    from . import _C
    print("使用虚拟torch._C模块")
except ImportError:
    pass

'''
    
    # 在import语句后插入补丁代码
    import_section = '''import builtins
import ctypes
import functools
import glob
import importlib
import inspect
import math
import os
import platform
import sys
import textwrap
import threading'''
    
    if import_section in content:
        content = content.replace(import_section, import_section + '\n' + patch_code)
        
        # 写回文件
        with open(torch_init_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("torch __init__.py 最终修补完成")
        return True
    else:
        print("未找到import部分")
        return False

if __name__ == "__main__":
    patch_torch_init_final()
