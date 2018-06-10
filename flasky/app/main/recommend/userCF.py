# 协同过滤推荐算法（itemCF）实现

import math
from operator import itemgetter
from ...models import UCFRec
from ... import db


class UserBasedCF:
    # 初始化相关参数
    def __init__(self, **kwargs):
        # K值：最相似的10个用户
        self.n_sim_user = 10
        if 'k_user' in kwargs:
            self.n_sim_user = kwargs['k_user']
        # N值：推荐(缓存)20个菜谱
        self.n_rec_cookbook = 20
        if 'rec' in kwargs:
            self.n_rec_cookbook = kwargs['rec']
        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        # 用户相似度矩阵
        self.user_sim_matrix = {}
        self.cookbook_count = 0

    # 读文件得到“用户-电影”数据
    def get_dataset(self, data):
        self.trainSet = data

    # 计算用户之间的相似度
    def calc_user_sim(self):
        # 构建“电影-用户”倒排索引
        # key = cookbookID, value = list of userIDs who have seen this cookbook
        print('Building cookbook-user table ...')
        cookbook_user = {}
        for user, cookbooks in self.trainSet.items():
            for cookbook in cookbooks:
                if cookbook not in cookbook_user:
                    cookbook_user[cookbook] = set()
                cookbook_user[cookbook].add(user)
        print('Build cookbook-user table success!')
        self.cookbook_count = len(cookbook_user)
        print('Total cookbook number = %d' % self.cookbook_count)

        print('Build user co-rated cookbooks matrix ...')
        for cookbook, users in cookbook_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    weight = 1
                    # 根据热门程度加权
                    # weight = 1/math.log2(1+len(users))
                    self.user_sim_matrix[u][v] += weight
        print('Build user co-rated cookbooks matrix success!')
        # 计算相似性
        print('Calculating user similarity matrix ...')
        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                # 余弦相似度公式
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))
                # Jaccard公式
                # self.user_sim_matrix[u][v] = count / (len(self.trainSet[u]) + len(self.trainSet[v])-count)
        print('Calculate user similarity matrix success!')

    # 针对目标用户U，找到其最相似的K个用户，产生N个推荐
    def recommend(self, user):
        # 和用户相似的前K个用户
        K = self.n_sim_user
        N = self.n_rec_cookbook
        rank = {}
        watched_cookbooks = self.trainSet[user]

        # v=similar user, wuv=similar factor
        for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0:K]:
            for cookbook in self.trainSet[v]:
                if cookbook in watched_cookbooks:
                    continue
                rank.setdefault(cookbook, 0)
                # 统计K个人里有多少个人观看
                rank[cookbook] += wuv
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    # 存储数据到数据库
    def save(self):
        db.create_all()
        rec_list = []
        # 存储用户-产品推荐表(UCF)
        for user, cookbooks in self.trainSet.items():
            for (cid, score) in self.recommend(user):
                rec_list.append(UCFRec(uid=user, cid=cid, score=score))
        db.session.add_all(rec_list)
        print("UCF: user-item rec OK")
        db.session.commit()
        print("UCF: Save complete")

    # 更新数据
    def refresh(self, data):
        db.create_all()
        # 清空之前数据
        for item in UCFRec.query.all():
            db.session.delete(item)
        db.session.commit()
        # 计算新的推荐
        self.get_dataset(data)
        self.calc_user_sim()
        self.save()







