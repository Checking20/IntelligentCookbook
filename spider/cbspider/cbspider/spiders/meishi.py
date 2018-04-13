import scrapy
from cbspider.items import CbspiderItem
import re
import os
import sqlite3
'''
    时间：2018/4/2
    作者：Output20
    说明：本爬虫用于爬取美食杰网站
'''

# 爬虫
class MeishiSpider(scrapy.Spider):
    name = "meishi"
    # allowed_domains=["http://www.meishij.net"]
    # 起始url
    start_urls = [
        # 首页："http://www.meishij.net/chufang/diy/wucan/?&page=1"
        # 生成多页(这里设置为10页)：
        "http://www.meishij.net/chufang/diy/wucan/?&page=%d"%(i+1) for i in range(55)
    ]
    '''
    ---暂时未用到的数据库部分---
    # 存储数据,使用SQLite3
    database_file = os.path.dirname(os.path.abspath(__file__)) + "\\meishi.db"
    # 如果有_删除原先数据库
    if os.path.exists(database_file):
        os.remove(database_file)
    # 连接数据库
    database = sqlite3.connect(database_file)
    '''

    # 首页爬取方法：抽取详细页面的链接
    def parse(self,response):
        # 获取详细页面
        hrefs = response.xpath("//div[@class='listtyle1']/a")
        for href in hrefs:
            # 抽取详细页面连接
            url = href.xpath("@href")[0].extract()
            # print(url)
            # 解析详细页面
            yield scrapy.Request(url, callback=self.parse_detail_page)

    # 具体页面爬取方法：人工定位各个信息的位置
    def parse_detail_page(self, response):
        # 选择抓取结构
        dish = CbspiderItem()
        # 获取id
        pattern = re.compile(r'zuofa\/.*')
        dish['id'] = pattern.findall(response.url)[0][6:-5]
        # 获取菜名
        dish['caiming'] = response.xpath("//h1/a/text()").extract()[0]
        info2 = response.xpath("//div[@class='info2']")
        # 获取成品图(链接)
        dish['chengpin'] = response.xpath("//div[@class='cp_headerimg_w']/img/@src")[0].extract()
        # 获取标签
        dish['biaoqian'] = response.xpath("//dl[@class='yj_tags clearfix']//a/text()").extract()
        # 获取工艺
        dish['gongyi'] = (info2.xpath("//li[@class='w127']/a").xpath("text()").extract()+[''])[0]
        # 获取口味
        dish['kouwei'] = (info2.xpath("//li[@class='w127 bb0']/a").xpath("text()").extract()+[''])[0]
        # 获取难度
        dish['nandu'] = (info2.xpath("//li[@class='w270']//a").xpath("text()").extract()+[''])[0]
        # 获取人数
        dish['renshu'] = (info2.xpath("//li[@class='w270 br0']//a").xpath("text()").extract()+[''])[0]
        # 获取准备时间
        dish['zhunbeishijian'] = (info2.xpath("//li[@class='w270 bb0']//a").xpath("text()").extract()+[''])[0]
        # 获取烹饪时间
        dish['pengrenshijian'] = (info2.xpath("//li[@class='w270 bb0 br0']//a").xpath("text()").extract()+[''])[0]
        # 获取主料
        dish['zhuliao'] = dict()
        for h4 in response.xpath("//div[@class='yl zl clearfix']//h4"):
            dish['zhuliao'][h4.xpath("a/text()").extract()[0]] = h4.xpath("span/text()").extract()[0]
        # 获取辅料
        dish['fuliao'] = dict()
        for li in response.xpath("//div[@class='yl fuliao clearfix']//li"):
            dish['fuliao'][li.xpath("h4/a/text()").extract()[0]] = li.xpath("span/text()").extract()[0]
        # 获取过程（文本+链接）
        count = 0
        dish['guocheng'] = dict()
        for div in response.xpath("//div[@class='editnew edit']/div/div"):
            count += 1
            dish['guocheng'][count] = (div.xpath("p/text()")[0].extract(),div.xpath("p/img/@src")[0].extract())
        # 获取主题
        dish['zhuti'] = response.xpath("//ul[@class='pathstlye1']//a[@class='curzt']/text()").extract()
        # 获取技巧
        dish['jiqiao'] = response.xpath("//div[@class='editnew edit']/p[@style]/text()").extract()
        return dish
