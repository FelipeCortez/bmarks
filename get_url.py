from timeit import default_timer as timer
import urllib.request
import re

def get_title(url):
    start = timer()
    with urllib.request.urlopen(url) as f:
        t1 = timer()
        print("request", t1 - start)
        contents = f.read().decode('UTF-8', 'backslashreplace')
        t2 = timer()
        print("read", t2 - t1)
        pattern=re.compile(r"<title.*?>(.+?)</title>")
        return re.findall(pattern, contents)[0]

urls=["https://felipecortez.net",
      "https://facebook.com",
      "http://reddit.com",
      "http://google.com"]

for page in urls:
    print(get_title(page))

