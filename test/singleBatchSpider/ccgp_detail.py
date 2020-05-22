# coding:utf8
from spider.spiders import SingleBatchSpider, Request, Response
from spider.utils import log
from dateutil import parser
from bs4 import BeautifulSoup
import spider.utils.tools as tools
logger = log.get_logger(__file__)

try:
    from . import setting
except:
    import setting
# 详情页解析
class ccpg_detail_Spider(SingleBatchSpider):
    def __init__(self, **kwargs):
        super(ccpg_detail_Spider, self).__init__(**kwargs)
        self.task_key = "task:ccgp:detail"  # 需修改
        self.task_table_name = "ccgp_list"
        self.task_data_table = "ccgp_detail"
        self.task_field_list = ["id","url","title","ctime"]
        self.batch_interval = 7
        self.task_tag_name = "ccgp_detail"
        self.message_recipients = ["WXT"]
        self.debug = False
        self.pool_size = 1 if self.debug else 100
        self.downloader.proxy_enable = not self.debug

    def add_task(self):
        pass

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
            task_obj={"id":1,"url":"http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/t20200519_1240407.html"}
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
                data={}
                data['url']=_response.url
                data['title']=soup.select_one('span[style="font-size: 20px;font-weight: bold"]').text
                data['ctime']=parser.parse(soup.select_one("span.datetime").text).strftime("%Y-%m-%d %H:%M:%S")
                data["gtime"] = tools.get_current_date()
                data['content']=soup.select_one('div[style="width: 1105px;margin:0 auto"]').decode()
                print(data)

                if not self.debug:
                    self.store_data([data], table_name=self.task_data_table,oss=False)
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
    with ccpg_detail_Spider(**kwargs) as my_spider:
        # my_spider.add_task()
        my_spider.run()

# 重复问题