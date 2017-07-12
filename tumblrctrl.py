import json
import sciter
import requests
import os
from concurrent.futures import ProcessPoolExecutor as PPool
from concurrent.futures import ThreadPoolExecutor as TPool
from concurrent.futures import as_completed
from tumblpy import Tumblpy

htmlTemplate = '''
            <li#{0} style="background-image:url({1})" original="{2}" preview="{3}">
                <div.btn>
                    <button.download></button><button.magnifier></button>
                </div>
            </li>
        '''

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

def mkMainDict( d, param ):
    data = []
    for v in d["posts"]:
        t = {
            'link_url'        : gets(v, 'link_url', ''),
            'source_url'        : gets(v, 'source_url', '')
        }
        index = 1
        for i in v['photos']:
            t['id'] = str(v['id']) + '[' + str(index) + ']'
            t['original_size'] = gets(i, 'original_size.url', '')
            t['preview_size'] = gets(i, 'alt_sizes.' + str(param['preview_size']) + '.url', '')
            t['alt_sizes'] = gets(i, 'alt_sizes.' + str(param['alt_sizes']) + '.url', '')
            data.append(t.copy())
            index += 1
    return data
def getDashboards( tumblr, param ):
    # frame.call_function('aaa', 'yyy' )
    # return
    dashboard = tumblr.dashboard( param['dashboard_param'] )
    # if dashboard:
    #     self.cfg['dashboard_param']['offset'] += self.cfg['dashboard_param']['limit']
    return mkMainDict( dashboard, param )

