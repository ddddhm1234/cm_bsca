import strings
import os
import json
import re

class GenerateSign():
    def __init__(self):
        self.libs = None
        return

    @staticmethod
    def is_a_good_sign(string, name, version):
        '''
        判断一个字符串是否适合被作为一个好的签名
        :param string: 字符串
        :param name: 组件名
        :param version: 组件版本
        :return: True/False
        '''
        string = string.lower()
        name = name.lower()
        if name not in string: # 基本要求，字符串中应该包含包名
            if name.startswith("lib") and name[3:] in string: # 如果是libxx, 可以只包含xx
                pass
            else:
                return False

        if string == name: # 字符串也不应该等于包名
             return False

        # if len(string) <= 10: # 字符串长度不应过短
        #     return False
        #
        # if len(string) > 256: # 字符串不应过长
        #     return False

        if string.startswith("/var"): # var目录是linux系统运行时的状态信息，其它组件可能需要访问name组件的状态，也需要这个目录
            return False

        if len(string.split("/")) >= 2 and os.path.basename(string).endswith(".c"):
            # 字符串不应该是源代码文件路径
            return False

        if version in string: # 组件签名不应包含版本号信息
            return False

        return True

    @staticmethod
    def get_good_signs(strings, name, version, version_str_addr, contain_str_addr):
        '''
        返回strings中所有适合当组件签名的字符串
        :param strings: 所有字符串，字典类型
        :param name: 组件名
        :param version: 组件版本号
        :param version_str_addr: 组件程序中版本字符串地址
        :param contain_str_addr: 组件程序中现有签名字符串地址
        :return: ([], int), 可选签名列表, 推荐选择个数
        '''

        contain_str_addr_max = max(contain_str_addr, default=0)
        contain_str_addr_min = min(contain_str_addr, default=0)
        version_str_addr_min = min(version_str_addr, default=0)
        version_str_addr_max = min(version_str_addr, default=0)



        good = []

        # 获取所有适合作为签名的字符串，储存在good列表中
        for k, v in strings.items():
            if GenerateSign.is_a_good_sign(k, name, version):
                good.append(k)
        if len(good) > 0:
            good_min = good[0]  # 地址最小的good列表中的字符串
            good_max = good[0]  # 地址最大的good列表中的字符串
            for k in good:
                if strings[k][0] > strings[good_max][0]:
                    good_max = k
                if strings[k][0] < strings[good_min][0]:
                    good_min = k

            if version_str_addr_min > contain_str_addr_min and version_str_addr_max < contain_str_addr_max:
                # 版本字符串被签名字符串“包裹”
                return (good, 0)
            else:
                if good_min == good_max:
                    return (good, 1)
                good.remove(good_min)
                good.remove(good_max)
                good.insert(0, good_min)
                good.insert(0, good_max)
                return (good, 2)
        else:
            return ([], 0)

    @staticmethod
    def get_version_re(items):
        min_len = len(items[0].split("."))
        max_len = len(items[0].split("."))
        for item in items:
            if len(item.split(".")) > max_len:
                max_len = len(item.split("."))
            if len(item.split(".")) < min_len:
                min_len = len(item.split("."))
        exp = r"([0-9]+" + r"\.[0-9]+" * (min_len - 1) + r"\.?[0-9]*" * (max_len - min_len) + ")"
        return exp

    @staticmethod
    def get_string_re(re):
        # 正则表达式字符串, 顺序不能改变, \\必须是第1次替换的
        chars = ['\\', '$', '(', ')', '*', '+', '.', '[', ']', '?', '^', '{', '}', '|']
        for ch in chars:
            re = re.replace(ch, '\\' + ch)
        return re


    def load_desc(self, name, path):
        with open(name, "r") as f:
            desc = json.load(f)

        libs = {}
        for item in desc:
            item["file"] = os.path.join(path, item["file"])
            if not os.path.exists(item["file"]) or not os.path.isfile(item["file"]):
                raise FileNotFoundError("lib not exists, %s" % (item["file"], ))
            
            _ = item["version"]
            i = 0
            while i < len(_) and ((ord(_[i]) >= 48 and ord(_[i]) <= 57) or _[i] == '.'):
                i += 1
            _ = _[:i]
            if _.endswith("."):
                _ = _[:len(_)-1]
            item["version"] = _[:i]
            libs.setdefault(item["name"], []).append(item)

        self.libs = libs

    def generate(self, least_contain=3):
        if self.libs is None:
            return None
        signs = {}
        for name, items in self.libs.items(): # 遍历组件
            cur_version_re = [] # 当前组件版本签名
            cur_contains = set() # 组件签名，动态增长
            cur_status = []
            version_re = self.get_version_re([x["version"] for x in items]) # 匹配版本号的正则表达式
            for item in items: # 遍历组件程序
                iter_strings = strings.get_file_strings(item["file"]) # 当前组件程序的所有字符串
                iter_strings_set = set(iter_strings.keys())
                iter_version_strings = {} # 当前组件程序的版本信息字符串
                for _ in iter_strings.keys():
                    if item["version"] not in _: # 当前字符串不包含版本号
                        continue
                    iter_version_strings[_] = iter_strings[_]

                # 生成签名
                inter_len = len(cur_contains.intersection(iter_strings_set)) # 组件签名与当前组件程序匹配的项数
                if inter_len < least_contain: # 如果组件签名不足以识别当前组件程序
                    # 扩展组件签名
                    good_signs, reco = self.get_good_signs(iter_strings, item["name"], item["version"],
                                                     [min(iter_version_strings[x]) for x in iter_version_strings.keys()],
                                                     # 当前组件程序的版本字符串的地址
                                                     [min(iter_strings[x]) for x in cur_contains.intersection(iter_strings_set)]
                                                     # 当前组件程序的签名字符串的地址
                                                     )
                    if len(good_signs) < max(least_contain - inter_len, reco):
                        cur_contains.update(good_signs)
                        if not 'not_perfect' in cur_status: # 签名可能不完美
                            cur_status.append('not_perfect')
                    else:
                        cur_contains.update(good_signs[:max(least_contain - inter_len, reco)])

                # 生成版本签名
                if len(iter_version_strings) > 0:
                    ok = False # 是否需要添加新的版本签名
                    for version in iter_version_strings.keys():
                        for _ in cur_version_re:
                            # print(_, version)
                            if re.match(_, version) is not None:
                                ok = True
                    if not ok: # 需要添加签名
                        best = None # 挑选最合适进行匹配的版本签名
                        for _ in iter_version_strings.keys():
                            if len(_) >= len(item["version"]) + 2:
                                best = _
                        if best is None:
                            best = list(iter_version_strings.keys())[0] # 随即选一个吧
                        MAGIC = "==========IDWIDSALKAWDO13920======1002=="
                        best_re = best.replace(item["version"], MAGIC)
                        best_re = self.get_string_re(best_re)
                        best_re = best_re.replace(MAGIC, version_re)
                        assert re.match(best_re, best) is not None
                        cur_version_re.append(best_re)

            # 结束一个组件
            if len(cur_version_re) == 0:
                cur_status.append('version_re_fail')
            if len(cur_contains) < least_contain:
                cur_status.append('sign_fail')
            if 'sign_fail' in cur_status: # 签名失败
                if 'version_re_fail' in cur_status:
                    print('[-]', name, '签名失败')
                    continue
                else:
                    if len(cur_version_re) > 0 and not (cur_version_re[0].startswith("(") and cur_version_re[0].endswith(")")):
                        signs[name] = {"name": name, "version_re": cur_version_re, "contains": list(cur_contains),
                                         "least_contain": 0}
                        print('[-]', name, '仅版本签名')
                        continue
            if 'version_re_fail' in cur_status:
                print('[-]', name, '版本签名失败')
                continue
            if 'not_perfect' in cur_status:
                print('[-]', name, '签名不完美, 不能识别所有组件')
            signs[name] = {"name": name, "version_re": cur_version_re, "contains": list(cur_contains),
                           "least_contain": least_contain}

        return signs

