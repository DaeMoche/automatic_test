import re
import json
import jsonpath
from urllib.parse import urljoin
from typing import Any, Dict, List
from requests import Response, Session
from utils.assertions import Assertions
from core.api.settings import DataSource
from dataclasses import dataclass, field
from utils.allure_reports import CustomAllure


class ValidateMessage:
    """验证结果描述信息"""

    PASSED = "测试步骤执行通过！"
    FAILED = "测试步骤执行未通过！"


class ValidateStatus:
    """验证结果状态"""

    PASSED = True
    FAILED = False


@dataclass
class Context:

    variables: Dict[str, Any] = field(default_factory=dict)
    session: Session = field(default_factory=Session)

    def _replace(self, data: Any) -> Any:
        if isinstance(data, dict):
            data = {k: self._replace(v) for k, v in data.items()}
        if isinstance(data, list):
            data = [self._replace(item) for item in data]
        if isinstance(data, str):
            for placeholder in ["${%s}", "{{%s}}"]:
                for k, v in self.variables.items():
                    key = placeholder % k
                    if key in data:
                        data = data.replace(key, str(v))
        return data

    def parse_and_replace(self, data: Any):
        """
        解析Yaml中的使用占位符占位的变量，并替换为目标值。

        :param data: 含有占位符的任意类型数据
        :type data: Any
        """

        data_str = (
            data
            if isinstance(data, str)
            else json.dumps(data, indent=2, ensure_ascii=False)
        )

        if "${" in data_str and "}" in data_str:

            CustomAllure.attach(data_str, "原始变量", "json")

            for _ in range(data_str.count("${")):
                start_index = data_str.index("$")
                end_index = data_str.index("}", start_index)
                variable = data_str[start_index : end_index + 1]

                # 正则提取变量
                match = re.match(r"\$\{(\w+)\((.*?)\)\}", variable)

                if match:

                    function, params = match.groups()
                    params = params.split(",") if params else []

                    # 利用反射调用获参数值的方法
                    value = getattr(self, function)(*params)

                    # 替换原始数值
                    data_str = re.sub(re.escape(variable), str(value), data_str)

                    log = {
                        "match": str(match),
                        "function": function,
                        "params": params,
                        "result": value,
                    }

                    CustomAllure.attach(log, "提取并执行占位函数", "json")

                if not match:
                    data_str = self._replace(data_str)

            CustomAllure.attach(data_str, "替换变量值", "json")

        return json.loads(data_str)

    def access_token(self):
        return self.variables.get("access_token")


@dataclass
class Request:
    """请求处理类"""

    base_url: str = field(default="")
    context: Context = field(default_factory=Context)

    def request(
        self, method: str, path: str, files: Any = None, **kwargs: Dict[str, Any]
    ) -> Response:
        """
        发送http请求

        :param method: 请求方法
        :type method: str
        :param path: 请求路径
        :type path: str
        :param kwargs: 由请求参数组装的字典
        :type kwargs: Dict[str, Any]
        :return: 请求响应结果
        :rtype: Response
        """

        # 构建完整URL
        url = self._build_url(path)

        # 记录请求信息
        self._record_request(method, url, **kwargs)

        # 发送请求
        response = self.context.session.request(method, url, files=files, **kwargs)
        response = self._encode(response)

        # 记录响应信息
        self._record_response(response)

        return response

    def extractor(self, res: Response, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        参数提取器，用于从接口响应信息中提取目标参数值

        :param res: 接口响应信息
        :type res: Response
        :param mapping: 目标参数key与提取表达式组成的字典
        :type mapping: Dict[str, str]
        :return: 返回目标参数key与参数值组成的字典
        :rtype: Dict[str, Any]
        """
        extracted_vars = {}
        try:
            data = res.json()
            for var_name, expr in mapping.items():
                value: List[Any] = jsonpath.jsonpath(data, expr)
                if len(value) > 0:
                    self.context.variables[var_name] = value[0]
                    extracted_vars[var_name] = value[0]

        except Exception as e:
            extracted_vars["error"] = str(e)

        self._record_extract_variables(mapping, extracted_vars)
        return extracted_vars

    def validator(
        self, res: Response, validates: List[Dict[str, Any]], dataSource: DataSource
    ):
        """
        接口响应信息验证器，用于校验接口返回信息是否满足预期结果

        :param self: 说明
        :param res: 说明
        :type res: Response
        :param validates: 说明
        :type validates: List[Dict[str, Any]]
        """

        result = {}
        try:

            assert_result = Assertions.assert_result(validates, res, dataSource)
            if assert_result == 0:
                result.setdefault("passed", ValidateStatus.PASSED)
                result.setdefault("message", ValidateMessage.PASSED)
            else:
                result.setdefault("passed", ValidateStatus.FAILED)
                result.setdefault("message", ValidateMessage.FAILED)
        except Exception as e:
            result.setdefault("message", str(e))
        finally:
            return result

    def _build_url(self, path: str) -> str:
        """
        构建完整的请求路径，当 **`path`** 是一个完整地址(http或https链接地址)，则设path为当前接口的请求地址，反之，会通过配置文件variables中的 **`base_url`** 。格式如下：
        >>> 'xxx/xxx/xxx'
        >>> 'http://www.example.com/example'
        >>> 'https://www.example.com/example'

        :param path: 请求路径

        :type path: str
        :return: 返回完整的接口请求地址
        :rtype: str
        """

        if self.base_url == "":
            self.base_url = self.context.variables.get("base_url")

        if "http://" in path or "https://" in path:
            return path

        return urljoin(self.base_url, path)

    def _encode(self, res: Response) -> Response:
        """
        处理接口返回值出现unicode编码时，如：\\u767b

        :param self: 说明
        :param res: 说明
        :type res: Response
        :return: 说明
        :rtype: Response
        """

        match = re.search(r"\\u[0-9a-fA-F]{4}", res.text)
        result = res.text.encode().decode("unicode_escape") if match else res

        return result

    def _record_request(self, method: str, path: str, **kwargs: Dict[str, Any]):
        """
        记录请求参数到allure中
        """

        _log = {"method": method, "url": path}
        _log.update(kwargs)

        CustomAllure.attach(_log, "请求参数", "json")

    def _record_response(self, res: Response):
        """
        记录接口响应信息到allure中
        """

        _log = {
            "status_code": res.status_code,
            "headers": dict(res.headers),
            "cookies": res.cookies.get_dict() if res.cookies.get_dict() else None,
            "body": json.loads(
                (
                    res.json()
                    if "applicathion/json" in res.json().get("Content-Type", "")
                    else res.text
                ),
            ),
            "elapsed": res.elapsed.total_seconds(),
        }

        CustomAllure.attach(_log, "请求结果", "json")

    def _record_extract_variables(
        self, mapping: Dict[str, str], extracted: Dict[str, Any]
    ):
        """
        记录变量提取到allure中
        """

        CustomAllure.attach(mapping, "提取表达式", "json")
        CustomAllure.attach(extracted, "提取结果", "json")

    def _record_validate_results(
        self,
        validators: Dict[str, Any],
        results: List[Dict[str, Any]],
    ):
        """
        记录验证过程到allure中
        """

        _log = {"validates": validators, "validate_results": results}

        CustomAllure.attach(_log, "接口响应验证结果", "json")
