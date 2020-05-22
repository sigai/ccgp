# coding:utf8
"""
http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html
"""
from spider.spiders import BatchSpider, Request, Response
from spider.utils import log ,tools
from lxml import etree
from urllib.parse import urljoin
from dateutil import parser
from bs4 import BeautifulSoup
logger = log.get_logger(__file__)

try:
    from . import setting
except:
    import setting

class ccpg_list_Spider(BatchSpider):
    def __init__(self, **kwargs):
        super(ccpg_list_Spider, self).__init__(**kwargs)
        self.task_key = "task:ccgp1:list"  # 需修改
        self.task_table_name = "ccgp1_task"
        self.task_data_table = "ccgp1_list"
        self.task_batch_table_name = "ccgp1_list_batch_record"
        self.task_field_list = ["id","url"]
        self.task_tag_name = "ccgp1_list"
        self.message_recipients = ["WXT"]
        self.pool_size = 1 if self.debug else 100
        self.downloader.proxy_enable = not self.debug
        try:
            self.local_batch_data = self.batch_date
        except:
            self.local_batch_data = "1970-01-01"
        # 批次间隔
        self.batch_interval = 1
        self.batch_interval_unit = "hour" # day, hour


    # 存任务到任务表中
    def add_task(self):
        for page in range(0,10):
            if page==0:
                url = "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index.html"
            else:
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
                    data['gtime']=tools.get_current_date()
                    data['ctime']=parser.parse(item.select_one("span").text).strftime("%Y-%m-%d %H:%M:%S")
                    data["batch_date"] = self.local_batch_data
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
        print("在这里啦")
        my_spider.check_batch()
        print("我经过这里啦")
        my_spider.run()

