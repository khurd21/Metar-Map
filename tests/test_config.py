import tempfile
import os
import yaml
import pytest
from metar_map.config import load_config, resources


def test_load_config_from_valid_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as tmp:
        yaml.dump({"foo": "bar", "baz": 123}, tmp)
        tmp_path = tmp.name
    try:
        config = load_config(config_path=tmp_path)
        assert config["foo"] == "bar"
        assert config["baz"] == 123
    finally:
        os.remove(tmp_path)


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config(config_path="/nonexistent/path/config.yaml")


def test_load_config_default(monkeypatch):  # type: ignore

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as tmp:
        yaml.dump({"default": True}, tmp)
        tmp_path = tmp.name

    class DummyFiles:
        def joinpath(self, _):
            return tmp_path

    monkeypatch.setattr(resources, "files", lambda _: DummyFiles())  # type: ignore
    try:
        config = load_config()
        assert config["default"] is True
    finally:
        os.remove(tmp_path)
