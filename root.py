import os
import sys

# 项目根路径
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_PATH)


FILE_PATH = {}

if __name__ == "__main__":
    print(ROOT_PATH)
    print(
        os.path.exists(
            "E:\\WorkSpace\\Python\\pytest-demo\\configs\\dbconfig\\config.yaml"
        )
    )
