from ...models import Visit, Like
from operator import itemgetter
import math


# 计算推荐排名
class Ranker:
    def __init__(self):
        pass

    def rank(self, raw_list):
        print("Ranking")
        rate_dict = {}

        # 喜欢加五分
        for item in Like.query.all():
            cid = item.cid
            rate_dict.setdefault(cid, 0)
            rate_dict[cid] += 5

        # 浏览加次数分
        for item in Visit.query.all():
            cid = item.cid
            times = item.times
            rate_dict.setdefault(cid, 0)
            rate_dict[cid] += times

        # 按热门程度降权
        rank_list = []
        for (cid, score) in raw_list:
            rate = rate_dict.get(cid)
            if rate is None:
                rate = 0
            rank_list.append((cid, score/(1+math.log2(1+rate))))
        return sorted(rank_list, key=itemgetter(1), reverse=True)


