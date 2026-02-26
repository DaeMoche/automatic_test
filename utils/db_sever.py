import pymysql
from typing import Dict
from utils.yaml_parse import load_yaml
from core.api.settings import DataSource
from pymysql import converters, FIELD_TYPE

conv = converters.conversions
conv[FIELD_TYPE.NEWDECIMAL] = float  # convert decimals to float
conv[FIELD_TYPE.DATE] = str  # convert dates to strings
conv[FIELD_TYPE.TIMESTAMP] = str  # convert dates to strings
conv[FIELD_TYPE.DATETIME] = str  # convert dates to strings
conv[FIELD_TYPE.TIME] = str  # convert dates to strings


class DBClient:
    """初始一个数据库客户端"""

    def __init__(self, file_path: str = None, dataSource: DataSource = None) -> None:
        self._config = (
            self.config(dataSource=dataSource)
            if dataSource
            else self.config(file_path=file_path)
        )
        self.connect = self._connect()
        self.cursor = self._cursor()

    def _connect(self):
        """
        数据库连接

        :param self: 说明
        """
        try:
            # print("连接数据库")
            return pymysql.connect(**self._config, conv=conv)
        except Exception as e:
            raise e

    def _cursor(self):
        """游标"""
        # print("获取游标")
        # 以字典形式返回查询结果
        return self.connect.cursor(cursor=pymysql.cursors.DictCursor)

    def close(self):
        """
        关闭数据库连接

        :param self: 说明
        """
        # print("关闭数据库连接")
        if self.connect and self.cursor:
            self.cursor.close()
            self.connect.close()
        return True

    def config(
        self,
        file_path: str = None,
        dataSource: Dict[str, DataSource] = None,
        section: str = "mysql",
    ):
        """
        获取数据库连接信息，从传递的数据源对象或者配置文件读取数据库连接信息，

        :param self: 说明
        :param file_path: 配置文件路径，不填写则报错
        :param dataSource: 数据源对象
        :type dataSource: object
        :type file_path: str
        :param section: 选择区段，默认为mysql
        :type section: str
        """
        if not dataSource:
            file_path = file_path if file_path else ValueError("文件路径不能为空！")
            conf = load_yaml(file_path).read_by_section(section=section)
            dataSource = DataSource(**conf)
        else:
            dataSource = dataSource.get(section)

        data = {
            "host": dataSource.host,
            "port": dataSource.port,
            "user": dataSource.username,
            "password": str(dataSource.password),
            "database": dataSource.database,
        }
        return data

    def insert(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as e:
            raise e
        finally:
            self.close()

    def delete(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as e:
            raise e
        finally:
            self.close()

    def update(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as e:
            raise e
        finally:
            self.close()

    def query(self, sql: str, fetchall: bool = False):
        """
        query 的 Docstring

        :param self: 说明
        :param sql: sql语句
        :type sql: str
        :param fetchall: 控制查询全部数据，默认False
        """
        try:
            self.cursor.execute(sql)
            self.connect.commit()
            return self.cursor.fetchall() if fetchall else self.cursor.fetchone()
        except Exception as e:
            raise e
        finally:
            self.close()


def db_client(dataSource: DataSource = None):
    """
    创建并初始化一个数据库客户端

    :param config: 数据库连接配置信息
    :type config: Dict[str, str]
    """
    return DBClient(dataSource=dataSource)


if __name__ == "__main__":
    cli = db_client()
    sql = "SELECT * FROM `sys_user` WHERE `sys_user`.`id` = 1 AND `sys_user`.`status` = 1;"
    res = cli.query(sql)
    print(res)
