from .filter import Filter

'''
    RecEngine：基本的推荐引擎，提供recommend接口
'''
class RecEngine:
    @staticmethod
    def recommend(uid):
        pass

'''
    RecSys推荐系统：由若干推荐引擎何其权重，Filter过滤器，Rank排名器，ReasonAnalyzer解释器，和Feedback反馈器构成
'''
class RecSys():

    def __init__(self):
        self.engines = []
        self.filter = None
        self.rank = None
        self.ra = None

    # 推荐
    def recommend(self,user):
        pass

    def combine(self,user):
        rec_dict = {}
        for engine, w in self.engines:
            for (cid, score) in engine.recommend(user):
                rec_dict.setdefault(cid,0)
                rec_dict[cid] += w * score
        return rec_dict
