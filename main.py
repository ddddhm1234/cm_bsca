import generate
import checker
import json
import os

CACHE = True

c = checker.Checker()
c.load_sign("lib.json")
# print(c.signs["busybox"]["contains"])

if CACHE and os.path.exists("lib.json") and os.path.isfile("lib.json"):
    pass
else:
    g = generate.GenerateSign()
    g.load_desc("/home/chengrui/Project/Python/sca/extract/desc.json", path="/media/chengrui/Extern/lib_dataset/file")
    signs = g.generate(2)
    f = open("lib.json", "w")
    json.dump(signs, f)
    f.close()

OPEN = True
if not OPEN:
    exit(0)

c = checker.Checker()
c.load_sign("lib.json")
result = c.scan_path(
    "/home/chengrui/Documents/WeChat Files/wxid_1w93femnnmqm22/FileStorage/MsgAttach/659d319948c255cbdbb53f19c1199505/File/2023-02/哪吒/lib64"
)
for k, v in result.items():
    print(v, os.path.basename(k))