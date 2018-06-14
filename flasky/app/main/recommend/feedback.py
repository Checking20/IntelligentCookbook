
from .cache import Cache


# Feedback: 改善RecSys的模型
class Feedback:
    def __init__(self):
        # Redis缓存
        self.cache = Cache()
        # 权值更新折扣
        self.discount = 0.9

    # 记录推荐并设置监听
    def record(self, eid, vnum):
        # 设置失效时间(三分钟)
        TTL = 60*5
        if self.cache.redis.get('ridcount') is None:
            self.cache.redis.set('ridcount', 1)
        # 得到当前推荐的编号
        rid = self.cache.redis.incr("ridcount")
        print('recommendID: ', rid)

        # 如果不是使用组合，不用反馈：
        if vnum < 5:
            return rid
        # 是组合引擎则需要反馈
        rid_str = "rid" + str(rid)
        # 记录键对应的推荐引擎
        self.cache.redis.set(rid_str, eid)
        # 设置该键的生存期(TTL)
        self.cache.redis.expire(rid_str, TTL)
        return rid

    # 推荐有效，更新权值
    def match(self, rid):
        rid_str = "rid" + str(rid)
        eid = self.cache.redis.get(rid_str)
        if not (eid is None):
            print("rid %s match!"% str(rid))
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

    # 推荐无效，更新权值
    def not_match(self, rid):
        rid_str = "rid" + str(rid)
        eid = self.cache.redis.get(rid_str)
        if not (eid is None):
            print("rid %s not match!" % str(rid))
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













