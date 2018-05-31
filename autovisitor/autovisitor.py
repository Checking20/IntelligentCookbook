#!coding:utf-8
import requests,json,random,time

class visitor:
    def __init__(self,ip,apis,uids,cids):
        self.ip = ip
        self.apis = apis
        self.uids = uids
        self.cids = cids

    def visit(self):
         api = random.sample(self.apis,1)[0]
         uid = random.sample(self.uids,1)[0]
         cid = random.sample(self.cids,1)[0]
         url = 'http://'+ip+'/'+api+'/'+uid+'/'+cid
         print(url)
         requests.get(url)



if __name__ == '__main__':
    items = None
    with open('data7.json','r') as json_file:
        items = json.load(json_file)
    ip = "118.25.4.52"
    apis = ['like','visit']
    uids = ['chenming','sheqijin','lipengze','zhangqian','jiaofangkai','wangjingxin']
    cids = [item['id'] for item in items][:100]
    v = visitor(ip,apis,uids,cids)
    for i in range(100):
        v.visit()

