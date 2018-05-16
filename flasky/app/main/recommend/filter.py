from ...models import Item


# 过滤产品(用户选择)
class Filter:
    def __init__(self):
        self.threshold = 0.5

    # 对推荐物品进行过滤(文档质量)
    def filter_item(self, raw_dict):
        print("Filtering")
        '''
        rec_dict = {}
        for cid in raw_dict:
            item = Item.query.filter_by(cid=cid).first()
            if item.quality < self.threshold:
                continue
            rec_dict[cid] = raw_dict[cid]
        
        return rec_dict
        '''
        return raw_dict

