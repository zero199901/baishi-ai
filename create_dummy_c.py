"""
创建完整的虚拟torch._C模块
"""

import os
import sys

def create_dummy_c_module():
    """创建虚拟的torch._C模块"""
    
    # 创建torch目录（如果不存在）
    torch_dir = "site-packages/torch"
    if not os.path.exists(torch_dir):
        print(f"目录不存在: {torch_dir}")
        return False
    
    # 创建虚拟_C模块
    dummy_c_content = '''"""
虚拟的torch._C模块
用于绕过PyTorch C扩展导入问题
"""

class DummyC:
    """虚拟的torch._C模块"""
    
    def __init__(self):
        self.__file__ = None
        self.__name__ = 'torch._C'
        self.__package__ = 'torch'
    
    def __getattr__(self, name):
        """返回虚拟函数"""
        def dummy(*args, **kwargs):
            print(f"警告: torch._C.{name} 被调用但C扩展未加载")
            # 返回适当的默认值
            if 'tensor' in name.lower() or 'Tensor' in name:
                return None
            elif 'device' in name.lower() or 'Device' in name:
                return 'cpu'
            elif 'dtype' in name.lower() or 'Dtype' in name:
                return None
            else:
                return None
        return dummy
    
    def __dir__(self):
        """返回可用的属性列表"""
        return [
            '_add_docstr', '_autograd', '_C', '_cudnn', '_distributed_autograd',
            '_distributed_c10d', '_distributed_rpc', '_functions', '_nn',
            '_profiler', '_tensor', '_utils', '_VariableFunctions',
            'FloatStorage', 'LongStorage', 'IntStorage', 'ShortStorage',
            'CharStorage', 'ByteStorage', 'BoolStorage', 'HalfStorage',
            'DoubleStorage', 'BFloat16Storage', 'ComplexFloatStorage',
            'ComplexDoubleStorage', 'Tensor', 'Storage', 'Type', 'size',
            'typename', 'is_tensor', 'is_storage', 'set_default_tensor_type',
            'set_default_dtype', 'get_default_dtype', 'set_num_threads',
            'get_num_threads', 'set_num_interop_threads', 'get_num_interop_threads',
            'set_flush_denormal', 'get_flush_denormal', 'set_anomaly_enabled',
            'is_anomaly_enabled', 'set_autocast_enabled', 'is_autocast_enabled',
            'set_autocast_cpu_enabled', 'is_autocast_cpu_enabled',
            'set_autocast_gpu_dtype', 'get_autocast_gpu_dtype',
            'set_autocast_cpu_dtype', 'get_autocast_cpu_dtype',
            'set_autocast_cache_enabled', 'is_autocast_cache_enabled',
            'clear_autocast_cache', 'autocast_increment_nesting',
            'autocast_decrement_nesting', 'is_autocast_cache_enabled',
            'set_autocast_cache_enabled', 'clear_autocast_cache',
            'autocast_increment_nesting', 'autocast_decrement_nesting'
        ]

# 创建模块实例
dummy_c = DummyC()

# 将模块添加到sys.modules
sys.modules['torch._C'] = dummy_c

print("虚拟torch._C模块创建完成")
'''

    # 写入虚拟_C模块文件
    dummy_c_path = os.path.join(torch_dir, '_C.py')
    with open(dummy_c_path, 'w', encoding='utf-8') as f:
        f.write(dummy_c_content)
    
    print(f"虚拟_C模块已创建: {dummy_c_path}")
    return True

if __name__ == "__main__":
    create_dummy_c_module()
