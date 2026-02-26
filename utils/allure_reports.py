from dataclasses import asdict
import json
import yaml
import allure
from typing import Any
from allure import attachment_type

from core.api.settings import DataSource


class CustomAllure:
    @classmethod
    def attach(cls, body: Any, name: str, _type: str):
        """
        attach 的 Docstring

        :param body: 展示信息
        :type body: Any
        :param name: 名称
        :type name: str
        :param _type: 报告展示类型 ['txt','json','yaml']
        :type _type: str
        """

        body = cls._trans_to_yaml(body) if _type == "yaml" else cls._trans_to_str(body)

        match _type:
            case "txt":
                _type = attachment_type.TEXT
            case "json":
                _type = attachment_type.JSON
            case "yaml":
                _type = attachment_type.YAML
            case _:
                _type = attachment_type.TEXT

        allure.attach(body=body, name=name, attachment_type=_type)

    @classmethod
    def _trans_to_str(cls, data: Any) -> str:
        if isinstance(data, dict):
            data = cls._trans_to_dict(data)
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif isinstance(data, str):
            return data
        else:
            return str(data)

    @classmethod
    def _trans_to_dict(cls, data: Any):
        if isinstance(data, (dict, DataSource)):

            if isinstance(data, DataSource):
                return asdict(data)

            for k, v in data.items():
                if isinstance(v, DataSource):
                    v = asdict(v)
                elif isinstance(v, dict):
                    v = cls._trans_to_dict(v)
                else:
                    pass

                data[k] = v

        return data

    @classmethod
    def _trans_to_yaml(cls, data: Any):
        # 返回字符串（保证 unicode 可读），如果传入已经是字符串则直接返回
        if isinstance(data, str):
            return data
        try:
            return yaml.safe_dump(
                data,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
            )
        except Exception:
            return cls._trans_to_str(data)
