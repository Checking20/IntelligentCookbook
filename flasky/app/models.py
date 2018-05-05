from . import db


# 定义产品相似度表
class ItemSim(db.Model):
    __tablename__ = 'itemsims'
    cid1 = db.Column(db.String(64), primary_key=True)
    cid2 = db.Column(db.String(64))
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<ItemSim %r>' % self.cid


# 定义用户相似度表
class UserSim(db.Model):
    __tablename__ = 'usersims'
    uid1 = db.Column(db.String(64), primary_key=True)
    uid2 = db.Column(db.String(64))
    sim = db.Column(db.Float)

    def __repr__(self):
        return '<UserSim %r>' % self.uid
