import json
import os


def obj2json(obj: object, indent=4) -> str:
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=indent, ensure_ascii=False)


def check_file(file_name: str, filter_exts: list, exclude_exts: list):
    for e in exclude_exts:
        if file_name.endswith(e):
            return False
    for e in filter_exts:
        if file_name.endswith(e):
            return True
    return False


def list_dir_files(dir_path: str, filter_exts: list, exclude_exts: list):
    if os.path.isfile(dir_path):
        return [dir_path]

    if not os.path.isdir(dir_path):
        print("create directory " + dir_path)
        os.mkdir(dir_path)

    res = []
    files = os.listdir(dir_path)
    assert isinstance(files, list)
    for file in files:
        if os.path.isdir(file) or not check_file(file, filter_exts, exclude_exts):
            continue
        path = dir_path + os.sep + file
        res.append(path)
    return res
