from typing import Any

import pytest

from cvgen.utils.filter_compound import filter_compound


@pytest.fixture
def sample_data():
    return {
        "level1": {
            "content": {
                "level2a": {
                    "content": "This is level 2a content",
                    "verbosity": 0.5,
                    "tags": ["important", "short"],
                },
                "level2b": {
                    "content": "This is level 2b content",
                    "verbosity": 1.5,
                    "tags": ["verbose", "detailed"],
                },
            },
            "verbosity": 1.0,
            "tags": ["top-level", "important", "short"],
        },
        "level1_list": [
            {"content": "List item 1", "verbosity": 0.8, "tags": ["list", "short"]},
            {"content": "List item 2", "verbosity": 1.2, "tags": ["list", "medium"]},
        ],
        "simple_key": "simple_value",
    }


def test_filter_compound_basic(sample_data: dict[str, Any]):
    result = filter_compound(sample_data, target_verbosity=1.0)
    assert "level1" in result
    assert "level2a" in result["level1"]
    assert "level2b" not in result["level1"]
    assert len(result["level1_list"]) == 1
    assert result["level1_list"][0] == "List item 1"
    assert "simple_key" in result


def test_filter_compound_strict_verbosity(sample_data: dict[str, Any]):
    result = filter_compound(sample_data, target_verbosity=0.7)
    assert "level1" not in result
    assert len(result["level1_list"]) == 0
    assert "simple_key" in result


def test_filter_compound_include_tags(sample_data: dict[str, Any]):
    result = filter_compound(sample_data, target_verbosity=2.0, include_tags=["important"])
    assert "level2a" in result["level1"]
    assert "level2b" not in result["level1"]
    assert "level1_list" in result
    assert len(result["level1_list"]) == 0


def test_filter_compound_exclude_tags(sample_data: dict[str, Any]):
    result = filter_compound(sample_data, target_verbosity=2.0, exclude_tags=["verbose"])
    assert "level2a" in result["level1"]
    assert "level2b" not in result["level1"]


def test_filter_compound_include_exclude_tags(sample_data: dict[str, Any]):
    result = filter_compound(
        sample_data, target_verbosity=2.0, include_tags=["short"], exclude_tags=["list"]
    )
    assert "level2a" in result["level1"]
    assert "level1_list" in result
    assert len(result["level1_list"]) == 0


def test_filter_compound_empty_result():
    data = {"content": "test", "verbosity": 2.0, "tags": ["exclude_me"]}
    result = filter_compound(data, target_verbosity=1.0, exclude_tags=["exclude_me"])
    assert result is None


def test_filter_compound_nested_config():
    data = {
        "filter_config": {"content_key": "nested_content", "verbosity_key": "nested_verbosity"},
        "nested_content": {
            "item": {"nested_content": "Deep content", "nested_verbosity": 0.5, "tags": ["nested"]}
        },
    }
    result = filter_compound(data, target_verbosity=1.0, include_tags=["nested"])
    assert result["nested_content"]["item"]["nested_content"] == "Deep content"


def test_filter_compound_list_input():
    data = [
        {"content": "Item 1", "verbosity": 0.5, "tags": ["keep"]},
        {"content": "Item 2", "verbosity": 1.5, "tags": ["remove"]},
        {"content": "Item 3", "verbosity": 0.8, "tags": ["keep"]},
    ]
    result = filter_compound(data, target_verbosity=1.0, include_tags=["keep"])
    assert len(result) == 2
    assert result[0] == "Item 1"
    assert result[1] == "Item 3"


def test_filter_compound_empty_input():
    assert filter_compound({}) == {}
    assert filter_compound([]) == []
    assert filter_compound(None) is None


def test_filter_compound_non_dict_non_list_input():
    assert filter_compound("string") == "string"
    assert filter_compound(42) == 42


def test_filter_compound_include_mode_all(sample_data: dict[str, Any]):
    result = filter_compound(
        sample_data, target_verbosity=2.0, include_tags=["important", "short"], include_mode="all"
    )
    assert "level2a" in result["level1"]
    assert "level2b" not in result["level1"]
    assert "level1_list" in result
    assert len(result["level1_list"]) == 0


def test_filter_compound_exclude_mode_all(sample_data: dict[str, Any]):
    result = filter_compound(
        sample_data, target_verbosity=2.0, exclude_tags=["verbose", "detailed"], exclude_mode="all"
    )
    assert "level2a" in result["level1"]
    assert "level2b" not in result["level1"]

    result = filter_compound(
        sample_data,
        target_verbosity=2.0,
        exclude_tags=["verbose", "detailed", "poop"],
        exclude_mode="all",
    )
    assert "level2a" in result["level1"]
    assert "level2b" in result["level1"]


def test_filter_compound_invalid_include_mode(sample_data: dict[str, Any]):
    with pytest.raises(ValueError):
        filter_compound(
            sample_data,
            target_verbosity=2.0,
            include_tags=["important", "short"],
            include_mode="invalid",
        )


def test_filter_compound_invalid_exclude_mode(sample_data: dict[str, Any]):
    with pytest.raises(ValueError):
        filter_compound(
            sample_data,
            target_verbosity=2.0,
            exclude_tags=["important", "short"],
            exclude_mode="invalid",
        )


def test_filter_compound_preserve_structure(sample_data: dict[str, Any]):
    result = filter_compound(sample_data, target_verbosity=2.0)
    assert isinstance(result["level1"], dict)
    assert isinstance(result["level1"], dict)
    assert isinstance(result["level1_list"], list)


def test_filter_compound_no_tags_key():
    # FIXME: need to define behavior for missing tags key
    data = {"content": {"item": "value"}, "verbosity": 0.5}
    result = filter_compound(data, target_verbosity=1.0, include_tags=["non-existent"])
    assert result == {"item": "value"}


def test_filter_compound_no_verbosity_key():
    data = {"content": {"item": "value"}, "tags": ["keep"]}
    result = filter_compound(data, target_verbosity=1.0, include_tags=["keep"])
    assert result == {"item": "value"}


def test_filter_compound_custom_keys():
    data = {
        "filter_config": {
            "content_key": "custom_content",
            "verbosity_key": "custom_verbosity",
            "tags_key": "custom_tags",
        },
        "custom_content": {
            "item": {
                "custom_content": "Custom content",
                "custom_verbosity": 0.5,
                "custom_tags": ["custom"],
            }
        },
    }
    result = filter_compound(
        data,
        target_verbosity=1.0,
        include_tags=["custom"],
        content_key="custom_content",
        verbosity_key="custom_verbosity",
        tags_key="custom_tags",
    )
    assert result["custom_content"]["item"]["custom_content"] == "Custom content"
