# coding:utf8

from spider.setting import *


default_redis_uri="redis://:root@127.0.0.1:6379/0"
default_mysql_uri ="mysql://root:111111@localhost:3306/test"
proxy_name_default=proxy_name_oversea

# 任务状态 2是正在运行中的意思
TASK_FINISH = 1
TASK_WAIT = 0
TASK_ERROR = -1
#  "task_run": 2,
