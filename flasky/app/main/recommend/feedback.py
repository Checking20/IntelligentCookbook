
'''
# Feedback：收集用户侧的推荐反馈用于RecSys的模型改善（使用redis缓存）：
class Feedback:
    # 初始化：配置缓存
    def __init__(self, cache):
        self.cache = cache
        self.discount = 0.9

    # 记录推荐信息
    def record(self, eid, rec_list):
        if self.cache.redis.get('ridcount') is None:
            self.cache.redis.set('ridcount', 0)
        rid = self.cache.redis.incr("ridcount")
        # 将推荐列表以set类型存入redis
        print("ridset"+str(rid))
        for (cid, weight) in rec_list:
            self.cache.redis.sadd(("ridset" + str(rid)), cid)

        # 将推荐编号映射到引擎
        self.cache.redis.set(("rid"+str(rid)), eid)

        # 如果相应引擎未有值，则设置初值
        if self.cache.redis.get(eid) is None:
            ek = 'eid'+str(eid)
            self.cache.redis.set(ek, 0)

    # 查询推荐历史
    def match(self, rid, cid):
        # 通过推荐编号得到引擎编号
        eid = self.cache.redis.get(("rid"+str(rid)))
        # 得到引擎当前权值
        weight = int(self.cache.redis.get("eid"+str(eid)))
        # 如果该商品在该推荐列表，奖励为1,反之为0
        if self.cache.redis.sismember(('ridset' + str(rid)), cid):
            weight = 1+weight*self.discount
        else:
            weight = 0+weight*self.discount
        # 将新的权值写回
        self.cache.redis.set(("eid"+str(eid)), weight)
'''


# Feedback: 收集用户侧的信息用于RecSys的模型改善（使用Redis缓存）
class Feedback:
    def __init__(self, cache):
        # Redis缓存
        self.cache = cache
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
    def notmatch(self, rid):
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













