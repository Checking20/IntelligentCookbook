from ...models import Visit, Like, Dislike
from ... import db
import datetime
from app.main.recommend.cache import Cache


# 记录喜欢
def record_like(uid, cid):
    # Redis部分
    # 关系表部分
    if len(Like.query.filter_by(uid=uid, cid=cid).all()) == 0:
        time = datetime.datetime.now()
        db.session.add(Like(uid=uid, cid=cid))
        db.session.commit()
        return True
    return False


# 记录屏蔽（添加）
def record_dislike(uid, cid):
    # Redis部分
    # 关系表部分
    if len(Dislike.query.filter_by(uid=uid, cid=cid).all()) == 0:
        db.session.add(Dislike(uid=uid, cid=cid))
        db.session.commit()
        return True
    return False


# 记录访问(修改,添加)
def record_visit(uid, cid):
    # Redis部分
    # 关系表部分
    visit = Visit.query.filter_by(uid=uid, cid=cid).first()
    if visit is None:
        visit = Visit(uid=uid, cid=cid, times=1)
    else:
        visit.times = visit.times+1
    db.session.add(visit)
    db.session.commit()
    return True


# 查询喜欢
def query_like(uid):
    # 优先访问Redis
    # 如果没有则访问关系表
    like_list = [item.cid for item in Like.query.filter_by(uid=uid).all()]
    return like_list


# 取消喜欢
def cancel_like(uid, cid):
    # Redis部分
    # 关系表部分
    like = Like.query.filter_by(uid=uid,cid=cid).first()
    if not (like is None):
        db.session.delete(like)
        db.session.commit()
        return True
    return False


# 取消屏蔽
def cancel_dislike(uid, cid):
    # Redis部分
    # 关系表部分
    dislike = Dislike.query.filter_by(uid=uid, cid=cid).first()
    if not (dislike is None):
        db.session.delete(dislike)
        db.session.commit()
        return True
    return False


