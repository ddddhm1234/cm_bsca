import strings
import re
import json
import os

class Checker():
    def __init__(self):
        self.signs = None
        return

    def load_sign(self, path):
        with open(path, "r") as f:
            self.signs = json.load(f)
        for name, sign in self.signs.items():
            sign["re"] = []
            sign["re2"] = None
            for x in sign["version_re"]:
                if x.startswith('(') and x.endswith(')') and x[-2] != '\\':
                    sign["re2"] = re.compile(x)
                else:
                    sign["re"].append(re.compile(x))
            sign["contain_set"] = set(sign["contains"])

    @staticmethod
    def max_version(vers):
        c_max = ["0", "0", "0"]
        for _ in vers:
            a = _.split(".")
            try:
                for v1, v2 in zip(a, c_max):
                    if int(v1) > int(v2):
                        c_max = a
                        break
                    elif int(v1) < int(v2):
                        break
            except:
                pass
        return '.'.join(c_max)

    def scan_file(self, file):
        string = strings.get_file_strings(file)
        set_string = set(string.keys())
        result = []
        for name, sign in self.signs.items():
            cur = {}

            common = set_string.intersection(sign["contain_set"])
            contains_addr = [min(string[x]) for x in common]
            if len(common) < sign["least_contain"]:
                continue

            cur["name"] = name
            prior_ver = [] # 值得信任的版本号
            last_ver = [] # 很难信任的版本号
            for s in string.keys():
                for re_p in sign["re"]:
                    m = re_p.match(s)
                    if m is not None:
                        prior_ver.append(m.group(1))
            if len(prior_ver) > 0:
                cur["version"] = self.max_version(prior_ver)
            else:
                if len(common) == 0: # 如果没有命中contain，就不要相信last_ver了
                    continue

                if sign["re2"] is None:
                    cur["version"] = ""
                else:
                    _ = sign["re2"]
                    for s in string.keys():
                        m = _.match(s)
                        if m is not None:
                            if m.group(0) == m.group(1):
                                last_ver.append(s)
                    if len(last_ver) == 1:
                        cur["version"] = last_ver[0]
                    elif len(last_ver) == 0:
                        cur["version"] = ""
                    else:
                        m_max = max(contains_addr)
                        m_min = min(contains_addr)
                        vers = []
                        for r in last_ver:
                            if min(string[r]) > m_min and min(string[r]) < m_max:
                                vers.append(r)
                        if len(vers) == 0:
                            cur["version"] = self.max_version(last_ver)
                        else:
                            cur["version"] = self.max_version(vers)
            result.append(cur)
        return result

    def scan_path(self, path):
        c = [path]
        result = {}
        while len(c) > 0:
            k = c.pop()
            l = os.listdir(k)
            for _ in l:
                if os.path.isfile(os.path.join(k, _)):
                    result[os.path.join(k, _)] = self.scan_file(os.path.join(k, _))
                elif os.path.isdir(os.path.join(k, _)):
                    c.append(os.path.join(k, _))
        return result