from dataclasses import dataclass
from typing import Dict
from utils.yaml_parse import read_yaml


@dataclass
class Server:
    """API server settings"""

    host: str
    port: int

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"


@dataclass
class DataSource:
    """Database server settings"""

    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass
class Configuration:
    server: Server
    data_source: Dict[str, DataSource]

    def __post_init__(self):
        self.server = Server(**self.server)
        # self.data_source = DataSource(**self.data_source)

        converted: Dict[str, DataSource] = {}
        for k, v in self.data_source.items():
            if isinstance(v, dict):
                converted.setdefault(k, DataSource(**v))
            else:
                converted.setdefault(k, v)

        self.data_source = converted


if __name__ == "__main__":
    data = read_yaml("configs\\settings.yaml")
    config = Configuration(**data.get("local"))
    print(f"config: {config}")
