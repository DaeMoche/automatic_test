import pytest
import allure
from core.api.api_flow import Flow
from utils.generate import cid, mid
from configs.configure import Environ
from core.api.executor import Executor


@pytest.mark.demo
@pytest.mark.env(Environ.TEST)
@allure.feature(next(mid) + "登录场景")
class TestLoginFlow:

    @pytest.mark.skip
    @pytest.mark.data("case")
    def test_login_flow(self, data, executor: Executor):
        data = Flow(*data)
        allure.dynamic.story(next(cid) + data.case.name)
        executor.execute_test_flow(data)
