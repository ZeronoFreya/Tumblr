# import sys
import json
from tumblpy import Tumblpy

with open('data.json', 'r') as f:
    cfg = json.load(f)

with open('tumblr_credentials.json', 'r') as f:
    tumblr_key = json.load(f)

t = Tumblpy(
    tumblr_key['consumer_key'],
    tumblr_key['consumer_secret'],
    tumblr_key['oauth_token'],
    tumblr_key['oauth_token_secret'],
    proxies=cfg['proxies']
)
cfg = {
    "alt_sizes": -3,
    "dashboard_param": {
        "limit": 5,
        "since_id": 26588344
    },
    "posts_param": {
        "limit": 5,
        "since_id": 26588344
    },
    "proxies": {
        "http": "127.0.0.1:61274",
        "https": "127.0.0.1:61274"
    }
}
all_posts = t.posts('kuvshinov-ilya.tumblr.com', None, cfg['posts_param'])
# dashboard = t.dashboard( cfg['dashboard_param'] )
# print('Here are some posts this blog has made:', json.dumps(all_posts, indent=4))
data = []
distId = []
for v in all_posts["posts"]:
    distId.append(v['id'])
    data.append(
        {
            'id': v['id'],
            'source_url' : v.get('source_url', ''),
            'original_size' : v['photos'][0]['original_size']['url'],
            'alt_sizes' : v['photos'][0]['alt_sizes'][cfg['alt_sizes']]['url']
        }
    )
# distId.sort()
# -2为接着图片序列， 原因不明  -3为重复上一次最后一张图片
# cfg['posts_param']['offset'] = distId[-2]
print(distId)
# with open('data.json', 'w') as f:
#     json.dump(cfg, f)
print('Here are some posts this blog has made:', json.dumps(data, indent=4))
