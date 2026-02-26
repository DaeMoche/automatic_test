import os
import yaml
from pathlib import Path
from root import ROOT_PATH
from typing import Any, Dict


class YAMLParser:
    """YAML文件解析类"""

    def __init__(self, file_path: str = None, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self.data = {}

    def _set_full_path__(self, path: str) -> str:
        if not path:
            raise ValueError("文件路径不能为空！")
        file_path = os.path.join(ROOT_PATH, path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{self.file_path} 不存在！")
        return file_path

    def read(self, file_path: str = None) -> Dict[str, Any]:
        """
        读取Yaml文件

        :return: 读取yaml文件内容并返回一个字典
        :rtype: Dict[str, Any]
        """

        file_path = (
            self._set_full_path__(file_path)
            if file_path
            else self._set_full_path__(self.file_path)
        )
        case_list = []
        with open(file=file_path, mode="r", encoding=self.encoding) as f:
            data = yaml.safe_load(f)
            if isinstance(data, list) and len(data) <= 1:
                info = data[0].get("info")
                cases = data[0].get("cases")

                if not info and not cases:
                    return data

                for case in cases:
                    _case = [info, case]
                    case_list.append(_case)

                return case_list
            else:
                return data

    def read_by_section(
        self, file_path: str = None, section: str = None
    ) -> Dict[str, Any]:
        return self.read(file_path).get(section)

    def write(self, file_path: str, data: Any):
        """
        将任意类型数据写入yaml文件

        :param self: 说明
        :param data: 待写入数据
        :type data: Any
        """

        def touch(file_path: str) -> str:
            return Path(os.path.join(ROOT_PATH, file_path))

        with open(file=touch(file_path), mode="w", encoding=self.encoding) as f:
            yaml.safe_dump(data, f)


def load_yaml(file_path: str = None):
    return YAMLParser(file_path) if file_path else YAMLParser()


def read_yaml(file_path: str):
    return load_yaml(file_path).read()


if __name__ == "__main__":
    data = read_yaml("configs\\settings.yaml")
    print(f"server: {data}")
    print(f"data: {data}")
