"""Minimalistic PySciter sample for Windows."""

import sciter
import ctypes
# import json
# import requests
# import logging


from tumblrctrl import TumblrCtrl

ctypes.windll.user32.SetProcessDPIAware(2)

# logging.basicConfig(filename='log1.log',
#                     format='%(message)s',
#                     datefmt='%Y-%m-%d',
#                     level=logging.DEBUG)

class Frame(sciter.Window):

    def __init__(self):
        super().__init__(ismain=True, uni_theme=False, debug=False)
        self.set_dispatch_options(enable=True, require_attribute=False)
        self.tumblrCtrl = TumblrCtrl( self )
        # self.ul = None
        # print('gg',self.tumblrCtrl.proxies)
        pass

    def on_load_dataww(self,ld):
        """Custom documents loader, just for example."""
        # print(self)
        # uri = ld.uri
        # uri = uri
        # print(ld.uri)
        if ld.uri.startswith('http'):
            # print('web')
            # url = '''http://68.media.tumblr.com/469c21ccd53ec48c4f7caee21c3ca0a7/tumblr_orhs5iSD0b1qla6e4o1_100.jpg'''
            # url = ld.uri[7:]
            # id = ld.requestId
            # print(ld.requestId)

            # return self.tumblrCtrl.scheduling( self, ld.uri.lstrip('tumblr:'), ld.requestId )
            return self.tumblrCtrl.myOnLoadDatas( ld.uri )
            # req = requests.get( url, proxies={"http": "127.0.0.1:50175", "https": "127.0.0.1:50175"} )
            # req = requests.get( url, proxies={"http": "127.0.0.1:61274", "https": "127.0.0.1:61274"} )
            # self.data_ready( uri, req.content )
        return False

    def log(self, p ):
        print(p)
        pass
    def downloadOriginal(self, id, url):
        id = str( id ).strip('"')
        url = str( url ).strip('"')
        return self.tumblrCtrl.downloadOriginal(id, url)

    def loadPreviewImg( self, id, original, preview ):
        print("loadPreviewImg")
        data = {
            'id' : str( id ).strip('"'),
            'original' : str( original ).strip('"'),
            'preview_size' : str( preview ).strip('"')
        }
        return self.tumblrCtrl.loadPreviewImg( data )

    def loadImgList(self):
        print("do")
        # self.ul = self.ul or frame.get_root().find_first('#ul')
        # root = frame.get_root()
        # ul = root.find_first('#ul')
        # return self.tumblrCtrl.loadImgList( self.tumblrCtrl, ul )
        return self.tumblrCtrl.loadImgList()

        imgDict = self.tumblrCtrl.loadImgList( self.ul )
        for x in imgDict:
            # html += li.format(x['alt_sizes'])
            # print(x['alt_sizes'])
            li = sciter.Element.create("li")
            li.set_attribute("data-src", x['alt_sizes'])
            self.ul.append(li)

        return

if __name__ == '__main__':
    import sys

    # import base64
    frame = Frame()
    # frame = sciter.Window(ismain=True, uni_theme=True)
    frame.load_file("gui/main.html")
    frame.tumblrCtrl.popup = frame.get_root().find_first('.popup-view')
    # print('gg',frame.tumblrCtrl.proxies)
    # url='https://68.media.tumblr.com/469c21ccd53ec48c4f7caee21c3ca0a7/tumblr_orhs5iSD0b1qla6e4o1_100.jpg'
    # req = requests.get(url)
    # imgurl = 'url(data:image/jpeg;base64,'
    # imgurl += repr(base64.b64encode(req.content).decode('ascii')).strip('\'') + ')'

    # root = frame.get_root()
    # ul = root.find_first('#ul>li')

    # li = '''<li style="background-image: url({0})"></li>'''

    # html = li.format(site)
    # root.call_function('gFunc', li)
    # ul.set_style_attribute( "background-image", imgurl )

    frame.run_app()
