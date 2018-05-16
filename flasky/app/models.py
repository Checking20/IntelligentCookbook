from . import db
import datetime


class Visit(db.Model):
    __tablename__ = 'visit'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    # 最近一次访问时间
    recent = db.Column(db.DateTime, default=datetime.datetime.now)
    # 访问次数
    times = db.Column(db.Integer)


# 用户喜好表
class Like(db.Model):

    __tablename__ = 'like'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return '<like %r %r>' % (self.uid, self.cid)


# 用户屏蔽表
class Dislike(db.Model):
    __tablename__ = 'dislike'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)

    def __repr__(self):
        return '<like %r %r>' % (self.uid, self.cid)


# 产品信息表
class Item(db.Model):
    __tablename__ = 'item'
    cid = db.Column(db.String(64), primary_key=True)
    popularty = db.Column(db.Float)
    quality = db.Column(db.Float)

    def __repr__(self):
        return '<item %r>' % self.cid


# 用户-产品喜爱表
class UserItem(db.Model):
    __tablename__ = 'useritem'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    weight = db.Column(db.Float)

    def __repr__(self):
        return '<UserItem %r %r>' % (self.uid, self.cid)


# 产品相似度表(每日更新但立马反映)
class ItemSim(db.Model):
    __tablename__ = 'itemsims'
    cid1 = db.Column(db.String(64), primary_key=True)
    cid2 = db.Column(db.String(64), primary_key=True)
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<ItemSim %r %r>' % (self.cid1, self.cid2)


# 用户相似度表(每日)
class UserSim(db.Model):
    __tablename__ = 'usersims'
    uid1 = db.Column(db.String(64), primary_key=True)
    uid2 = db.Column(db.String(64), primary_key=True)
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<UserSim %r %r>' % (self.uid1, self.uid2)


# 用户-产品推荐表(ICF)
class ICFRec(db.Model):
    __tablename__ = 'icfr'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    score = db.Column(db.Float)

    def __repr__(self):
        return '<ICFRec %r %r>' % (self.uid, self.cid)


# 用户-产品推荐表(UCF)
class UCFRec(db.Model):
    __tablename__ = 'ucfr'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    score = db.Column(db.Float)

    def __repr__(self):
        return '<UCFRec %r %e>' % (self.uid, self.cid)



