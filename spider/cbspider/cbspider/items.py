# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# 定义抓取数据
class CbspiderItem(scrapy.Item):
    # 工艺
    gongyi = scrapy.Field()
    # 口味
    kouwei = scrapy.Field()
    # 难度
    nandu = scrapy.Field()
    # 准备时间
    zhunbeishijian = scrapy.Field()
    # 烹饪时间
    pengrenshijian = scrapy.Field()
    # 人数
    renshu = scrapy.Field()
    # 主料
    zhuliao = scrapy.Field()
    # 辅料
    fuliao = scrapy.Field()
