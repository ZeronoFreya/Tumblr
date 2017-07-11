from tumblrctrl import TumblrCtrl
import json
t = TumblrCtrl()
d = t.getDashboard()
print(json.dumps(d, indent=4))
