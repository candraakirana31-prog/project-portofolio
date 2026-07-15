import urllib.request
import traceback

try:
    r = urllib.request.urlopen('http://127.0.0.1:5000', timeout=10)
    data = r.read()
    print('STATUS', r.getcode())
    print(data.decode('utf-8')[:2000])
except Exception:
    traceback.print_exc()
