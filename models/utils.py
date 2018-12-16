from urllib.request import urlopen
import torch
import os
import ujson
import shutil
import glob
import pickle
import base64


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def ensure_folder(filename):
    folder = os.path.dirname(os.path.abspath(filename))
    mkdir(folder)


def rmfile(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def rmdir(directory):
    try:
        shutil.rmtree(directory)
    except:
        pass


def cldir(directory):
    rmdir(directory)
    mkdir(directory)


def save_json(filename, obj):
    ensure_folder(filename)
    with open(filename, "w", encoding="utf8") as file:
        ujson.dump(obj, file, indent=4, ensure_ascii=False)


def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding="utf8") as file:
        return ujson.load(file)


def read_all_lines(filename, encoding="utf8"):
    if not os.path.isfile(filename):
        return
    with open(filename, encoding=encoding) as file:
        for line in file:
            line = line.rstrip().strip("\ufeff")
            if line:
                yield line


def find_all_linespans(text, encoding="utf8"):
    last_breaker_index = -1
    for index, char in enumerate(text):
        if char == '\n':
            yield last_breaker_index + 1, index
            last_breaker_index = index
    yield last_breaker_index + 1, len(text)


def write_all_lines(filename, lines, encoding="utf8"):
    ensure_folder(filename)
    with open(filename, "w", encoding=encoding) as file:
        for line in lines:
            file.write(line + "\n")


def distinct_all_lines(filename, encoding="utf8"):
    lines = set(read_all_lines(filename, encoding))
    write_all_lines(filename, sorted(lines))
    return lines


def read_all_text(path, encoding="utf8"):
    with open(path, "r", encoding=encoding) as file:
        return file.read().strip("\ufeff").replace("\r\n", "\n")


def write_all_text(path, text, encoding="utf8"):
    ensure_folder(path)
    with open(path, "w", encoding=encoding) as file:
        file.write(text)


def read_all_bytes(path):
    with open(path, "rb") as file:
        return file.read()


def write_all_bytes(path, bytes):
    ensure_folder(path)
    with open(path, "wb") as file:
        file.write(bytes)


def write_file(path, content):
    if isinstance(content, bytes):
        write_all_bytes(path, content)
    else:
        write_all_text(path, content)


def read_file(path: str):
    if is_text_file(path):
        return read_all_text(path)
    else:
        return read_all_bytes(path)


def copy_file(source_path, target_path):
    ensure_folder(target_path)
    shutil.copyfile(source_path, target_path)


def download(url, path, overwrite=True):
    if os.path.exists(path) and not overwrite:
        return
    response = urlopen(url)
    ensure_folder(path)
    with open(path, 'wb') as file:
        while True:
            chunk = response.read(64 * 1024)
            if not chunk:
                break
            file.write(chunk)


def is_text_file(path):
    return extension(path) in ["txt", "html", "xml", "json"]


def ensure_str(content):
    if isinstance(content, bytes):
        return base64.b64encode(content)
    else:
        return content


def list_files(folder):
    if os.path.exists(folder):
        return [
            x for x in os.listdir(folder) if os.path.isfile(os.path.join(folder, x))
        ]
    else:
        return []


def list_filepaths(folder, pattern="*.*"):
    for path in glob.glob(f"{folder}/{pattern}"):
        yield path


def list_folders(folder):
    if not os.path.isdir(folder):
        return []
    return [x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))]


def basename(path):
    return os.path.basename(path)


def extension(path):
    return os.path.splitext(path)[-1][1:]


def basename_without_extension(path):
    return os.path.splitext(basename(path))[0]


def dump(path, obj):
    ensure_folder(path)
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def load(path):
    with open(path, "rb") as file:
        return pickle.load(file)


def batch_convert(source_folder, target_folder, method, error_folder=None, format=None):
    mkdir(target_folder)
    if error_folder is not None:
        mkdir(error_folder)
    for source_path in list_files(source_folder):
        basename = os.path.basename(source_path)
        if format is not None:
            basename = os.path.splitext(basename)[0] + "." + format
        target_path = os.path.join(target_folder, basename)
        try:
            if error_folder is not None:
                error_path = os.path.join(error_folder, basename)
                rmfile(error_path)
                method(source_path, target_path, error_path)
                if os.path.isfile(error_path):
                    raise read_all_text(error_path)
            else:
                method(source_path, target_path)
            print(f"{basename_without_extension(source_path)} converted.")
        except:
            print(f">>>>>>>failed to convert {source_path}")


class Logger(object):
    def __init__(self, output_file, flush_interval=10):
        ensure_folder(output_file)
        self.counter = 0
        self.flush_interval = flush_interval
        self.output_file = open(output_file, "w", encoding="utf8")

    def __call__(self, message, verbose=True):
        if verbose:
            print(message)
        self.output_file.write(message + "\n")
        self.counter += 1
        if self.counter >= self.flush_interval:
            self.counter = 0
            self.output_file.flush()


class Metrics(object):
    def __init__(self):
        self.common = self.predict = self.actual = 0

    def accumulate(self, predict, target):
        common = (predict * target).sum().tolist()
        predict = predict.sum().tolist()
        actual = target.sum().tolist()
        self.common += common
        self.predict += predict
        self.actual += actual

    def precision(self):
        return self.common / self.predict if 0 < self.common else 0

    def recall(self):
        return self.common / self.actual if 0 < self.common else 0

    def f1(self):
        return 2 * self.precision() * self.recall() / (self.precision() + self.recall())
