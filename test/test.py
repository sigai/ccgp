"""
1.单批次主要是为了用那个任务表，保证任务的不丢失，还有任务状态；有取任务的逻辑,没有批次记录表
2.批次比单批次多了个 取任务的逻辑 和 检查批次的逻辑check_batch
批次，需要任务表，用来存每次的任务
批次记录表
数据表
3.get_task 取数据，先看redis里有没有，没有在从数据库批量取出，存redis中，在从redis中取
get_task_from_mysql 查出任务状态为0,更新任务状态为2,因为多线程,表示这条任务已经被别人拿走了,最后放redis中
get_task_from_redis


4.check_batch 检查批次(1检查上一次批次是否都完成2下一批次该不该开始)
先运行一下,就不会报batch_data失败的问题了,
4.1检查上一次批次进度
(在record_batch_count方法中,查任务表中state=1的个数与总数比较,同时更新批次表,保留最后的创建时间)
4.2确认是否都完成
没完成-->就会一直运行该批次,该批次完成后,到时间后,才会进入下一批次进入下一批次,
完成-->检查本批次是否到达开始时间,
            -->未到达时间直接返回,
            -->到达时间会 ,重置redis批次时间,重置mysql的state为0,插入新批次到表中

check_batch会生成batch_data会存到mysql和redis中


问题1:由于已有爬虫停止 故终止当前爬虫
问题2:重复
cookie_pool
file_download_service 文件下载服务
datalog数据日志
self.event_exit = threading.Event()
"""
# coding:utf8
"""
http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html
"""
from spider.spiders import Spider, Request, Response
from spider.utils import log, tools
from lxml import etree
from urllib.parse import urljoin
from dateutil import parser
from bs4 import BeautifulSoup

logger = log.get_logger(__file__)

try:
    from . import setting
except:
    import setting
from spider.network import proxy
from spider.network import downloader
from spider.utils import tools

url='http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/index_1.html'
dl=downloader.Downloader()
re=dl.download(url)
get_c=tools.get_cookies(re)
print(get_c)

