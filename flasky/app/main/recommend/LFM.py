import random
import math
from operator import itemgetter
from app import db
from app.models import Pmat, Qmat, LFMRec


class LFM:
    def __init__(self, **kwargs):
        # 储存参数
        self.F = 5
        self.N = 100
        self.alpha = 0.3
        self.lamda = 0.03
        self.ratio = 1
        self.rec = 20
        if 'F' in kwargs:
            self.F = kwargs['F']
        if 'N' in kwargs:
            self.N = kwargs['N']
        if 'alpha' in kwargs:
            self.alpha = kwargs['alpha']
        if 'lamda' in kwargs:
            self.lamda = kwargs['lamda']
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        if 'rec' in kwargs:
            self.rec = kwargs['rec']

        self.dataset = None
        self.users = None
        self.items = None
        self.pmat = None
        self.qmat = None

    # 装载数据
    def get_dataset(self, data):
        self.dataset = data
        self.users = list(data.keys())
        itemset = set()
        for (uid, items) in data.items():
            itemset = itemset | set(items.keys())
        self.items = list(itemset)

    # p,q矩阵的初始化(将矩阵里的值随机的赋为0或1，私有)
    def _initpara(self, users, items, F):
        p = dict()
        q = dict()
        # 将参数值随机赋为0~1
        for userid in users:
            p[userid] = [(0 + 1 * random.random()) for f in range(0, F)]
        for itemid in items:
            q[itemid] = [(0 + 1 * random.random()) for f in range(0, F)]
        return p, q

    # 得到用于计算LFM的矩阵(私有)
    def _initsamples(self, user_items, ratio):
        user_samples = []
        # 物品池：用于生成负样本
        items_pool = []

        for (userid, items) in user_items.items():
            for item in items:
                items_pool.append(item)
        # print(items_pool)

        for (userid, items) in user_items.items():
            samples = dict()
            for (itemid, score) in items.items():
                if score > 0:
                    # 忽视用户的偏爱
                    samples[itemid] = 1
                    # 考虑用户的偏爱
                    # samples[itemid] = score

            # 随机生成负样本(考虑项目热门程度)
            # 说明：不利用屏蔽的原因是保持接口的一致性
            for i in range(0, len(items) * ratio * 3):
                # n：采样次数
                n = 0
                itemid = items_pool[random.randint(0, len(items_pool) - 1)]
                # 如果已经产生行为,继续下一轮
                if itemid in samples:
                    continue
                samples[itemid] = 0
                n += 1
                # 达到比值
                if n >= len(items)*ratio:
                    break
            user_samples.append((userid, samples))
        return user_samples

    # 初始化模型(初始化参数+初始化矩阵)
    def _initmodel(self, user_items, users, items, F, ratio):
        p, q = self._initpara(users, items, F)
        user_samples = self._initsamples(user_items, ratio)
        return p, q, user_samples

    # 预测某个用户对某个物品的喜欢程度
    def predict(self, userid, itemid, p, q):
        pre = sum(p[userid][f] * q[itemid][f] for f in range(0, len(p[userid])))
        return pre

    # 预测某个用户对各个物品的喜欢程度
    def predict_list(self, userid, items, p, q):
        predict_score = dict()
        for itemid in items:
            p_score = self.predict(userid, itemid, p, q)
            predict_score[itemid] = p_score
        return predict_score

    # LFM：隐语义模型
    def lfm(self):
        '''
        LFM计算参数 p,q
        :param user_items: 用户-物品矩阵
        :param users: 用户
        :param items: 物品
        :param F: 隐类因子个数
        :param N: 迭代次数
        :param alpha: 步长
        :param lamda: 正则化参数
        :return: p矩阵,q矩阵
        '''
        user_items = self.dataset
        users = self.users
        items = self.items
        F = self.F
        N = self.N
        alpha = self.alpha
        lamda = self.lamda
        ratio = self.ratio
        p, q, user_samples = self._initmodel(user_items, users, items, F, ratio)

        # 随机梯度下降
        for step in range(0, N):
            random.shuffle(user_samples)  # 乱序
            error = 0
            count = 0
            for userid, samples in user_samples:
                for itemid, rui in samples.items():
                    pui = self.predict(userid, itemid, p, q)
                    eui = rui - pui
                    count += 1
                    error += math.pow(eui, 2)
                    # 更新参数
                    for f in range(0, F):
                        p_u = p[userid][f]
                        q_i = q[itemid][f]
                        p[userid][f] += alpha * (eui * q_i - lamda * p_u)
                        q[itemid][f] += alpha * (eui * p_u - lamda * q_i)

            # 计算平方误差
            if count == 0:
                rmse = 0
            else:
                rmse = math.sqrt(error / count)
            # 学习率递减
            alpha *= 0.9
            # print("episode %d rmse: %.6f" % (step+1,rmse))

        self.pmat = p
        self.qmat = q
        return p, q

    # 存储数据到数据库(得到两个表：Pmat,Qmat)
    def save(self):
        db.create_all()
        # 存储P矩阵
        uf_list = []
        for (user, flist) in self.pmat:
            for i in range(len(flist)):
                uf_list.append(Pmat(uid=user, fid=i, score=flist[i]))
        db.session.add_all(uf_list)
        print("LFM: Pmat OK")
        # 存储Q矩阵
        cf_list = []
        for (item, flist) in self.qmat:
            for i in range(len(flist)):
                cf_list.append(Qmat(cid=item, fid=i, score=flist[i]))
        db.session.add_all(cf_list)
        print("LFM: Qmat OK")
        # 存储用户推荐
        rec_list = []
        for user in self.users:
            pre_dict = self.predict_list(user, self.items, self.pmat, self.qmat)
            # 去除已经产生行为的数据
            for item in self.dataset[user]:
                pre_dict.pop(item)
            # 找出评分最高的XX个物品
            for (item, score) in sorted(pre_dict.items(), key=itemgetter(1), reverse=True)[:self.rec]:
                rec_list.append(LFMRec(uid=user, cid=item, score=score))
        db.session.add_all(rec_list)
        print("LFM: LFMRec OK")
        db.session.commit()

    # 更新数据
    def refresh(self, data):
        # 清空之前数据
        db.create_all()
        for item in Qmat.query.all():
            db.session.delete(item)
        for item in Pmat.query.all():
            db.session.delete(item)
        db.session.commit()
        # 计算新的推荐
        self.get_dataset(data)
        self.lfm()
        self.save()
