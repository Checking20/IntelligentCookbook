
# 协同过滤推荐算法（itemCF）实现

import math
from operator import itemgetter
from ...models import ItemSim, ICFRec, UserItem
from ... import db


# 基于Item的协同过滤算法
class ItemBasedCF:
    # 初始化参数
    def __init__(self):
        # 找到相似的20个菜谱，为目标用户推荐10个菜谱

        # K值：找到和已经看过菜谱最相似的20个菜谱
        self.n_sim_cookbook = 20
        # N值: 将其中前10名推荐给用户
        self.n_rec_cookbook = 50
        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}
        # 用户(用户名单)
        self.userset = set()

        # 用户相似度矩阵
        self.cookbook_sim_matrix = {}
        self.cookbook_popular = {}
        self.cookbook_count = 0

    # 读文件得到“用户-菜谱”数据(基于比例划分数据)
    def get_dataset(self, predata):
        self.trainSet = predata.trainSet
        self.testSet = predata.testSet

    # 计算菜谱之间的相似度
    def calc_cookbook_sim(self):
        for user, cookbooks in self.trainSet.items():
            for cookbook in cookbooks:
                if cookbook not in self.cookbook_popular:
                    self.cookbook_popular[cookbook] = 0
                self.cookbook_popular[cookbook] += 1

        self.cookbook_count = len(self.cookbook_popular)
        print("Total cookbook number = %d" % self.cookbook_count)

        for user, cookbooks in self.trainSet.items():
            self.userset.add(user)
            for m1 in cookbooks:
                for m2 in cookbooks:
                    if m1 == m2:
                        continue
                    self.cookbook_sim_matrix.setdefault(m1, {})
                    self.cookbook_sim_matrix[m1].setdefault(m2, 0)
                    # 朴素计数
                    weight = 1
                    # 根据用户活跃度进行加权(item-IUF)
                    # weight = 1/math.log2(1+len(cookbooks))
                    self.cookbook_sim_matrix[m1][m2] += weight
        print("Build co-rated users matrix success!")

        # 计算菜谱之间的相似性
        print("Calculating cookbook similarity matrix ...")
        for m1, related_cookbooks in self.cookbook_sim_matrix.items():
            mx = 0 # wix中最大的值
            for m2, count in related_cookbooks.items():
                # 注意0向量的处理，即某菜谱的用户数为0
                if self.cookbook_popular[m1] == 0 or self.cookbook_popular[m2] == 0:
                    self.cookbook_sim_matrix[m1][m2] = 0
                else:
                    # 余弦相似度
                    self.cookbook_sim_matrix[m1][m2] = count / math.sqrt(self.cookbook_popular[m1] * self.cookbook_popular[m2])
                # 更新最大值
                mx = max(self.cookbook_sim_matrix[m1][m2], mx)
            # 进行相似度归一化(Item-Norm)
            for m2, count in related_cookbooks.items():
                self.cookbook_sim_matrix[m1][m2] /= mx
        print('Calculate cookbook similarity matrix success!')

    # 针对目标用户U，对其看过的每部菜谱找到K部相似的菜谱，并推荐其N部菜谱
    def recommend(self, user):
        K = self.n_sim_cookbook
        N = self.n_rec_cookbook
        rank = {}

        watched_cookbooks = self.trainSet[user]
        for cookbook, rating in watched_cookbooks.items():
            # 得到与看过菜谱最相似的K个菜谱
            for related_cookbook, w in sorted(self.cookbook_sim_matrix[cookbook].items(), key=itemgetter(1), reverse=True)[:K]:
                # 去掉已经看过的菜谱
                if related_cookbook in watched_cookbooks:
                    continue
                rank.setdefault(related_cookbook, 0)
                # 排名的依据——>推荐菜谱与该已看菜谱的相似度(累计)*用户对已看菜谱的评分
                rank[related_cookbook] += w * float(rating)
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    # 为指定菜谱找出相似N
    def find_sim(self, cookbook):
        K = self.n_sim_cookbook
        sim_dict = {}
        for related_cookbook, w in sorted(self.cookbook_sim_matrix[cookbook].items(), key=itemgetter(1), reverse=True)[:K]:
            sim_dict[related_cookbook] = w
        return sim_dict

    # 存储数据到数据库(得到两个表：静态ICF：用户-推荐菜谱，动态ICF：菜谱-推荐菜谱)
    def save(self):
        db.create_all()
        # 存储用户-产品推荐表
        rec_list = []
        for user in self.userset:
            # print("recommend for %s", user)
            for (cid, score) in self.recommend(user):
                rec_list.append(ICFRec(uid=user, cid=cid, score=score))
        db.session.add_all(rec_list)
        print("ICF: user-item rec OK")

        # 遍历菜谱, 找出K相似
        sim_list = []
        # 存储产品相似度
        for cookbook in self.cookbook_sim_matrix.keys():
            for rcookbook, s in self.find_sim(cookbook=cookbook).items():
                sim_list.append(ItemSim(cid1=cookbook, cid2=rcookbook, sim=s))
        db.session.add_all(sim_list)
        print("ICF: item-item sim OK")

        weight_list = []
        # 存储用户-产品喜爱表
        for user, cookbooks in self.trainSet.items():
            for cookbook in cookbooks:
                weight_list.append(UserItem(uid=user, cid=cookbook, weight=float(self.trainSet[user][cookbook])))
        db.session.add_all(weight_list)
        print("ICF: user-item like OK")

        db.session.commit()
        print("ICF：Save complete")








