from elftools.elf import elffile

def get_file_strings(file, min_length=3):
    '''
    获取文件中的所有可打印字符串及其出现位置，如果文件是ELF格式且存在.rodata section，
    则只提取.rodata section中的字符串
    :param file: 文件路径
    :param min_length: 字符串最短长度
    :return: {'s': [1,2,3]}
    '''
    f = open(file, "rb")
    try:
        e = elffile.ELFFile(f)
        sec = e.get_section_by_name(".rodata")
        if sec is None:
            data = bytes(f.read())
        else:
            data = sec.data()
        return get_data_strings(data, min_length)
    except elffile.ELFError:
        data = bytes(f.read())
        return get_data_strings(data, min_length)

def get_data_strings(file_data, min_length=3):
    '''
    :param file_data: 数据
    :param min_length: 最短字符串长度
    :return: {'s': [1,2,3]}
    '''
    strings = {}
    buf = []
    for i, ch in enumerate(file_data):
        if ch >= 32 and ch <= 126:  # 可打印字符串
            buf.append(chr(ch))
        else:
            cur_str = ''.join(buf)
            if min_length <= len(cur_str):
                strings.setdefault(cur_str, []).append(i - len(strings))
            buf = []

    return strings

if __name__ == "__main__":
    print(get_file_strings("/bin/cat", 5))