import random
import math


# 计算概率(softmax)
def softmax(weight_dict):
    t = 0.1
    q_dict = {}
    sum = 0
    for (eid, weight) in weight_dict.items():
        sum += math.exp(weight/t)
    for (eid, weight) in weight_dict.items():
        q_dict[eid] = math.exp(weight/t)/sum
    return q_dict


# 根据概率选择引擎
def random_choose(q_dict):
    r = random.random()
    cur = 0
    qlist = [(eid, weight) for (eid, weight) in q_dict.items()]
    for (eid, weight) in qlist:
        if cur <= r < (cur+weight):
            return eid
        cur += weight
    return qlist[-1]


