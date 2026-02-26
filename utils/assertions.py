import operator
import jsonpath
from requests import Response
from typing import Any, Dict, List, Callable
from core.api.settings import DataSource
from utils.exceptions import AssertTypeError
from utils.db_sever import db_client
from utils.allure_reports import CustomAllure


class AssertType:
    """断言状态"""

    EQUAL = "相等"
    ERROR = "错误"
    PASSED = "通过"
    FAILED = "失败"
    EXISTS = "存在"
    CONTAIN = "包含"
    EXCEPTION = "断言异常"
    NOT_EQUAL = "不相等"
    NOT_EXISTS = "不存在"
    NOT_CONTAIN = "不包含"


class Assertions:
    """断言处理模块类"""

    @classmethod
    def _assert_by_status_code(cls, expected: int, actual: int) -> int:
        """
        接口响应状态码断言

        :param expected: 期望结果
        :type expected: int
        :param actual: 接口响应状态码
        :type actual: int
        :return: 断言状态:
            >>> 0: 通过
            >>> 1: 未通过
        :rtype: int
        """
        success_flag = 0
        try:
            expected = int(expected) if isinstance(expected, str) else expected
            msg = ""
            if expected == actual:
                assert_status = AssertType.PASSED
                msg = f"断言通过！期望结果:{expected} == 实际结果:{actual}"
            else:
                assert_status = AssertType.FAILED
                msg = f"断言失败！期望结果:{expected} != 实际结果:{actual}"
                success_flag += 1
            info = {"expected": expected, "actual": actual, "message": msg}
            CustomAllure.attach(info, f"状态码断言: {assert_status}", "json")
        except Exception as e:
            assert_status = AssertType.EXCEPTION
            success_flag += 1
            CustomAllure.attach(str(e), f"状态码断言: {assert_status}", "json")
        finally:
            return success_flag

    @classmethod
    def _assert_by_contain_context(cls, expected: Dict[str, Any], res: Response) -> int:
        """
        字符串包含模式，断言预期结果字符串是否包含在接口实际响应返回信息中

        :param expected: 期望结果
        :type expected: Dict[str, Any]
        :param res: 接口响应信息 :class:`Response`
        :type res: Response
        :return: 断言状态:
            >>> 0: 通过
            >>> 1: 未通过
        :rtype: int
        """
        success_flag = 0
        try:
            for assert_key, assert_value in expected.items():

                actual: List[str] = jsonpath.jsonpath(res.json(), f"$..{assert_key}")

                if len(actual) > 0:

                    actual_str = "".join(actual)

                    if assert_value in actual_str:

                        msg = "断言通过！期望结果在实际结果中存在！"
                        assert_status = AssertType.CONTAIN

                    else:

                        success_flag += 1
                        assert_status = AssertType.NOT_CONTAIN
                        msg = "断言失败！期望结果在实际结果中不存在！"

                    info = {"expected": assert_value, "actual": actual, "message": msg}

                    CustomAllure.attach(info, f"包含断言: {assert_status}", "json")

        except Exception as e:
            success_flag += 1
            assert_status = AssertType.EXCEPTION
            CustomAllure.attach(str(e), f"包含断言: {assert_status}", "json")

        finally:
            return success_flag

    @classmethod
    def _assert_by_equal(cls, expected: Dict[str, Any], res: Response) -> int:
        """
        相等断言，根据预期结果与接口响应实际结果进行对比

        :param expected: 期望结果
        :type expected: Dict[str, Any]
        :param res: 接口响应信息
        :type res: Response
        :return: 断言状态:
            >>> 0: 通过
            >>> 1: 未通过
        :rtype: int
        """
        success_flag = 0
        try:
            if isinstance(expected, dict) and isinstance(res, Response):
                # 获取期望结果与实际结果相同的key
                common_key = list(expected.keys() & res.json().keys())
                if common_key:
                    common_key = common_key[0]
                    # 根据相同key去接口响应信息获取实际结果,生成实际结果字典
                    actual = {common_key: res.json().get(common_key)}

                    result = operator.eq(expected, actual)

                    if result:
                        assert_status = AssertType.EQUAL
                        msg = f"断言通过！期望结果:{expected} == 实际结果:{actual}"
                    # print(msg)
                    else:
                        success_flag += 1
                        assert_status = AssertType.NOT_EQUAL
                        msg = f"断言失败！期望结果:{expected} != 实际结果:{actual}"

                    # print(msg)
                    info = {"expected": expected, "actual": actual, "message": msg}

                    CustomAllure.attach(info, f"相等断言: {assert_status}", "json")

                else:
                    for assert_key, _ in expected.items():
                        actual = {
                            assert_key: jsonpath.jsonpath(
                                res.json(), f"$..{assert_key}"
                            )[0]
                        }
                        if operator.eq(expected, actual):
                            assert_status = AssertType.EQUAL
                            msg = f"断言通过！期望结果:{expected} == 实际结果:{actual}"
                        else:
                            success_flag += 1
                            assert_status = AssertType.NOT_EQUAL
                            msg = f"断言失败！期望结果:{expected} != 实际结果:{actual}"

                        info = {"expected": expected, "actual": actual, "message": msg}

                        CustomAllure.attach(info, f"相等断言: {assert_status}", "json")

        except Exception as e:
            print(e)
            success_flag += 1
            assert_status = AssertType.EXCEPTION
            CustomAllure.attach(str(e), f"相等断言: {assert_status}", "json")
        finally:
            return success_flag

    @classmethod
    def _assert_by_not_equal(cls, expected: Dict[str, Any], res: Response) -> int:
        """
        不相等断言，根据预期结果与接口响应实际结果进行对比

        :param expected: 期望结果
        :type expected: Dict[str, Any]
        :param res: 接口响应信息
        :type res: Response
        :return: 断言状态:
            >>> 0: 通过
            >>> 1: 未通过
        :rtype: int
        """
        success_flag = 0
        try:
            if isinstance(expected, dict) and isinstance(res, Response):
                # 获取期望结果与实际结果相同的key
                common_key = list(expected.keys() & res.json().keys())
                if common_key:
                    common_key = common_key[0]
                    # 根据相同key去接口响应信息获取实际结果,生成实际结果字典
                    actual = {common_key: res.json().get(common_key)}
                    result = operator.ne(expected, actual)
                    if result:
                        assert_status = AssertType.NOT_EQUAL
                        msg = f"断言通过！期望结果:{expected} != 实际结果:{actual}"
                        # print(msg)
                    else:
                        success_flag += 1
                        assert_status = AssertType.EQUAL
                        msg = f"断言失败！期望结果:{expected} == 实际结果:{actual}"
                        # print(msg)
                    info = {"expected": expected, "actual": actual, "message": msg}
                    CustomAllure.attach(info, f"不相等断言: {assert_status}", "json")

                else:
                    for assert_key, _ in expected.items():

                        actual = {
                            assert_key: jsonpath.jsonpath(
                                res.json(), f"$..{assert_key}"
                            )[0]
                        }

                        if operator.ne(expected, actual):
                            assert_status = AssertType.NOT_EQUAL
                            msg = f"断言通过！期望结果:{expected} != 实际结果:{actual}"

                        else:
                            success_flag += 1
                            assert_status = AssertType.EQUAL
                            msg = f"断言失败！期望结果:{expected} == 实际结果:{actual}"

                        info = {"expected": expected, "actual": actual, "message": msg}

                        CustomAllure.attach(
                            info, f"不相等断言: {assert_status}", "json"
                        )

        except Exception as e:
            print(e)
            success_flag += 1
            assert_status = AssertType.EXCEPTION
            CustomAllure.attach(str(e), f"不相等断言: {assert_status}", "json")
        finally:
            return success_flag

    @classmethod
    def _assert_by_database(cls, sql: str, dataSource: DataSource) -> int:
        """
        数据库断言

        :param cls: 说明
        :param expected: 说明
        :type expected: Dict[str, Any]
        :param db: 说明
        :type db: Any
        :return: 断言状态:
            >>> 0: 通过
            >>> 1: 未通过
        :rtype: int
        """
        success_flag = 0
        assert_status = None
        try:
            client = db_client(dataSource)
            res = client.query(sql)
            if res:
                assert_status = AssertType.EXISTS
                msg = "断言通过！数据库存在该记录！"
            else:
                success_flag += 1
                assert_status = AssertType.NOT_EXISTS
                msg = "断言失败！数据库不存在该记录，请检查sql语句是否正确！"

            # print("断言通过！")
            info = {"sql": sql, "result": res, "message": msg}
            CustomAllure.attach(info, f"数据库断言: {assert_status}", "json")

        except Exception as e:
            success_flag += 1
            assert_status = AssertType.EXCEPTION
            CustomAllure.attach(str(e), f"数据库断言: {assert_status}", "json")
        finally:
            return success_flag

    @classmethod
    def assert_result(
        cls,
        expected: List[Dict[str, Any]],
        res: Response,
        dataSource: DataSource = None,
    ) -> int:
        """
        断言主函数

        :param expected: 期望结果
        :type expected: List[Dict[str,Any]]
        :param res: 接口响应信息
        :type res: Response
        """
        method_mapping = {
            "status_code": cls._assert_by_status_code,
            "contain": cls._assert_by_contain_context,
            "eq": cls._assert_by_equal,
            "ne": cls._assert_by_not_equal,
            "sql": cls._assert_by_database,
        }
        all_flag = 0
        try:
            for expect in expected:
                for assert_mode, assert_value in expect.items():
                    func: Callable[[Any, Any], int] = method_mapping.get(assert_mode)

                    # Python 3.10 以上支持match
                    if func is not None:
                        flag = 0
                        match assert_mode:
                            case "status_code":
                                flag = func(assert_value, res.status_code)
                            case "contain":
                                flag = func(assert_value, res)
                            case "eq":
                                flag = func(assert_value, res)
                            case "ne":
                                flag = func(assert_value, res)
                            case "sql":
                                flag = func(assert_value, dataSource)
                            case _:  # _表示匹配到其他任何情况
                                raise AssertTypeError(
                                    f"未知定义的断言模式:{assert_mode}"
                                )
                        all_flag += flag

        except Exception as e:
            raise e
        finally:
            return all_flag
