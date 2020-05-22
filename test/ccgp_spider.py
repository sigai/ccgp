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
import re
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
        _response = response.response
        soup = BeautifulSoup(_response.text, "html.parser")
        list=soup.select('ul.xinxi_ul li')
        for item in list:
            data = {}
            data["url"]=urljoin(_response.url,item.select_one("a").attrs["href"])
            data["title"]=item.select_one("a").text
            yield Request({"url": data['url']}, callback=self.detail_content, meta={"data": data})
        # 下一页
        next_url=urljoin(_response.url,soup.find("a",text=re.compile("下一页")).attrs["href"])
        print(next_url)
        if next_url:
            yield Request({"url": next_url}, callback=self.parse)

    # 详情页
    def detail_content(self, response):
        request = response.request
        data = request.meta["data"]
        _response = response.response
        soup=BeautifulSoup(_response.text,"html.parser")
        data["content"]= soup.select_one('div[style="width: 1105px;margin:0 auto"]').decode()
        ctime=soup.select_one('span.datetime').text
        data["ctime"]=parser.parse(ctime).strftime("%Y-%m-%d %H:%M:%S")
        data["gtime"] = tools.get_current_date()
        if data:
            self.store_data(data, table_name="test", mysql=True,oss=False )
            print("mysql入库成功")
        print(data)
        yield data


# 启动
if __name__ == "__main__":
    # 实例化爬虫对象
    # 建立数据库本地连接
    kwargs = {}  # 此处可传递参数参考其他文档
    with MySpider(**kwargs) as my_spider:
        my_spider.run()
