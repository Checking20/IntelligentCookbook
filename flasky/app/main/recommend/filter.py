from ...models import Item, Dislike


# 过滤产品(用户选择)
class Filter:
    def __init__(self):
        # 过滤阈值
        self.threshold = 0.5

    # 过滤菜谱
    def filter_item(self, uid, raw_list):
        print("Filtering")
        filtered_dict = {}
        for item in raw_list:
            filtered_dict[item[0]] = item[1]
        # 过滤不喜欢列表
        for item in Dislike.query.filter_by(uid=uid).all():
            if filtered_dict.get(item.cid) is not None:
                print("filter %s for %s" % (item.cid, uid))
                filtered_dict.pop(item.cid)

        return list(filtered_dict.items())

