from typing import Any, Dict
from utils.yaml_parse import read_yaml
from dataclasses import dataclass, field


@dataclass
class ReqestParameter:
    """定义请求参数类"""

    path: str = None
    method: str = field(default="GET")
    headers: Dict[str, Any] = None
    params: Dict[str, Any] = None
    json: Dict[str, Any] = None
    data: Dict[str, Any] = None
    cookies: Dict[str, Any] = None
    files: Dict[str, object] = None
    timeout: int = 15

    def __post_init__(self):
        self.method = self.method.upper()


@dataclass
class Case:
    """定义测试用例类"""

    name: str = None
    extract: Dict[str, Any] = None
    validate: Dict[str, Any] = None
    description: str = None
    request: Dict[str, Any] = field(default_factory=dict)
    precondition: Dict[str, Any] = None
    postcondition: Dict[str, Any] = None

    def __post_init__(self):
        self.request = ReqestParameter(**self.request)


@dataclass
class Information:
    """allure报告信息"""

    project: str = field(default="Project")
    module: str = field(default="Module")


@dataclass
class Flow:
    info: Information = None
    case: Case = field(default_factory=Case)

    def __post_init__(self):
        self.info = Information(**self.info)
        self.case = Case(**self.case)


if __name__ == "__main__":
    # data = read_yaml("tests\\test_data\\logout.yaml")
    # data = read_yaml("case.yaml")
    data = read_yaml("case.yaml")
    for case in data:
        _case = Flow(*case)
        print(_case)
    # case = FlowConfig(**data[0])

    # print(asdict(case))
