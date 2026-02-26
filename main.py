import os

# import shutil
import pytest

if __name__ == "__main__":
    pytest.main()
    # shutil.copy()

# allure version = 2.23.0
os.system("allure generate ./report/allure-results -c -o ./report/allure2-report")
os.system("allure open ./report/allure2-report")

# allure version >= 3.0.0
# os.system("cd allure3 && npx allure generate ../report/allure-results -o ../report/allure3-report")
# os.system("cd allure3 && npx allure open ../report/allure3-report")
