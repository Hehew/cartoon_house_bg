from django.shortcuts import render, HttpResponse
import json
from pyquery import PyQuery as pq
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import re
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
#
# chrome_options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
#
# chrome_options.add_argument('window-size=1920x3000') #指定浏览器分辨率
# chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
# chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
# chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
# chrome_options.add_argument('--headless')
# brower = webdriver.Chrome(chrome_options=chrome_options)
phantomargs = ['--load-images=false']
brower = webdriver.PhantomJS(service_args=phantomargs)
brower.set_window_size(1120, 550)
wait = WebDriverWait(brower,10)

# Create your views here.
def index(request):
    try:
        # /bg/current_week/
        response = requests.get('http://www.u17.com/')
        url = request.path
        if response.status_code == 200:
            if url == '/bg/current_week/':
                res = current_week_cartoon_parse(response.text)
            elif url == '/bg/only_me/':
                res = only_me_parse(response.text)
            elif url == '/bg/hot_list/':
                res = hot_list_parse(response.text)
            return HttpResponse(json.dumps(res), content_type="application/json")
        else:
            return HttpResponse('连接超时请检查你的网络!')
    except Exception:
        return HttpResponse('连接超时请检查你的网络!')

def get_info(request):
    try:
        url = request.GET.get('detail_url')
        response = requests.get(url)
        if response.status_code == 200:
            res = get_info_parse(response.text)
            return HttpResponse(json.dumps(res), content_type="application/json")
        else:
            return HttpResponse('连接超时请检查你的网络!')
    except Exception:
        return HttpResponse('连接超时请检查你的网络!')

def search_for_keyword(request):
    try:
        keyword = request.GET.get('keyword').encode('utf-8').decode()
        response = requests.get('http://so.u17.com/all/' + keyword + '/m0_p1.html')
        if response.status_code == 200:
            res = get_search_parse(response.text)
            return HttpResponse(json.dumps(res), content_type="application/json")
        else:
            return HttpResponse('连接超时请检查你的网络!')
    except Exception:
        return HttpResponse('连接超时请检查你的网络!')

# def get_page_detail(request):
#     try:
#         id = request.GET.get('id')
#         response = requests.get('http://www.u17.com/chapter_vip/' + id + '.shtml')
#         print('http://www.u17.com/chapter_vip/' + id + '.shtml')
#         if response.status_code == 200:
#             res = get_page_detail_parse(response.text)
#             print(response.text)
#             return HttpResponse(json.dumps(res), content_type="application/json")
#         else:
#             return HttpResponse('连接超时请检查你的网络!')
#     except Exception:
#         return HttpResponse('连接超时请检查你的网络!')

def get_page_detail(request):
    try:
        id = request.GET.get('id')
        brower.get('http://www.u17.com/chapter_vip/' + id + '.shtml')
        res = get_page_detail_parse()

        return HttpResponse(json.dumps(res), content_type="application/json")
    except Exception:
        return HttpResponse('连接超时请检查你的网络!')

def current_week_cartoon_parse(text):
    doc = pq(text)
    items = doc('.comic_list_ts .cut1 .comic_all>li').items()
    res = []
    for item in items:
        item = {
            'detail_url': item.find('.comic_pic').attr('href'),
            'imageSrc': item.find('.comic_pic>img').attr('xsrc'),
            'title': item.find('.comic_tit').text(),
            'label': item.find('.comic_type').text()
        }
        res.append(item)
    return res

def only_me_parse(text):
    doc = pq(text)
    items = doc('.comic_list_qy .cut1 .comic_all>li').items()
    res = []
    for item in items:
        item = {
            'detail_url': item.find('.comic_pic').attr('href'),
            'imageSrc': item.find('.comic_pic>img').attr('xsrc'),
            'title': item.find('.comic_tit').text(),
            'label': item.find('.comic_type').text()
        }
        res.append(item)
    return res

def get_search_parse(text):
    doc = pq(text)
    items = doc('.comiclist>ul>li').items()
    res = []
    for item in items:
        item = {
            'detail_url': item.find('.cover>a').attr('href'),
            'imageSrc': item.find('.cover img').attr('src'),
            'title': item.find('.info .u').attr('title'),
            'label': item.find('.info .cf .fl').text().replace(' ','')
        }
        res.append(item)
    return res
def hot_list_parse(text):
    doc = pq(text)
    items = doc('.hot_comic_list>li').items()
    res = []
    for item in items:
        item = {
            'detail_url': item.find('.hot_comic_img').attr('href'),
            'imageSrc': item.find('.hot_comic_img img').attr('xsrc'),
            'title': item.find('.hot_comic_tit').text()
        }
        res.append(item)
    return res

def get_info_parse(text):
    doc = pq(text)
    items = doc('#chapter>li').items()
    res = []

    for item in items:
        item = {
            'detail_url': item.find('a').attr('href'),
            'title': item.find('a').text().strip(),
            'image_num': re.search('(\(.*?\))',item.text().strip()).group(1),
            'page_id': item.find('a').attr('id').split('_')[1]
        }
        res.append(item)
    return res

# def get_page_detail_parse(text):
#     doc = pq(text)
#     items = doc('.mg_auto').items()
#     res = []
#     for item in items:
#         item = item.find('img.cur_pic.lazyload').attr('xsrc')
#         res.append(item)
#     return res

def get_page_detail_parse():
    html = brower.page_source
    doc = pq(html)
    res = []
    items = doc('.mg_auto').items()
    for item in items:
        item = item.find('img.cur_pic.lazyload').attr('xsrc')
        res.append(item)
    return res