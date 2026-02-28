import allure
from dataclasses import asdict
from core.api.core import Request
from core.api.api_flow import Case, Flow
from utils.allure_reports import CustomAllure


class Executor:
    """执行器类负责按文件定义的测试流程执行测试"""

    def __init__(self, request: Request = None):
        self.request = request if request else Request()

    def execute_test_case(self, case: Case):
        """
        单接口测试

        :param case: 测试用例
        :type case: CaseConfig
        """

        try:
            # 设置Allure报告标题和描述
            allure.dynamic.story(case.name)
            allure.dynamic.title(case.description)

            # 验证输入参数类型
            if not isinstance(case, Case):
                raise TypeError(f"参数类型错误: {type(case)}，必须是 CaseConfig 类型")

            # 处理数据步骤
            with allure.step("数据预处理"):
                # TODO 数据预处理逻辑:变量替换、数据格式化
                # 替换请求参数中的变量
                params = self.request.context.parse_and_replace(asdict(case.request))

            # 发送请求步骤
            with allure.step("发送请求"):
                files = params.pop("files", None)
                if files:
                    for k, v in files.items():
                            files = {k: open(v, "rb")}
                            
                response = self.request.request(files=files, **params)

            # 提取变量步骤（如果有）
            if case.extract:
                with allure.step("提取变量"):
                    self.request.extractor(response, case.extract)

            # 验证接口响应信息（如果有）
            if case.validate:
                with allure.step("验证接口响应信息"):
                    assert_result = self.request.validator(
                        response,
                        case.validate,
                        self.request.context.variables.get("data-source"),
                    )

                # 使用更明确的断言
                if not assert_result.get("passed"):
                    raise AssertionError(
                        f"验证失败: {assert_result.get('message', '未知错误')}"
                    )

        except Exception as e:
            # 记录异常到Allure报告
            CustomAllure.attach(str(e), "异常信息", "txt")
            raise

    def execute_test_flow(self, flow: Flow):
        """
        业务流程测试

        :param case_info: 测试用例配置信息
        :type case_info: CaseConfig
        :return: 测试执行结果汇总
        :rtype: Dict[str, Any]
        """

        try:
            # TODO: 实现多接口串联测试逻辑
            # 这里应该处理多个测试用例的执行流程
            # 例如：执行前置条件 -> 执行测试用例 -> 执行后置条件

            allure.dynamic.epic(flow.info.project)
            allure.dynamic.title(flow.case.description)

            # 验证输入参数类型
            if not isinstance(flow.case, Case):
                raise TypeError(
                    f"参数类型错误: {type(flow.case)}，必须是 CaseConfig 类型"
                )

            # 处理数据步骤
            with allure.step("数据预处理"):
                # TODO 数据预处理逻辑:变量替换、数据格式化
                # 替换请求参数中的变量
                params = self.request.context.parse_and_replace(
                    asdict(flow.case.request)
                )

            # 发送请求步骤
            with allure.step("发送请求"):
                response = self.request.request(**params)

            # 提取变量步骤（如果有）
            if flow.case.extract:
                with allure.step("提取变量"):
                    self.request.extractor(response, flow.case.extract)

            # 验证接口响应信息（如果有）
            if flow.case.validate:
                with allure.step("验证接口响应信息"):
                    assert_result = self.request.validator(
                        response,
                        flow.case.validate,
                        self.request.context.variables.get("data-source"),
                    )

                # 使用更明确的断言
                if not assert_result.get("passed"):
                    raise AssertionError(
                        f"验证失败: {assert_result.get('message', '未知错误')}"
                    )

        except Exception as e:
            # 记录异常到Allure报告
            CustomAllure.attach(str(e), "多接口业务流程测试异常信息", "txt")
            raise
