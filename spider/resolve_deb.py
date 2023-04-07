import os
import sys
import shutil
from elftools.elf.elffile import ELFFile
import json


def walk_path(path, check, para1):
    c = [path]
    result = []
    while len(c) > 0:
        k = c.pop()
        l = os.listdir(k)
        for _ in l:
            if os.path.isfile(os.path.join(k, _)):
                if check(os.path.join(k, _), para1):
                    result.append(os.path.join(k, _))
            elif os.path.isdir(os.path.join(k, _)):
                c.append(os.path.join(k, _))

    return result

def unzip_deb(deb, deb_name):
    def is_elf(e, name):
        try:
            if os.path.basename(e).split(".")[0].split("_")[0] != name:
                return False
            with open(e, "rb") as f:
                k = ELFFile(f)
            return True
        except:
            return False

    tmp = os.path.join(os.getcwd(), "tmp")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.mkdir(tmp)
    tmp2 = os.path.join(tmp, "data")
    tmp3 = os.path.join(tmp, "control")
    os.mkdir(tmp2)
    os.mkdir(tmp3)
    os.system("cd %s && ar -vx %s" % (tmp, deb))

    control = None
    data = None
    for _ in os.listdir(tmp):
        if _.startswith("control."):
            control = _
        elif _.startswith("data."):
            data = _
    if control is None or data is None:
        return None
    os.system("tar -xvf %s -C %s" % (os.path.join(tmp, control), tmp3))
    os.system("tar -xvf %s -C %s" % (os.path.join(tmp, data), tmp2))
    with open(os.path.join(tmp3, "control"), "r") as f:
        for _ in f:
            if _.startswith("Version:"):
                version = _[_.find(":") + 1:].strip().split("+")[0].strip()
            elif _.startswith("Package:"):
                package = _[_.find(":") + 1:].strip()
            elif _.startswith("Architecture:"):
                arch = _[_.find(":") + 1:].strip()
    if len(version.split(":")) > 1:
        version = version.split(":")[1].strip()
    return (walk_path(tmp2, is_elf, deb_name), package, version, arch)


def walk_deb(deb="deb", output="file"):
    cwd = os.path.join(os.getcwd(), deb)
    output = os.path.join(os.getcwd(), output)
    file_desc = []
    for package in os.listdir(cwd):
        for _ in os.listdir(os.path.join(cwd, package)):
            deb_info = unzip_deb(os.path.join(cwd, package, _), package)
            if deb_info is None:
                print("[-] 解包失败, " + os.path.join(cwd, package, _))
                continue
            for k in deb_info[0]:
                try:
                    shutil.copy(k, os.path.join(output, os.path.basename(k) + deb_info[2] + deb_info[3]))
                    file_desc.append({"name":package, "version": deb_info[2].split("-")[0],
                                  "file": os.path.basename(k) + deb_info[2] + deb_info[3],
                                  "arch": deb_info[3]})
                except:
                    continue
    f = open("desc.json", "w")
    json.dump(file_desc, f)
    f.close()

if __name__ == "__main__":
    walk_deb()