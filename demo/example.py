# import sys
import json
from tumblpy import Tumblpy

cfg = {
    "alt_sizes": -3,
    "preview_size":-4,
    "dashboard_param": {
        "limit": 20,
        "offset": 0,
        "since_id": 162863435409
    },
    "posts_param": {
        "limit": 20,
        "offset": 0
    },
    "proxies": {
        "http": "127.0.0.1:50175",
        "https": "127.0.0.1:50175"
    },
    "since_id": 26588344
}
# 162826769394
# 162826780134_250
# 162824270739_250
with open('tumblr_credentials.json', 'r') as f:
    tumblr_key = json.load(f)

t = Tumblpy(
    tumblr_key['consumer_key'],
    tumblr_key['consumer_secret'],
    tumblr_key['oauth_token'],
    tumblr_key['oauth_token_secret'],
    proxies=cfg['proxies']
)


dashboard = t.dashboard( cfg['dashboard_param'] )
print('Here are some posts this blog has made:', json.dumps(dashboard, indent=4))

data = []
distId = []
for v in dashboard["posts"]:
    distId.append(v['id'])
    data.append(
        {
            'id': v['id'],
            'source_url' : v.get('source_url', ''),
            'original_size' : v['photos'][0]['original_size']['url'],
            'alt_sizes' : v['photos'][0]['alt_sizes'][cfg['alt_sizes']]['url']
        }
    )
distId.sort()
# -2为接着图片序列， 原因不明  -3为重复上一次最后一张图片
cfg['dashboard_param']['since_id'] = distId[-2]
# print(distId)
# with open('data.json', 'w') as f:
#     json.dump(cfg, f)
# print('Here are some posts this blog has made:', json.dumps(data, indent=4))

# blog_url = t.post('user/info')
# blog_url = blog_url['user']['blogs'][0]['url']

# print('Your blog url is: {}'.format(blog_url))

# posts = t.posts(blog_url)

# print('Here are some posts this blog has made:', json.dumps(posts, indent=4))

# print t.post('post', blog_url=blog_url, params={'type':'text', 'title': 'Test', 'body': 'Lorem ipsum.'})