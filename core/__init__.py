if __name__ == "__main__":
    # data = open("E:\\WorkSpace\\Python\\automatic_test\\.gitignore", "rb")
    # print(data.read())
    import requests

    files = {
        "file1": (
            "logo.png",  # 文件名
            open("logo.png", "rb"),  # 文件流
            "image/png",  # 请求头Content-Type字段对应的值
            {"Expires": "0"},
        )
    }
    response = requests.post("http://www.hangge.com/upload.php", files=files)
    print(response.text)
