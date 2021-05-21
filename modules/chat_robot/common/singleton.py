"""
本类是用来约束单例类，
使用方式：
class SingletonClass(metaclass=Singleton):
    def __init__(self, name):
    self.name = name

验证：
instance1 = SingletonClass("111")
instance2 = SingletonClass("222")
print(instance1,instance2)

输出的地址是一致的
"""
import threading


class Singleton(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
