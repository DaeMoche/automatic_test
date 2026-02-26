import os
import pytest
from pathlib import Path
from configs import configure
from core.api.core import Request
from core.api.executor import Executor
from utils.yaml_parse import read_yaml
from core.api.settings import Configuration
from utils.allure_reports import CustomAllure


# 注册自定义标记
def pytest_configure(config):

    config.addinivalue_line("markers", "demo: demo标记.")
    config.addinivalue_line("markers", "env(name): 环境标记.")
    config.addinivalue_line("markers", "data(file): 数据标记.")


# 设置环境变量
@pytest.fixture(scope="session")
def env(request):
    """设置环境"""
    environment = request.config.getoption("-E", default="local")

    config = read_yaml(configure.settings).get(environment)

    CustomAllure.attach(config, f"读取配置文件设置环境: {environment}", "json")

    return Configuration(**config)


# 定义测试夹具
@pytest.fixture(scope="session")
def api(env):

    # 加载变量
    req = Request(base_url=env.server.url)

    # 设置环境变量
    req.context.variables.setdefault("data-source", env.data_source.copy())

    CustomAllure.attach(env, "初始化配置配置", "json")

    return req


# 定义执行器夹具
@pytest.fixture(scope="session")
def executor(api, request):
    """流程执行器fixtrequesture"""
    print("\r\n====== Setup ==========")

    # 定义终结函数
    def tear_down():

        # 清理
        api.context.session.close()
        api.context.variables.clear()

        CustomAllure.attach("执行器资源释放完成", "执行器资源释放完成", "txt")

        print("\r\n====== Teardown =======")

    # 注册终结函数
    request.addfinalizer(tear_down)

    CustomAllure.attach("执行器初始化完成", "初始化执行器", "txt")

    return Executor(request=api)


# 添加命令行选项
def pytest_addoption(parser):
    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        default="test",
        help="only run test matching the environment NAME.",
    )


# 根据环境变量跳过测试
def pytest_runtest_setup(item):
    env = [mark.args[0] for mark in item.iter_markers(name="env")]
    if env:
        if item.config.getoption("-E") not in env:
            pytest.skip(f"test requires env in {env!r}")


# 根据标记动态读取测试用例文件，并自动收集
def pytest_generate_tests(metafunc):
    """根据 @pytest.mark.data('<file>') 在收集阶段动态参数化测试用例

    当测试或类上使用了 `@pytest.mark.data('case')` 时，读取 `tests/test_data/case.yml` 或
    `case.yaml` 并把读取到的列表传给 `parametrize("data", dataset)`。
    """
    data_mark = getattr(metafunc.definition, "get_closest_marker", None)
    if not data_mark:
        return

    marker = metafunc.definition.get_closest_marker("data")
    if not marker:
        return

    # 只有当测试函数需要名为 "data" 的夹具/参数时才进行参数化
    if "data" not in metafunc.fixturenames:
        return

    data_file = marker.args[0] if marker.args else None
    data_path = Path(__file__).parent / "tests" / "test_data" / f"{data_file}"

    data_file_candidate = (
        f"{data_path}.yml"
        if os.path.exists(f"{data_path}.yml")
        else f"{data_path}.yaml" if os.path.exists(f"{data_path}.yaml") else None
    )

    if not data_file_candidate:
        metafunc.parametrize("data", [])
        return

    dataset = read_yaml(data_file_candidate) or []
    metafunc.parametrize("data", dataset)
