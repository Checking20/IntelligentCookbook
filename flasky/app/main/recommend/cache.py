from redis import Redis

# Cache：基于redis的缓存(单例模式)
class Cache(object):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # 初始化：链接redis数据库
    def __init__(self):
        self.redis = Redis(host="localhost", port=6379)
