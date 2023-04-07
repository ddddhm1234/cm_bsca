### 项目说明
* ./spider 目录是爬虫程序，可以从清华debian源中爬取deb包，并解析deb包
* ./generate.py 通过输入elf与其对应的组件名，版本号标签，自动化生成签名
* ./checker.py 通过签名，检测组成elf的组件与组件版本号
* ./cvedetails-lookup.py 通过组件与组件版本号，查找关联CVE
* ./lib.json 现阶段提取的组件签名库