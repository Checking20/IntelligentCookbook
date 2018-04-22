import scrapy
import queue
from cbspider.items import CbspiderItem
import re
'''
    时间：2018/4/21
    作者：Output20
    说明：本爬虫用于爬取美食杰网站
'''

# 爬虫
class MeishiSpider2(scrapy.Spider):
    name = "meishi2"
    # allowed_domains=["http://www.meishij.net"]

    # 主题页面队列
    kinds_list = []
    # 更新主题列表
    kinds_set = set()
    # 已经爬取过的页面（详细页面）
    crawled_urls = set()
    # 记录最大主题数最大爬取页面数目
    MAXTHEME = 10
    MAXPAGES = 10

    # 爬取主题页面方式
    def start_requests(self):
        # 读文件
        with open('urls', 'r')as lines:
            for line in lines:
                self.kinds_list.append(line[:-1])
                self.kinds_set.add(line[:-1])

        # 列表长度和主题数取小
        for i in range(min(self.MAXTHEME, len(self.kinds_list))):
            # 从队列中获取主题
            kind = self.kinds_list[i]
            # 将主题设置为爬取
            for i in range(self.MAXPAGES):
                # 爬取主题页面
                yield self.make_requests_from_url(kind + "?&page=%d" % (i + 1))

    # 首页爬取方法：抽取详细页面的链接
    def parse(self,response):
        # 获取详细页面
        hrefs = response.xpath("//div[@class='listtyle1']/a")
        for href in hrefs:
            url = href.xpath("@href")[0].extract()
            # 如果url未被爬取过
            if url not in self.crawled_urls:
                # 解析详细页面
                yield scrapy.Request(url, callback=self.parse_detail_page)

    # 具体页面爬取方法：人工定位各个信息的位置
    def parse_detail_page(self, response):
        # 第一部分:选择抓取结构(人工定义)
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
        # 获取描述
        dish['miaoshu'] = response.xpath("//div[@class='materials']/p/text()").extract()[0]
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

        # 第二部分：其他处理
        # 将网页url加入crawled_pages
        self.crawled_urls.add(response.url)
        # 爬取页面数目加一
        # 获取新的主题链接
        zhutis = response.xpath("//ul[@class='pathstlye1']//a[@class='curzt']")
        for href in zhutis:
            h = href.xpath("@href")[0].extract()
            if h not in self.kinds_set:
                self.kinds_set.add(h)
                with open('urls','a')as lines:
                    lines.write(h+'\n')
        # return dish
