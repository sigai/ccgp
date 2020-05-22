# coding:utf8
import requests
from spider import setting
from spider.network import proxy


if 1:
    url="https://laedc.org/research-analysis/search-reports/download-category/economic-impact-studies/"
    # 简单用法 代理池对象
    proxy_source_url = setting.get_proxy_uri(setting.proxy_name_default)
    proxy_pool = proxy.ProxyPool(proxy_source_url=proxy_source_url)
    proxies = proxy_pool.get()
    print(proxies)
    resp = requests.get(url, proxies=proxies)
    print(resp.text)
    print(resp.status_code)

# 自定义解析
# if 1:
#     proxy_source_url = setting.get_proxy_uri(setting.proxy_name_default)
#     proxy_list = requests.get(proxy_source_url).text.split()
#     proxy_list = [x.strip() for x in proxy_list if x.strip()]
#     print(proxy_list)
    # 处理成自己需要的格式
