import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

import yaml


class YAMLHandler(ABC):
    @abstractmethod
    def load_from_file(self, file_path: Path) -> Dict:
        pass

    @abstractmethod
    def load_from_string(self, content: str) -> Dict:
        pass

    @abstractmethod
    def dump_to_string(self, data: Dict) -> str:
        pass

    @abstractmethod
    def dump_to_file(self, data: Dict, file_path: Path) -> None:
        pass


class PyYAMLHandler(YAMLHandler):
    def load_from_file(self, file_path: Path) -> Dict:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def load_from_string(self, content: str) -> Dict:
        return yaml.safe_load(content)

    def dump_to_string(self, data: Dict) -> str:
        return yaml.dump(data, allow_unicode=True, sort_keys=False)

    def dump_to_file(self, data: Dict, file_path: Path) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True, sort_keys=False)


def get_yaml_handler() -> YAMLHandler:
    return PyYAMLHandler()
