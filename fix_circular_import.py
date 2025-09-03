#!/usr/bin/env python3
"""
修复PyTorch循环导入问题
解决torch.types模块从torch导入device时的循环导入错误
"""

import os
import sys

def fix_circular_import():
    """修复torch.types.py中的循环导入问题"""
    
    types_file = "site-packages/torch/types.py"
    
    if not os.path.exists(types_file):
        print(f"文件不存在: {types_file}")
        return False
    
    # 读取原文件
    with open(types_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到问题代码并替换
    old_import = '''from torch import (  # noqa: F401
    device as _device,
    DispatchKey as DispatchKey,
    dtype as _dtype,
    layout as _layout,
    qscheme as _qscheme,
    Size as Size,
    SymBool as SymBool,
    SymFloat as SymFloat,
    SymInt as SymInt,
    Tensor as Tensor,
)'''
    
    new_import = '''# 延迟导入以避免循环导入问题
if TYPE_CHECKING:
    from torch import (  # noqa: F401
        device as _device,
        DispatchKey as DispatchKey,
        dtype as _dtype,
        layout as _layout,
        qscheme as _qscheme,
        Size as Size,
        SymBool as SymBool,
        SymFloat as SymFloat,
        SymInt as SymInt,
        Tensor as Tensor,
    )
else:
    # 运行时使用延迟导入
    def _get_device():
        from torch import device
        return device
    def _get_dispatch_key():
        from torch import DispatchKey
        return DispatchKey
    def _get_dtype():
        from torch import dtype
        return dtype
    def _get_layout():
        from torch import layout
        return layout
    def _get_qscheme():
        from torch import qscheme
        return qscheme
    def _get_size():
        from torch import Size
        return Size
    def _get_symbool():
        from torch import SymBool
        return SymBool
    def _get_symfloat():
        from torch import SymFloat
        return SymFloat
    def _get_symint():
        from torch import SymInt
        return SymInt
    def _get_tensor():
        from torch import Tensor
        return Tensor
    
    # 创建延迟导入的代理对象
    class _LazyImport:
        def __init__(self, getter):
            self._getter = getter
            self._value = None
        
        def __getattr__(self, name):
            if self._value is None:
                self._value = self._getter()
            return getattr(self._value, name)
        
        def __call__(self, *args, **kwargs):
            if self._value is None:
                self._value = self._getter()
            return self._value(*args, **kwargs)
    
    _device = _LazyImport(_get_device)
    DispatchKey = _LazyImport(_get_dispatch_key)
    _dtype = _LazyImport(_get_dtype)
    _layout = _LazyImport(_get_layout)
    _qscheme = _LazyImport(_get_qscheme)
    Size = _LazyImport(_get_size)
    SymBool = _LazyImport(_get_symbool)
    SymFloat = _LazyImport(_get_symfloat)
    SymInt = _LazyImport(_get_symint)
    Tensor = _LazyImport(_get_tensor)'''
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        # 写回文件
        with open(types_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("torch/types.py 循环导入修复完成")
        return True
    else:
        print("未找到需要修复的导入代码")
        return False

def fix_storage_import():
    """修复torch/storage.py中的导入问题"""
    
    storage_file = "site-packages/torch/storage.py"
    
    if not os.path.exists(storage_file):
        print(f"文件不存在: {storage_file}")
        return False
    
    # 读取原文件
    with open(storage_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到问题代码并替换
    old_import = "from torch.types import _bool, _int, Storage"
    
    new_import = '''# 延迟导入以避免循环导入问题
try:
    from torch.types import _bool, _int, Storage
except ImportError:
    # 如果导入失败，使用占位符
    _bool = bool
    _int = int
    Storage = object'''
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        # 写回文件
        with open(storage_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("torch/storage.py 导入修复完成")
        return True
    else:
        print("未找到需要修复的导入代码")
        return False

def main():
    """主函数"""
    print("开始修复PyTorch循环导入问题...")
    
    success1 = fix_circular_import()
    success2 = fix_storage_import()
    
    if success1 and success2:
        print("所有修复完成！")
        return True
    else:
        print("部分修复失败")
        return False

if __name__ == "__main__":
    main()
