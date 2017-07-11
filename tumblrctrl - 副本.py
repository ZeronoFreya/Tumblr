import json
import sciter
import requests
import os
# from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import ThreadPoolExecutor as Pool
from tumblpy import Tumblpy

def gets( t, s, d=None ):
    if not t: return d
    for k in s.split('.'):
        if type(t) == list and k.lstrip('-').isdigit():
            l = k = int(k)
            if k < 0: l = abs(k) - 1
            if len(t) > l: t = t[k]; continue
        elif type(t) == dict and k in t:
            t = t[k]; continue
        else:
            return d
    return t

class TumblrCtrl(object):
    """docstring for TumblrCtrl"""
    def __init__(self):
        super(TumblrCtrl, self).__init__()
        self.cfg = {"alt_sizes": -2, "dashboard_param": {"limit": 20, "since_id": 0}, "proxies": {}}
        with open('data.json', 'r') as f:
            self.cfg.update( json.load(f) )
        with open('tumblr_credentials.json', 'r') as f:
            self.tumblr_key = json.load(f)
        self.proxies = self.cfg['proxies']
        self.offset = self.cfg['posts_param']['limit']

        # 创建一个线程池
        self.pool = Pool(max_workers=20)
        # self.queue = Queue.Queue()
        self.tumblr = Tumblpy(
                self.tumblr_key['consumer_key'],
                self.tumblr_key['consumer_secret'],
                self.tumblr_key['oauth_token'],
                self.tumblr_key['oauth_token_secret'],
                proxies=self.proxies
            )

    def loadImgList( self, ul ):
        '''获取图片列表
            {
                "id": 0,
                "source_url": "",
                "original_size": "https://*_1280.jpg",
                "alt_sizes": "https://*_100.jpg"
            }
        '''
        print('获取图片列表')
        f = self.pool.submit(self.download, "list", {'ul':ul} )
        return

    def myOnLoadDatas(self, el, uri, requestId):
        f = self.pool.submit(self.download, "photo", { 'el' : el, 'uri' : uri, 'requestId' : requestId } )
        # print(f.done())
        # print(f.result())
        return True

    def download( self, medium_type, ld ):
        print("download")
        try:
            if medium_type == "list":
                imgDict = self.getDashboard()
                # imgDict = self.getBloggers()
                # html = ''
                # li = '''<li data-src='{0}'></li>'''
                for x in imgDict:
                    # html += li.format(x['alt_sizes'])
                    # print(x['alt_sizes'])
                    li = sciter.Element.create("li")
                    li.set_attribute("data-src", x['alt_sizes'])
                    ld['ul'].append(li)
                # return html
                return
            elif medium_type == "photo":
                # print(ld['uri'], self.proxies)
                req = requests.get( ld['uri'], proxies=self.proxies )
                # print("1",ld['requestId'],ld['uri'])
                ld['el'].data_ready( ld['uri'], req.content, ld['requestId'] )
                # ld['el'].data_ready( ld['uri'], req.content )
        except Exception as e:
            print('err2', e)

    # def downloadImg(self, url):
    #     name = url.split("/")[-1].split("?")[0]
    #     file_path = os.path.join('R:\imgTemp', name)
    #     print(file_path)
    #     if not os.path.isfile(file_path):
    #         retry_times = 0
    #         while retry_times < 5:
    #             try:
    #                 resp = requests.get(url,
    #                                     stream=True,
    #                                     proxies=self.cfg['proxies'],
    #                                     timeout=10)
    #                 with open(file_path, 'wb') as fh:
    #                     for chunk in resp.iter_content(chunk_size=1024):
    #                         fh.write(chunk)
    #                 break
    #             except:
    #                 pass
    #             retry_times += 1
    #     return file_path



    # def onLoadDatas( self, el, ld ):
    #     uri = ld.uri
    #     print(uri)
    #     req = requests.get( uri, proxies=self.cfg['proxies'] )
    #     el.data_ready( uri, req.content, ld.requestId )
    #     return False
    def _mkMainDict(self, d):
        data = []
        for v in d["posts"]:
            data.append({
                'id'              : gets(v, 'id', 0),
                'source_url'     : gets(v, 'source_url', ''),
                'original_size'  : gets(v, 'photos.0.original_size.url', ''),
                'alt_sizes'      : gets(v, 'photos.0.alt_sizes.' + str(self.cfg['alt_sizes']) + '.url', '')
            })
        return data
    def getDashboard(self):


        dashboard = self.tumblr.dashboard( self.cfg['dashboard_param'] )
        self.cfg['dashboard_param']['offset'] += self.offset
        return self._mkMainDict( dashboard )
    def getBloggers(self):
        '''取得博主的列表'''
        all_posts = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, self.cfg['posts_param'])
        self.cfg['posts_param']['offset'] += self.offset
        return self._mkMainDict( all_posts )