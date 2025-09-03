#!/usr/bin/env python3
"""
PyTorch PyInstaller兼容性补丁
解决PyTorch C扩展加载失败的问题
"""

import sys
import os
import importlib.util

def patch_torch_import():
    """修补torch导入问题"""
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    site_packages_path = os.path.join(current_dir, 'site-packages')
    
    # 添加site-packages到Python路径
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
    
    # 尝试修复torch._C导入问题
    try:
        # 先尝试直接导入torch
        import torch
        print("PyTorch导入成功")
        return True
    except ImportError as e:
        print(f"PyTorch导入失败: {e}")
        
        # 尝试修复_C模块导入
        try:
            # 手动加载_C模块
            torch_path = os.path.join(site_packages_path, 'torch')
            _c_so_path = os.path.join(torch_path, '_C.cpython-311-darwin.so')
            
            if os.path.exists(_c_so_path):
                # 使用importlib加载模块
                spec = importlib.util.spec_from_file_location("torch._C", _c_so_path)
                if spec and spec.loader:
                    _c_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(_c_module)
                    
                    # 将模块添加到sys.modules
                    sys.modules['torch._C'] = _c_module
                    print("手动加载torch._C成功")
                    
                    # 再次尝试导入torch
                    import torch
                    print("PyTorch导入成功（通过手动加载_C）")
                    return True
        except Exception as e2:
            print(f"手动加载torch._C失败: {e2}")
    
    return False

if __name__ == "__main__":
    success = patch_torch_import()
    if success:
        print("PyTorch补丁应用成功")
    else:
        print("PyTorch补丁应用失败")
