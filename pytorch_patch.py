#!/usr/bin/env python3
"""
PyTorch PyInstaller兼容性补丁
解决PyTorch C扩展加载失败的问题
"""

import sys
import os

def patch_pytorch():
    """应用PyTorch补丁"""
    
    # 添加site-packages到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    site_packages_path = os.path.join(current_dir, 'site-packages')
    
    if site_packages_path not in sys.path:
        sys.path.insert(0, site_packages_path)
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = f"{site_packages_path}:{os.environ.get('PYTHONPATH', '')}"
    os.environ['TORCH_HOME'] = os.path.join(current_dir, 'models', 'torch')
    
    # 动态库路径
    torch_lib_path = os.path.join(site_packages_path, 'torch', 'lib')
    if os.path.exists(torch_lib_path):
        os.environ['DYLD_LIBRARY_PATH'] = f"{torch_lib_path}:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
        os.environ['LD_LIBRARY_PATH'] = f"{torch_lib_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    print("PyTorch补丁已应用")
    return True

if __name__ == "__main__":
    patch_pytorch()
