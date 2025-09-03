#!/usr/bin/env python3
"""
批量修复torch._tensor.py中的_C.TensorBase引用
"""

import re

def fix_tensor_base_references():
    """修复torch._tensor.py中的_C.TensorBase引用"""
    
    file_path = "site-packages/torch/_tensor.py"
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有的_C.TensorBase引用
    # 1. 替换赋值语句
    content = re.sub(r'(\w+)\s*=\s*_C\.TensorBase\.(\w+)', r'# \1 = _C.TensorBase.\2', content)
    
    # 2. 替换类型注解中的引用
    content = re.sub(r'"torch\._C\.TensorBase"', r'"DummyTensorBase"', content)
    
    # 3. 替换函数调用中的引用
    content = re.sub(r'_C\.TensorBase\.(\w+)', r'# _C.TensorBase.\1', content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复torch._tensor.py中的_C.TensorBase引用")

if __name__ == "__main__":
    fix_tensor_base_references()
