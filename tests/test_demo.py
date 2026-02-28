import pytest
import allure
from utils.generate import mid
from core.api.api_flow import Case
from configs.configure import Environ
from core.api.executor import Executor


@pytest.mark.demo
@pytest.mark.env(Environ.TEST)
@allure.epic("SV-GO")
@allure.feature(next(mid) + "业务流程场景")
class TestLogin:

    @pytest.mark.data("login")
    def test_login(self, data, executor: Executor):
        data = Case(**data)
        executor.execute_test_case(data)

    @pytest.mark.data("getuserinfo")
    def test_get_userinfo(self, data, executor: Executor):
        data = Case(**data)
        executor.execute_test_case(data)

    @pytest.mark.data("upload")
    def test_upload(self, data, executor: Executor):
        data = Case(**data)
        executor.execute_test_case(data)

    @pytest.mark.data("logout")
    def test_logout(self, data, executor: Executor):
        data = Case(**data)
        executor.execute_test_case(data)
