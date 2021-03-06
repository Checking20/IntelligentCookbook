from .filter import Filter
from .rank import Ranker
from .data.record2table import record2table
from operator import itemgetter
from app.main.recommend.userCF import UserBasedCF as UCF
from app.main.recommend.itemCF import ItemBasedCF as ICF
from app.main.recommend.feedback import Feedback
from app.main.recommend.cache import Cache
from app.main.recommend.functions import softmax, random_choose
from ...models import UserItem, ItemSim, UCFRec, ICFRec
from ... import db
import threading

# 推荐个数(未剪裁)
rec_N = 20


# RecEngine：基本的推荐引擎
class RecEngine:
    @staticmethod
    def recommend(uid):
        pass


# RandomEngine:随机的推荐引擎
class RandomEngine(RecEngine):
    @staticmethod
    def recommend(uid):
        rec_dict = {}


# UCFEngine：基于userCF的推荐引擎
class UCFEngine(RecEngine):
    # 推荐(利用离线数据)
    @staticmethod
    def recommend(uid):
        rec_dict = {}
        for item in UCFRec.query.filter_by(uid=uid).all():
            rec_dict[item.cid] = item.score
        return sorted(rec_dict.items(), key=itemgetter(1), reverse=True)[:rec_N]


# ICFEngine：基于itemCF的推荐引擎
class ICFEngine(RecEngine):
    # 推荐(统一接口)
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


# 引擎和其编号的映射
EngineMap = {
    'eid1': ICFEngine,
    'eid2': UCFEngine,
    'eid3': RandomEngine,
}


# RecSys推荐系统：针对所有用户，由若干推荐引擎何其权重，Filter过滤器，Rank排名器，和Feedback反馈器和Cache构成
class RecSys:

    def __init__(self, **kwargs):
        self.filter = Filter()
        self.rank = Ranker()
        self.ra = None
        self.cache = Cache()
        self.fb = Feedback()
        self.engines = [1, 2]
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

    # 模型合并方式
    def combine(self, user):
        weight_dict = {}
        for engine in self.engines:
            weight_dict[engine] = float(self.cache.redis.get(('eid'+str(engine))))
        q_dict = softmax(weight_dict)
        ceid = random_choose(q_dict)
        return ceid, EngineMap["eid"+str(ceid)].recommend(user)

    # 推荐列表被访问的反馈
    def match(self, rid):
        return self.fb.match(rid)

    @staticmethod
    # 离线计算推荐表
    def calc():
        db.create_all()
        # 清空之前的数据
        for item in ItemSim.query.all():
            db.session.delete(item)
        for item in ICFRec.query.all():
            db.session.delete(item)
        for item in UCFRec.query.all():
            db.session.delete(item)
        for item in UserItem.query.all():
            db.session.delete(item)
        db.session.commit()
        # 计算新的推荐
        data = record2table()
        icf = ICF()
        ucf = UCF()
        icf.get_dataset(data)
        ucf.get_dataset(data)
        icf.calc_cookbook_sim()
        ucf.calc_user_sim()
        # 将推荐表写入数据库
        icf.save()
        ucf.save()
        db.session.commit()

    # 推荐系统工作流程
    def recommend(self, user):
        N = 50
        rec_list = []
        TTL_rec = 60
        TTL_rej = 60
        # 0.检查redis中是否有推荐缓存
        user_str = 'recfor'+str(user)
        if self.cache.redis.llen(user_str) != 0:
            print("recommend from redis!")
            rid = int(self.cache.redis.lrange(user_str, 0, 0)[0])
            raw_list = self.cache.redis.lrange(user_str, 1, N)
            for item in raw_list:
                rec_list.append(bytes.decode(item))
            return {"rid": rid, "rec_list": rec_list}

        # 推荐系统流程
        print("need to calculate!")
        # 1. 推荐引擎+模型计算初始推荐列表
        ceid, raw_list = self.combine(user)
        # 2. 对初始列表过滤得到过滤后的列表
        filtered_list = self.filter.filter_item(user, raw_list)
        # 3. 对过滤后的列表进行排序
        rank_list = self.rank.rank(filtered_list)
        # 4. 反馈器记录这次推荐
        rid = self.fb.record(ceid)
        # 5. 生成推荐结果
        rec_list = [cid for (cid, score) in rank_list]
        # 6. 设置定时器
        timer = threading.Timer(TTL_rej, self.fb.not_match, args=[rid])
        timer.start()
        # 7. 将推荐结果缓存近Redis
        for item in rec_list:
            self.cache.redis.lpush(user_str, item)
        self.cache.redis.lpush(user_str, rid)
        self.cache.redis.expire(user_str, TTL_rec)
        return {"rid": rid, "rec_list": rec_list}
