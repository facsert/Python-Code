import tarfile
import zipfile
import gzip
from os import makedirs
from os.path import basename, exists
from re import search

import rarfile
from loguru import logger

class Tar:
    """ 压缩和解压包 """

    @staticmethod
    def extract_zip(filepath, output):
        """ 解压 zip 压缩文件 """
        makedirs(output, exist_ok=True)
        with zipfile.ZipFile(filepath, 'r') as package:
            package.extractall(output)
        return output

    @staticmethod
    def extract_targz(filepath, output):
        """ 解压 tar.gz 压缩文件 """
        makedirs(output, exist_ok=True)
        with tarfile.open(filepath, "r:gz") as package:
            package.extractall(output)
        return output

    @staticmethod
    def extract_tarxz(filepath, output):
        """ 解压 tar.xz 压缩文件 """
        makedirs(output, exist_ok=True)
        with tarfile.open(filepath, "r:xz") as package:
            package.extractall(output)
        return output

    @staticmethod
    def extract_rar(filepath, output):
        """ 解压 rar 压缩文件 """
        makedirs(output, exist_ok=True)
        with rarfile.RarFile(filepath, "r") as package:
            package.extractall(output)
        return output

    @staticmethod
    def extract_gz(filepath, output):
        """ 解压 gz 压缩文件(gz 是单文件) """
        gz = gzip.open(filepath, 'rb')
        with open(output, 'wb') as f:
            while True:
                chunk = gz.read(65535)
                if not chunk:
                    break
                f.write(chunk)
        gz.close()

    @classmethod
    def extract(cls, filepath, output):
        """ 解压 .tar.gz, .tar.xz, .gz, .rar, .zip 压缩包"""
        filename = basename(filepath).lower()
        suffix_list = (".tar.gz", ".tar.xz", ".gz", ".rar", ".zip")
        suffix = search(f"({'|'.join(suffix_list)})$", filename)
        if not suffix:
            logger.error(f"Not support extract {filepath}")
            return False

        {
            ".tar.gz": cls.extract_targz,
            ".tar.xz": cls.extract_tarxz,
            ".gz": cls.extract_gz,
            ".rar": cls.extract_rar,
            ".zip": cls.extract_zip,
        }[suffix.group()](filepath, output)
        return True

    @staticmethod
    def compress_zip(files, output):
        """ 压缩成 zip 文件 """
        with zipfile.ZipFile(output, 'w') as package:
            _ = [package.write(file) for file in files]

    @staticmethod
    def compress_targz(files, output):
        """ 压缩成 tar.gz 文件 """
        with tarfile.open(output, "w:gz") as package:
            _ = [package.add(file) for file in files]

    @staticmethod       
    def compress_tarxz(files, output):
        """ 压缩成 tar.xz 文件 """
        with tarfile.open(output, "w:xz") as package:
            _ = [package.add(file) for file in files]

    @staticmethod
    def compress_gz(file, output):
        """ 压缩成 gz 文件 """
        file = file if isinstance(file, str) else file[0]
        with open(file, 'rb') as fp:
            with gzip.open(output, 'wb') as gz:
                while True:
                    chunk = fp.read(65535)
                    if not chunk:
                        break
                    gz.write(chunk)

    @classmethod
    def compress(cls, files:list[str]|str, output:str) -> bool:
        """ 压缩文件(不支持 rar)"""
        package_name = basename(output).lower()
        suffix_list = (".tar.gz", ".tar.xz", ".gz", ".zip")
        suffix = search(f"({'|'.join(suffix_list)})$", package_name)
        if not suffix:
            logger.error(f"Not support compress {output}")
            return False

        files = files if isinstance(files, list) else [files]
        not_exist = list(filter(lambda f: not exists(f), files))
        if not_exist:
            logger.error(f"File not exists: {list(not_exist)}")
            return False

        {
            ".tar.gz": cls.compress_targz,
            ".gz": cls.compress_gz,
            ".tar.xz": cls.compress_tarxz,
            ".zip": cls.compress_zip,
        }[suffix.group()](files, output)
        return True

if __name__ == '__main__':
    pass
