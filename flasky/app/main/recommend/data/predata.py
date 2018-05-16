import random
'''
    这个类主要用于划分数据集来对推荐结果进行测试
'''


# 用于划分数据集和测试结果（使用单例模式）
class Predata(object):

    _instance = None

    def __init__(self):
        datafile = 'C:/Users/SheCh/Desktop/My/本学期/实训/flasky/app/main/recommend/data/ratings.csv'
        self.divide_data(datafile)
        print('Dataset is created!')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    trainSet = {}
    testSet = {}
    trainset_len = 0
    testset_len = 0

    # 将数据装载
    def load_file(self,filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)

    # 将数据划分为训练集和测试集
    def divide_data(self, filename, pivot=0.50):
        for line in self.load_file(filename):
            user, cookbook, rating, timestamp = line.split(',')
            if (random.random() < pivot):
                self.trainSet.setdefault(user, {})
                self.trainSet[user][cookbook] = rating
                self.trainset_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][cookbook] = rating
                self.testset_len += 1

        print('Split success!')
        print('TrainSet = %s' % self.trainset_len)
        print('TestSet = %s' % self.testset_len)

