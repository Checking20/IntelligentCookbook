from ....models import Like, Visit

def record2table():
    score_dict = {}
    # 喜欢加五分
    for item in Like.query.all():
        score_dict.setdefault(item.uid, {})
        score_dict[item.uid].setdefault(item.cid, 0)
        score_dict[item.uid][item.cid] += 5

    # 浏览加次数分
    for item in Visit.query.all():
        score_dict.setdefault(item.uid, {})
        score_dict[item.uid].setdefault(item.cid, 0)
        score_dict[item.uid][item.cid] += item.times

    return score_dict
