"""
临时torch模块存根
用于绕过PyTorch导入问题
"""

import sys
import os

# 创建一个最小的torch模块存根
class TorchStub:
    def __init__(self):
        self.__version__ = "2.8.0"
        self.cuda = None
        self.device = None
        self.tensor = None
        self.nn = None
        self.optim = None
        self.utils = None
        
    def __getattr__(self, name):
        # 返回一个空函数，避免AttributeError
        def dummy(*args, **kwargs):
            print(f"警告: torch.{name} 被调用但PyTorch未正确加载")
            return None
        return dummy

# 将存根模块添加到sys.modules
sys.modules['torch'] = TorchStub()
sys.modules['torch._C'] = TorchStub()

print("已加载torch存根模块")
