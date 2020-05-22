# coding:utf8
"""
单批次:主要时取任务的逻辑,
第一步:建列表任务表,任务状态state要默认为0
CREATE TABLE `ccgp_task` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(200) NOT NULL DEFAULT '' ,
  `state` int(11) NOT NULL DEFAULT '0' ',
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`) USING BTREE ,
  KEY `state` (`state`) USING BTREE'
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;
建列表页的数据表,state要默认为0,便于详情页取任务标记为1
CREATE TABLE `ccgp_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `url` text,
  `ctime` datetime DEFAULT NULL,
  `state` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1807 DEFAULT CHARSET=utf8mb4;
建详情页数据表
CREATE TABLE `ccgp_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `url` text,
  `ctime` datetime DEFAULT NULL,
  `gtime` datetime DEFAULT NULL,
  `content` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1807 DEFAULT CHARSET=utf8mb4;
第二步:把列表页的第一页到最后一页的链接add_task到任务表ccgp_task中,start_requests入口函数取任务
(它会先从redis中取数据,没有数据的话,就从mysql数据库中取,取出来的数据存入redis中,再从redis中取)
parse函数解析页面,存入ccgp_list数据表中,把任务表中state变为1,表示这条任务完成了
第三步:列表页存储解析完成了,要解析ccgp_list中存储的详情页,ccgp_list作为任务表,取任务,解析存储到
ccgp_detail中,任务表state为1
"""
default_redis_uri="redis://:root@127.0.0.1:6379/0"
default_mysql_uri ="mysql://root:111111@localhost:3306/test"
# 任务状态 2是正在运行中的意思
TASK_FINISH = 1
TASK_WAIT = 0
TASK_ERROR = -1
#  "task_run": 2,


