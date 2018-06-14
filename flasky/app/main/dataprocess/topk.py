from ...models import Visit, Like
from operator import itemgetter
from app.main.recommend.cache import Cache
import time


# 得到热门
def get_topk(k):
    # 先访问Redis
    cache = Cache()
    if cache.redis.exists("ranking"):
        return [(bytes.decode(item[0]), item[1]) \
                for item in cache.redis.zrevrange("ranking", 0, 10, withscores=True)][:k]
    score_dict = {}

    # 喜欢加五分(考虑时间的影响，小时为单位)
    for item in Like.query.all():
        cid = item.cid
        dt = item.datetime
        score_dict.setdefault(cid, 0)
        score_dict[cid] += 5*int(time.mktime(dt.timetuple())/3600)

    # 浏览加次数分(考虑时间的影响，小时为单位)
    for item in Visit.query.all():
        cid = item.cid
        times = item.times
        rc = item.recent
        score_dict.setdefault(cid, 0)
        score_dict[cid] += times*int(time.mktime(rc.timetuple())/3600)

    top_list = sorted(score_dict.items(), key=itemgetter(1), reverse=True)

    # 更新Redis
    for item in top_list:
        cache.redis.zadd("ranking", item[0], item[1])

    return top_list[:k]