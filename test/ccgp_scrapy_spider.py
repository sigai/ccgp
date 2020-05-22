# coding:utf8
"""
最简爬虫代码示例
"""

# 导入依赖
from spider.spiders import Spider, Request
from spider.db import DB
import spider.utils.tools as tools
from dateutil import parser
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from scrapy.selector import Selector
# 编写自己的爬虫 名字根据项目需求而定
class MySpider(Spider):
    def __init__(self, **kwargs):
        super(MySpider, self).__init__(**kwargs)

        # 代理开关  默认使用代理
        self.downloader.proxy_enable = False

    def start_requests(self):
        """入口函数"""
        for i in range(1,2):
            url="http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html"
            yield Request(url)

    def parse(self, response):
        # 获取请求体
        request = response.request
        print(request)
        # 获取原生requests模块的Response
        _response = response.response
        # _response.encoding = "utf8"
        s=Selector(response=_response)
        list=s.xpath(".//li")
        for item in list:
            data = {}
            data["url"]=urljoin(_response.url,item.xpath(".//a/@href").extract_first())
            data["title"]=item.xpath(".//a/text()").extract_first()
            yield Request({"url": data['url']}, callback=self.detail_content, meta={"data": data})
        # 下一页
        next_url=urljoin(_response.url,s.xpath(".//a[contains(text(),'下一页')]/@href").extract_first())
        if next_url:
            yield Request({"url": next_url}, callback=self.parse)

    # 详情页
    def detail_content(self, response):
        request = response.request
        data = request.meta["data"]
        _response = response.response
        s = Selector(response=_response)
        data["content"]= s.xpath('.//div[@style="width: 1105px;margin:0 auto"]').extract_first()
        ctime=s.xpath('.//span[@class="datetime"]/text()').extract_first()
        data["ctime"]=parser.parse(ctime).strftime("%Y-%m-%d %H:%M:%S")
        data["gtime"] = tools.get_current_date()
        if data:
            # self.store_data(data, table_name="test", mysql=True, )
            print("mysql入库成功")
        print(data)
        yield data

# 启动
if __name__ == "__main__":
    # 实例化爬虫对象
    # 建立数据库本地连接
    db_uri = "mysql://root:111111@localhost:3306/test"
    conndb = DB().create(db_uri)
    kwargs = {"conndb":conndb}  # 此处可传递参数参考其他文档
    with MySpider(**kwargs) as my_spider:
        my_spider.run()
