from . import db


# 定义用户-产品喜爱表
class UserItem(db.Model):
    __tablename__ = 'useritem'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    weight = db.Column(db.Float)


# 定义产品相似度表(每日更新但立马反映)
class ItemSim(db.Model):
    __tablename__ = 'itemsims'
    cid1 = db.Column(db.String(64), primary_key=True)
    cid2 = db.Column(db.String(64), primary_key=True)
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<ItemSim %r %r>' % (self.cid1, self.cid2)


# 定义用户相似度表(每日)
class UserSim(db.Model):
    __tablename__ = 'usersims'
    uid1 = db.Column(db.String(64), primary_key=True)
    uid2 = db.Column(db.String(64), primary_key=True)
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<UserSim %r %r>' % (self.uid1, self.uid2)


# 定义用户-产品推荐表(ICF)
class ICFRec(db.Model):
    __tablename__ = 'icfr'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    score = db.Column(db.Float)

    def __repr__(self):
        return '<ICFRec %r %r>' % (self.uid, self.cid)


# 定义用户-产品推荐表(UCF)
class UCFRec(db.Model):
    __tablename__ = 'ucfr'
    uid = db.Column(db.String(64), primary_key=True)
    cid = db.Column(db.String(64), primary_key=True)
    score = db.Column(db.Float)

    def __repr__(self):
        return '<UCFRec %r %e>' % (self.uid, self.cid)



