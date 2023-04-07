import requests
import re
import os

OPEN_CACHE = True

def download_deb(url, name, package=None, output=None, arch=None):
    def download(url, output):
        if OPEN_CACHE and os.path.exists(output):
            return
        with open(output, "wb") as f:
            f.write(requests.get(url).content)

    if package is None:
        package = name

    if arch is None:
        arch = ["amd64"]

    if output is None:
        output = os.path.join(os.getcwd(), "deb")
        if not os.path.exists(output):
            os.mkdir(output)
        output = os.path.join(output, package)
        if not os.path.exists(output):
            os.mkdir(output)

    ret = requests.get(url)
    data = ret.content
    code = ret.status_code
    if code == 404:
        print("[-]", name, ", 找不到")
    match = re.findall(r'<tr><td class="link"><a href="(.+\.deb)" title="', data.decode())
    for _ in match:
        if _.split("_")[2].split(".")[0] not in arch: # arch过滤
            continue

        if "-dev" in _ or "-dbg" in _ or "-doc" in _: # 过滤dev包(源码), dbg包(调试符号包)
            continue

        if re.match(name + "[0-9]*", _.split("_")[0]) is None or len(_.split("_")[0].split('-')) > 1:
            continue

        download(url + "/" + _, os.path.join(output, _))

def get_checkers():
    def get_deb_url(n):
        base = "https://mirrors.tuna.tsinghua.edu.cn/debian/pool/main/"
        if n.startswith("lib"):
            url = base + n[:4] + "/" + n
        else:
            url = base + n[:1] + "/" + n
        return url

    l = os.listdir("./checkers")
    for _ in l:
        if _.startswith("_"):
            continue
        if _ == "README.md":
            continue
        if _.startswith("thunder"):
            continue
        n = _.split(".")[0]
        url = get_deb_url(n)
        download_deb(url, n)


def main():
    global OPEN_CACHE
    OPEN_CACHE = True # 本地若是有同名文件，则不下载，加快进度
    download_deb("https://mirrors.tuna.tsinghua.edu.cn/debian/pool/main/libx/libxml2/", "libxml2")

if __name__ == "__main__":
    main()