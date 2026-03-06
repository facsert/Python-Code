import tarfile
import zipfile
import gzip
from os import makedirs
from os.path import dirname
from pathlib import Path
from shutil import copyfileobj

from typing import Iterable, Generator, Any

class Tar:

    read_mode: str = "r"
    write_mode: str = "w"
    
    def compress(self, path_or_files: str|list[str], dst: str) -> int:
        """ 压缩 """
        count: int = 0
        with tarfile.open(dst, self.write_mode) as tar:
            for file, arc in self.list_files(path_or_files):
                tar.add(file, arcname=arc)
                count += 1
        return count

    def extract(self, file: str, dst: str) -> int:
        """ 解压缩 """
        makedirs(dst, exist_ok=True)
        with tarfile.open(file, self.read_mode) as tar:
            tar.extractall(dst)
            return len(tar.getmembers())

    def list_files(self, path_or_files: str|Iterable[str]) -> Generator[tuple[Path, str], Any, None]:
        """ 读取路径或文件列表返回文件 """
        if isinstance(path_or_files, (list, tuple, set)):
            for file in path_or_files:
                p: Path = Path(file)
                yield p, p.name
        else:
            path: Path = Path(path_or_files)
            if path.is_file():
                yield path, path.name
            
            elif path.is_dir():
                for file in path.rglob("*"):
                    if file.is_file():
                        yield file, str(file.relative_to(path))
            else:
                raise FileNotFoundError(path)

class TarZip(Tar):
    """ zip 压缩/解压缩 """

    read_mode: str = "r"
    write_mode: str = "w"

    def compress(self, path_or_files: str|list[str], dst: str) -> int:
        """ zip 压缩 """
        count = 0
        with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for file, arc in self.list_files(path_or_files):
                z.write(file, arcname=arc)
                count += 1
        return count
    
    def extract(self, file, dst) -> int:
        """ zip 解压缩 """
        makedirs(dst, exist_ok=True)
        with zipfile.ZipFile(file, "r") as z:
            z.extractall(dst)
            return len(z.namelist())

class TarGz(Tar):
    """ tar.gz 压缩/解压缩 """
    
    read_mode: str = "r:gz"
    write_mode: str = "w:gz"

class TarXz(TarGz):
    """ tar.xz 压缩/解压缩 """

    read_mode: str = "r:xz"
    write_mode: str = "w:xz"

class Gz:
    """ gz 压缩/解压缩 """

    read_mode: str = "rb"
    write_mode: str = "wb"
    
    def extract(self, file: str, dst: str) -> int:
        makedirs(dirname(dst), exist_ok=True)
        with gzip.open(file, "rb") as f_in:
            with open(dst, "wb") as f_out:
                copyfileobj(f_in, f_out)
        return 1
                    
    def compress(self, path_or_files: str|list[str], dst: str) -> int:
        path = Path(path_or_files)
        if not path.is_file():
            raise TypeError("gzip only supports single file")

        with open(path, self.read_mode) as fs:
            with gzip.open(dst, self.write_mode) as tar:
                copyfileobj(fs, tar)
        
        return 1

def compress(path_or_files: str|list[str], dst: str) -> int:
    """ 路径或文件压缩 """
    name: str = dst.lower()
    if name.endswith(".zip"):
        return TarZip().compress(path_or_files, dst)

    if name.endswith(".tar.gz"):
        return TarGz().compress(path_or_files, dst)

    if name.endswith(".tar.xz"):
        return TarXz().compress(path_or_files, dst)
    
    if name.endswith(".gz"):
        return Gz().compress(path_or_files, dst)
    
    raise RuntimeError("unsupported archive type, applies to zip, tar.gz, tar.xz, gz")

def extract(file: str, dst: str) -> int:
    """ 解压包 """
    path: Path = Path(file)
    if not path.is_file():
        raise FileExistsError(f"{file} not exist or not a package")
    
    name: str = path.name.lower()
    if name.endswith(".zip"):
        return TarZip().extract(file, dst)

    if name.endswith(".tar.gz"):
        return TarGz().extract(file, dst)

    if name.endswith(".tar.xz"):
        return TarXz().extract(file, dst)
    
    if name.endswith(".gz"):
        return Gz().extract(file, dst)
    
    raise RuntimeError("unsupported archive type, applies to zip, tar.gz, tar.xz, gz")

if __name__ == "__main__":
    # 将 /root/home/project 路径下所有文件压缩成 project.tar.gz
    compress("/root/home/project", "/root/home/project.tar.gz")
    
    # 创建 /root/project 路径, 将 project.tar.gz 文件解压到该路径下
    extract("/root/home/project.tar.gz", "/root/project")