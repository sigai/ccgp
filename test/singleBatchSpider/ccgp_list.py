# coding:utf8
"""
http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html
"""
from spider.spiders import SingleBatchSpider, Request, Response
from spider.utils import log
from lxml import etree
from urllib.parse import urljoin
import requests
from lxml.html import fromstring
from dateutil import parser
from bs4 import BeautifulSoup
logger = log.get_logger(__file__)

try:
    from . import setting
except:
    import setting

class ccpg_list_Spider(SingleBatchSpider):
    def __init__(self, **kwargs):
        super(ccpg_list_Spider, self).__init__(**kwargs)
        self.task_key = "task:ccgp:list"  # 需修改
        self.task_table_name = "ccgp_task"
        self.task_data_table = "ccgp_list"
        self.task_field_list = ["id","url"]
        self.batch_interval = 7
        self.task_tag_name = "ccgp_list"
        self.message_recipients = ["WXT"]
        self.debug = False
        self.pool_size = 1 if self.debug else 100
        self.downloader.proxy_enable = not self.debug
    # 存任务到任务表中
    def add_task(self):
        for page in range(1,2):
            url=f"http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_{page}.html"
            task_obj={
                "url":url
            }
            self.db.add(task_obj,table_name=self.task_table_name)
            print("添加列表到任务表")

    # 除了任务表的字段,可携带一些其他的信息,比如headers
    def get_requests(self,task_obj):
        requestData={
            "url":task_obj.get("url")
        }
        if self.debug:
            proxies = {
            }
            requestData["proxies"] = proxies
        return requestData

    def start_requests(self):
        if self.debug:
            task_obj={"id":1,"url":"http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html"}
            requestData=self.get_requests(task_obj)
            yield Request(requestData,meta={"task":task_obj},callback=self.parse())
        while 1:
            task_obj = self.get_task(obj=True)
            if not task_obj:
                logger.debug("没有任务")
                break
            url = task_obj.url
            # 下载
            yield Request({"url": url}, meta={"task": task_obj}, callback=self.parse)
        return

    def parse(self, response: Response):
        request = response.request
        task_obj = request.meta["task"]
        url=task_obj.get("url")
        _response = response.response
        try:
            if _response:
                # todo 解析代码
                soup = BeautifulSoup(_response.text, "html.parser")
                rows = soup.select('ul.xinxi_ul li')
                dataList=[]
                for item in rows:
                    data={}
                    data['url']=urljoin(_response.url, item.select_one("a").attrs["href"])
                    data['title']=item.select_one("a").text
                    data['ctime']=parser.parse(item.select_one("span").text).strftime("%Y-%m-%d %H:%M:%S")
                    dataList.append(data)
                    print(data)
                if len(dataList) > 0:
                    if not self.debug:
                        self.store_data(dataList, table_name=self.task_data_table,oss=False)
                        print("数据表存储成功")
                if not self.debug:
                    # 更新完成标志
                    self.set_task_state(setting.TASK_FINISH, condition={"url":url})
                logger.debug("任务完成 {}".format(task_obj))

            else:
                if _response is not None:
                    if _response.status_code == 404:
                        url = _response.url
                        # todo 解析代码
                        # 更新完成标志
                        self.set_task_state(state=-1, condition={"url": url})
                        return
                raise Exception
        except Exception as e:
            logger.exception(e)
            self.put_task(task_obj)
        return

if __name__ == "__main__":
    kwargs={}
    with ccpg_list_Spider(**kwargs) as my_spider:
        # my_spider.add_task()
        my_spider.run()

# 重复问题