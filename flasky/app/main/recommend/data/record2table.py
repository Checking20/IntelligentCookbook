from ....models import Like, Visit


# 将数据库记录转换成user-item矩阵
def record2table():
    score_dict = {}
    # 喜欢加五分
    for item in Like.query.all():
        score_dict.setdefault(item.uid, {})
        score_dict[item.uid].setdefault(item.cid, 0)
        score_dict[item.uid][item.cid] += 5

    # 浏览加次数*1分
    for item in Visit.query.all():
        score_dict.setdefault(item.uid, {})
        score_dict[item.uid].setdefault(item.cid, 0)
        score_dict[item.uid][item.cid] += item.times

    return score_dict