class TumblrCtrl(object):
    """docstring for TumblrCtrl"""
    def __init__(self, frame):
        super(TumblrCtrl, self).__init__()
        self.frame = frame
        self.popup = None
        # self.imgView = self.frame.get_root().find_first('#ul')
        self.cfg = {"alt_sizes":-3,"dashboard_param":{"limit":20,"offset":0},"posts_param":{"limit":20,"offset":0},"proxies":{}}
        with open('data.json', 'r') as f:
            self.cfg.update( json.load(f) )
        with open('tumblr_credentials.json', 'r') as f:
            self.tumblr_key = json.load(f)
        self.proxies = self.cfg['proxies']
        # self.offset = self.cfg['dashboard_param']['limit']
        self.current_folder = os.getcwd()
        self.target_folder = os.path.join(self.current_folder, 'imgTemp')
        if not os.path.isdir(self.target_folder):
            os.mkdir(self.target_folder)
        self.download_folder = os.path.join(self.current_folder, 'download')
        if not os.path.isdir(self.download_folder):
            os.mkdir(self.download_folder)

        # 创建一个线程池
        self.tpool = TPool(max_workers=20)
        # 创建一个进程池
        self.ppool = PPool(max_workers=2)
        # self.queue = Queue.Queue()
        self.tumblr = Tumblpy(
                self.tumblr_key['consumer_key'],
                self.tumblr_key['consumer_secret'],
                self.tumblr_key['oauth_token'],
                self.tumblr_key['oauth_token_secret'],
                proxies=self.proxies
            )

    def myOnLoadDatas(self, uri):
        self.tpool.submit(self._downloadInRAM, "photo", uri )
        return True
    def loadPreviewImg( self, data ):

        fileName = data['id'] + '_' + data['preview_size'].split("_")[-1]
        print(fileName)
        # return
        file_path = os.path.join( self.target_folder, fileName )
        if not os.path.isfile(file_path):
            self.tpool.submit(self._downloadPrev, "photo", data, file_path )
        else:
            self.popup.set_style_attribute( "background-image", "url("+file_path +")" )
            self.popup.set_attribute("imgid", data['id'])
            self.popup.set_attribute("original", data['original'])
        pass
    def loadImgList( self ):
        '''获取图片列表
            {
                "id": 0,
                "source_url": "",
                "original_size": "https://*_1280.jpg",
                "alt_sizes": "https://*_100.jpg"
            }
        '''
        print('获取图片列表')
        future_tasks = [self.ppool.submit( getDashboards, self.tumblr, self.cfg )]
        for f in future_tasks:
            if f.running():
                print('is running')
        for f in as_completed(future_tasks):
            try:
                if f.done():
                    self.cfg['dashboard_param']['offset'] += self.cfg['dashboard_param']['limit']
                    for x in f.result():
                        fileName = x['id'] + '_' + x['alt_sizes'].split("_")[-1]
                        # print(fileName)
                        file_path = os.path.join( self.target_folder, fileName )
                        if not os.path.isfile(file_path):
                            self.tpool.submit(self._download, "photo", x, file_path )
                        else:
                            html = htmlTemplate.format( x['id'], file_path, x['original_size'], x['preview_size'] )
                            self.frame.call_function('appendImgList', html )
            except Exception as e:
                f.cancel()
        return
                # li = sciter.Element.create("li")
                # li.set_attribute("id", x['id'])
                # # li.set_attribute("data-src", file_path)
                # ul.append(li)
                # li.set_style_attribute( "background-image", file_path )

    def _getTumblrList(self):
        print('_getTumblrList')
        return self.getDashboard()
        # return self.getBloggers()
    def _downloadPrev(self, medium_type, data, file_path ):
        if medium_type == "photo":
            print('_download photo')
            req = requests.get( data['preview_size'], proxies=self.proxies )
            with open(file_path, 'wb') as fh:
                for chunk in req.iter_content(chunk_size=1024):
                    fh.write(chunk)
            self.popup.set_style_attribute( "background-image", "url("+file_path +")" )
            self.popup.set_attribute("imgid", data['id'])
            self.popup.set_attribute("original", data['original'])
            # html = htmlTemplate.format( x['id'], file_path, x['original_size'], x['preview_size'] )
            # self.frame.call_function('appendImgList', html )
        return
    def downloadOriginal(self, id, url):
        fileName = id + '_' + url.split("_")[-1]
        file_path = os.path.join( self.download_folder, fileName )
        if not os.path.isfile(file_path):
            self.tpool.submit(self._downloadOriginal, url, file_path )

    def _downloadOriginal(self, url, file_path):
        req = requests.get( url, proxies=self.proxies )
        with open(file_path, 'wb') as fh:
            for chunk in req.iter_content(chunk_size=1024):
                fh.write(chunk)

    def _download(self, medium_type, x, file_path ):
        if medium_type == "photo":
            print('_download photo')
            req = requests.get( x['alt_sizes'], proxies=self.proxies )
            with open(file_path, 'wb') as fh:
                for chunk in req.iter_content(chunk_size=1024):
                    fh.write(chunk)
            html = htmlTemplate.format( x['id'], file_path, x['original_size'], x['preview_size'] )
            self.frame.call_function('appendImgList', html )
            # li = sciter.Element.create("li")
            # li.set_attribute("id", id)
            # # li.set_attribute("data-src", file_path)
            # ul.append(li)
            # li.set_style_attribute( "background-image", file_path )
        return
    def _downloadInRAM( self, medium_type, uri ):
        print("_downloadInRAM", uri)
        try:
            if medium_type == "photo":
                req = requests.get( uri, proxies=self.proxies )
                self.frame.data_ready( uri, req.content )
        except Exception as e:
            raise e

    def _mkMainDict(self, d):
        data = []
        for v in d["posts"]:
            data.append({
                'id'              : gets(v, 'id', 0),
                'link_url'        : gets(v, 'link_url', ''),
                'original_size'  : gets(v, 'photos.0.original_size.url', ''),
                'preview_size'  : gets(v, 'photos.0.alt_sizes.' + str(self.cfg['preview_size']) + '.url', ''),
                'alt_sizes'      : gets(v, 'photos.0.alt_sizes.' + str(self.cfg['alt_sizes']) + '.url', '')
            })
        return data
    def getDashboard(self):
        dashboard = self.tumblr.dashboard( self.cfg['dashboard_param'] )
        if dashboard:
            self.cfg['dashboard_param']['offset'] += self.cfg['dashboard_param']['limit']
        return self._mkMainDict( dashboard )
    def getBloggers(self):
        '''取得博主的列表'''
        all_posts = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, self.cfg['posts_param'])
        if all_posts:
            self.cfg['posts_param']['offset'] += self.cfg['posts_param']['limit']
        return self._mkMainDict( all_posts )