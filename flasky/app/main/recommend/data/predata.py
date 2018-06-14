import random
from .record2table import record2table
from .... import db
from ....models import Like


# 用于加载数据（使用单例模式）
class Predata(object):

    _instance = None

    def __init__(self):
        self.trainSet = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # 装载数据库数据
    def load_data(self):
        self.trainSet = record2table()

    # 将数据装载
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)

    # 将外部数据导入
    def usefile(self, filename):
        like_list = []
        db.create_all()
        for line in self.load_file(filename):
            user, cookbook, rating, timestamp = line.split(',')
            like_list.append(Like(uid=user, cid=cookbook))
        db.session.add_all(like_list)
        db.session.commit()
