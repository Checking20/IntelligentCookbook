
from .cache import Cache


# Feedback: 收集用户侧的信息用于RecSys的模型改善（使用Redis缓存）
class Feedback:
    def __init__(self):
        # Redis缓存
        self.cache = Cache()
        # 折扣
        self.discount = 0.9

    # 记录推荐
    def record(self, eid):
        # 设置失效时间(三分钟)
        TTL = 60*5
        if self.cache.redis.get('ridcount') is None:
            self.cache.redis.set('ridcount', 0)
        # 得到当前推荐的编号
        rid = self.cache.redis.incr("ridcount")
        print('recommendID: ', rid)
        rid_str = "rid" + str(rid)
        # 记录键对应的推荐引擎
        self.cache.redis.set(rid_str, eid)
        # 设置该键的生存期(TTL)
        self.cache.redis.expire(rid_str, TTL)
        return rid

    # 推荐有效
    def match(self, rid):
        rid_str = "rid" + str(rid)
        eid = self.cache.redis.get(rid_str)
        if not (eid is None):
            print("rid %d match!"%rid)
            eid = int(eid)
            eid_str = "eid" + str(eid)
            # 得到相应引擎的权重
            weight = float(self.cache.redis.get(eid_str))
            # 增加权值
            weight = weight*self.discount+1
            self.cache.redis.set(eid_str, weight)
            self.cache.redis.delete(rid_str)
            return True
        return False

    # 推荐无效
    def not_match(self, rid):
        rid_str = "rid" + str(rid)
        eid = self.cache.redis.get(rid_str)
        if not (eid is None):
            print("rid %d not match!" % rid)
            eid = int(eid)
            eid_str = "eid" + str(eid)
            # 得到相应引擎的权重
            weight = float(self.cache.redis.get(eid_str))
            # 降低权值
            weight = weight * self.discount + 0
            self.cache.redis.set(eid_str, weight)
            self.cache.redis.delete(rid_str)
            return True
        return False













