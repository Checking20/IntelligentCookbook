import threading
from operator import itemgetter
from app.main.recommend.cache import Cache
from app.main.recommend.feedback import Feedback
from app.main.recommend.functions import softmax, random_choose
from app.main.recommend.itemCF import ItemBasedCF
from app.main.recommend.userCF import UserBasedCF
from app.main.recommend.LFM import LFM
from app.main.dataprocess.topk import get_topk
from .data.record2table import record2table
from .filter import Filter
from .rank import Ranker
from ... import db
from ...models import UserItem, ItemSim, UCFRec, LFMRec

# 推荐个数
rec_N = 20


# RecEngine：基本的推荐引擎（接口）
class RecEngine:
    @staticmethod
    def recommend(uid):
        pass


# TopEngine：基于热门的推荐引擎（在线）
class TopEngine(RecEngine):
    @staticmethod
    def recommend(uid):
        get_topk(rec_N)


# UCFEngine：基于userCF的推荐引擎（离线）
class UCFEngine(RecEngine):
    # 基于UserCF推荐(利用离线数据)
    @staticmethod
    def recommend(uid):
        rec_dict = {}
        for item in UCFRec.query.filter_by(uid=uid).all():
            rec_dict[item.cid] = item.score
        return sorted(rec_dict.items(), key=itemgetter(1), reverse=True)[:rec_N]


# ICFEngine：基于itemCF的推荐引擎(离线)
class ICFEngine(RecEngine):
    # 基于ItemCF推荐
    @staticmethod
    def recommend(uid):
        return ICFEngine.recommend_online(uid)

    # 推荐（利用离线数据+在线数据）
    @staticmethod
    def recommend_online(uid):
        # 产生行为的所有产品
        watched_item_dict = {}
        # 产生行为的所有产品
        for item in UserItem.query.filter_by(uid=uid).all():
            watched_item_dict[item.cid] = item.weight

        rank = {}
        for cid, weight in watched_item_dict.items():
            for sim_item in ItemSim.query.filter_by(cid1=cid).all():
                if sim_item.cid2 in watched_item_dict:
                    continue
                rank.setdefault(sim_item.cid2, 0)
                # 排名的依据——>推荐菜谱与该已看菜谱的相似度(累计)*用户对已看菜谱的评分
                rank[sim_item.cid2] += sim_item.sim * weight
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:rec_N]

    # 推荐(利用离线数据)
    # ——被删除——


# LFMEngine：基于隐语义模型的推荐引擎（离线）
class LFMEngine(RecEngine):
    # 基于隐语义模型推荐(利用离线数据)
    @staticmethod
    def recommend(uid):
        rec_dict ={}
        for item in LFMRec.query.filter_by(uid=uid).all():
            rec_dict[item.cid] = item.score
        return sorted(rec_dict.items(), key=itemgetter(1), reverse=True)[:rec_N]



# 引擎和其编号的映射
EngineMap = {
    'eid0': TopEngine,
    'eid1': ICFEngine,
    'eid2': UCFEngine,
    'eid3': LFMEngine,
}

# 引擎离线计算和其编号的映射
EngineCalMap = {
    'eid1': ItemBasedCF,
    'eid2': UserBasedCF,
    'eid3': LFM,
}


# RecSys推荐系统：针对所有用户，由若干推荐引擎何其权重，Filter过滤器，Rank排名器，和Feedback反馈器和Cache构成
class RecSys:
    def __init__(self, **kwargs):
        self.filter = Filter()
        self.rank = Ranker()
        self.ra = None
        self.cache = Cache()
        self.fb = Feedback()
        # 在综合引擎被使用的引擎
        self.engines = [1]

        # 是否有定制化选择
        if 'engines' in kwargs:
            self.engines = list(kwargs['engines'])
        # 初始化引擎权重
        for engine in self.engines:
            if self.cache.redis.get(('eid'+str(engine))) is None:
                self.cache.redis.set(('eid'+str(engine)), 0)
        # 是否初始化权值
        if 'init' in kwargs and kwargs['init'] is True:
            for engine in self.engines:
                self.cache.redis.set(('eid' + str(engine)), 0)


    # 推荐方式
    '''
        1. 如果用户没有访问过任何菜谱，使用TopEngine
        2. 如果用户访问菜谱数目少于5，使用itemCF
        3. 否则使用组合引擎
    '''
    def normal_rec(self, user, vnum):
        if vnum == 0:
            return 0, TopEngine.recommend(user)
        elif vnum < 5:
            return 1, ICFEngine.recommend(user)
        return self.combine_engines(user)

    # 组合引擎（Bandit）
    def combine_engines(self, user):
        weight_dict = {}
        for engine in self.engines:
            weight_dict[engine] = float(self.cache.redis.get(('eid'+str(engine))))
        q_dict = softmax(weight_dict)
        ceid = random_choose(q_dict)
        return ceid, EngineMap["eid"+str(ceid)].recommend(user)

    # 推荐列表被访问的反馈
    def match(self, rid):
        return self.fb.match(rid)

    # 离线计算推荐表：如果引擎需要离线数据支持就计算
    def calc(self,**kwargs):
        db.create_all()
        data = record2table()
        for id in self.engines:
            strid = 'eid'+str(id)
            if strid in EngineCalMap:
                EngineCalMap[strid](**kwargs).refresh(data)

    # 推荐系统工作流程
    def recommend(self, user):
        # 推荐保留时间
        TTL_rec = 70
        # 推荐拒绝时间
        TTL_rej = 60

        # 检查redis中是否有推荐缓存,如果有，直接返回推荐
        user_str = 'recfor'+str(user)
        if self.cache.redis.llen(user_str) != 0:
            print("recommend from redis!")
            rec_list = []
            rid = int(self.cache.redis.lrange(user_str, 0, 0)[0])
            raw_list = self.cache.redis.lrange(user_str, 1, rec_N)
            for item in raw_list:
                rec_list.append(bytes.decode(item))
            return {"rid": rid, "rec_list": rec_list}

        # ——推荐系统流程——
        print("need to calculate!")
        # 0. 得到用户访问过的菜谱数量
        vnum = len(UserItem.query.filter_by(uid=user).all())
        # 1. 计算初始推荐列表(还有使用的引擎)
        ceid, raw_list = self.normal_rec(user, vnum)
        # 2. 对初始列表过滤
        filtered_list = self.filter.filter_item(user, raw_list)
        # 3. 对过滤后的列表进行排序
        rank_list = self.rank.rank(filtered_list)
        # 4. 生成推荐结果
        rec_list = [cid for (cid, score) in rank_list]
        # 5. 反馈器记录这次推荐
        rid = self.fb.record(ceid, vnum)
        # 6. 设置定时器
        timer = threading.Timer(TTL_rej, self.fb.not_match, args=[rid])
        timer.start()
        # 7. 将推荐结果缓存进Redis
        for item in rec_list:
            self.cache.redis.lpush(user_str, item)
        self.cache.redis.lpush(user_str, rid)
        self.cache.redis.expire(user_str, TTL_rec)
        return {"rid": rid, "rec_list": rec_list}
