# coding:utf8
"""
海外代理实例:
https://laedc.org/research-analysis/search-reports/download-category/economic-impact-studies/?dlpage=2
"""

# 导入依赖
from spider.spiders import Spider, Request

from bs4 import BeautifulSoup
from spider.network import proxy
try:
    from . import setting
except:
    import setting

# 编写自己的爬虫 名字根据项目需求而定
class MySpider(Spider):
    def __init__(self, **kwargs):
        super(MySpider, self).__init__(**kwargs)
        # 代理开关  默认使用代理
        self.downloader.proxy_enable = False
        # 使用海外代理
        self.downloader.proxy_pool=proxy.oversea_proxy_pool
        self.proxies=self.downloader.proxy_pool.get()
        # self.proxy_source_url = setting.get_proxy_uri(setting.proxy_name_default)

    # def get_requests(self,url):
    #     re_data={
    #         "url":url
    #     }
    #     proxy_pool = proxy.ProxyPool(proxy_source_url=self.proxy_source_url)
    #     proxies = proxy_pool.get()
    #     re_data["proxies"]=proxies
    #     return re_data

    def start_requests(self):
        """入口函数"""
        for i in range(0,1):
            url="https://laedc.org/research-analysis/search-reports/download-category/economic-impact-studies/"
            print(self.proxies)
            yield Request({"url":url,"proxies":self.proxies})

    def parse(self, response):
        _response = response.response
        print(_response.status_code)
        soup = BeautifulSoup(_response.text, "html.parser")
        rows=soup.select('.dlm-downloads li')
        for item in rows:
            data={}
            data['url']=item.select_one('a').attrs['href']
            data['title']=item.select_one('a').text
            print(self.proxies)
            yield Request({"url":data['url'],"proxies":self.proxies},callback=self.detail_content,meta={'data':data})
        # 下一页
        next_url="https://laedc.org"+soup.select_one(".next").attrs["href"]
        if next_url:
            print(next_url)
            print(self.proxies)
            yield Request({"url":next_url,"proxies":self.proxies}, callback=self.parse)

        return
 # 详情页
    def detail_content(self, response):
        request = response.request
        data = request.meta["data"]
        _response = response.response
        soup=BeautifulSoup(_response.text,"html.parser")
        data['content']=soup.select_one('#download-page').decode()
        print(data)
        if data:
            self.store_data(data, table_name="laedc", mysql=True,oss=False )
            print("mysql入库成功")
        print(data)
        yield data

# 启动
if __name__ == "__main__":
    # 实例化爬虫对象
    kwargs = {}  # 此处可传递参数参考其他文档
    with MySpider(**kwargs) as my_spider:
        my_spider.run()