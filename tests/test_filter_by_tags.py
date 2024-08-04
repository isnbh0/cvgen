import pytest

from cvgen.utils.filter_by_tags import filter_by_tags

# Test data
simple_dict = {"content": "Hello", "tags": ["greeting", "english"]}

nested_dict = {
    "level1": {
        "tags": ["nested", "deep"],
        "content": {
            "level2": {
                "content": "Double nested",
                "tags": ["double", "nested"],
            }
        },
    },
    "tags": ["top", "level"],
}

list_of_dicts = [
    {"content": "Item 1", "tags": ["a", "b"]},
    {"content": "Item 2", "tags": ["b", "c"]},
    {"content": "Item 3", "tags": ["c", "d"]},
]

custom_config = {
    "filter_config": {"content_key": "data", "tags_key": "labels"},
    "data": "Custom content",
    "labels": ["custom", "config"],
}


# Test cases
def test_simple_include():
    result = filter_by_tags(simple_dict, include_tags=["greeting"])
    assert result == "Hello"


def test_simple_exclude():
    result = filter_by_tags(simple_dict, exclude_tags=["french"])
    assert result == "Hello"


def test_simple_exclude_match():
    result = filter_by_tags(simple_dict, exclude_tags=["english"])
    assert result is None


def test_nested_include():
    result = filter_by_tags(nested_dict, include_tags=["nested"])
    assert "level1" in result
    assert "level2" in result["level1"]


def test_nested_exclude():
    result = filter_by_tags(nested_dict, exclude_tags=["double"])
    assert "level1" in result
    assert "level2" not in result["level1"]


def test_list_of_dicts():
    result = filter_by_tags(list_of_dicts, include_tags=["b"])
    assert len(result) == 2
    assert result[0] == "Item 1"
    assert result[1] == "Item 2"


def test_include_all():
    result = filter_by_tags(list_of_dicts, include_tags=["b", "c"], include_mode="all")
    assert len(result) == 1
    assert result[0] == "Item 2"


def test_exclude_all():
    result = filter_by_tags(list_of_dicts, exclude_tags=["a", "d"], exclude_mode="all")
    print(result)
    assert len(result) == 3  # No item has both 'a' and 'd'


def test_include_exclude_combination():
    result = filter_by_tags(list_of_dicts, include_tags=["b"], exclude_tags=["a"])
    assert len(result) == 1
    assert result[0] == "Item 2"


def test_custom_config():
    result = filter_by_tags(custom_config, include_tags=["custom"])
    assert result == "Custom content"


def test_empty_include_tags():
    result = filter_by_tags(simple_dict, include_tags=[])
    assert result is None


def test_empty_exclude_tags():
    result = filter_by_tags(simple_dict, exclude_tags=[])
    assert result == "Hello"


def test_include_all_but():
    result = filter_by_tags(list_of_dicts, exclude_tags=["a"])
    assert len(result) == 2
    assert result[0] == "Item 2"
    assert result[1] == "Item 3"


def test_exclude_all_but():
    result = filter_by_tags(list_of_dicts, include_tags=["a", "b"], include_mode="any")
    assert len(result) == 2
    assert result[0] == "Item 1"
    assert result[1] == "Item 2"


def test_exclude_all_but_include_mode_all():
    result = filter_by_tags(list_of_dicts, include_tags=["a", "b"], include_mode="all")
    assert len(result) == 1
    assert result[0] == "Item 1"


def test_non_list_tags():
    dict_with_string_tag = {"content": "String tag", "tags": "single"}
    result = filter_by_tags(dict_with_string_tag, include_tags=["single"])
    assert result == "String tag"


def test_missing_tags():
    dict_without_tags = {"content": "No tags"}
    result = filter_by_tags(
        dict_without_tags,
        include_tags=["any"],
        should_unwrap=False,  # FIXME: this is a hack to simulate ignoring missing tags
    )
    assert result == dict_without_tags


def test_nested_config_override():
    nested_with_config = {
        "filter_config": {"tags_key": "labels"},
        "data": {"content": "Nested with config", "labels": ["nested", "config"]},
    }
    result = filter_by_tags(nested_with_config, include_tags=["config"])
    print(result)
    assert result["data"] == "Nested with config"


def test_include_exclude_none():
    result = filter_by_tags(simple_dict)
    assert result == "Hello"


@pytest.mark.parametrize("mode", ["any", "all"])
def test_include_mode(mode):
    data = {"content": "Test", "tags": ["a", "b", "c"]}
    result = filter_by_tags(data, include_tags=["a", "d"], include_mode=mode)
    assert (result is not None) == (mode == "any")


@pytest.mark.parametrize("mode", ["any", "all"])
def test_exclude_mode(mode):
    data = {"content": "Test", "tags": ["a", "b", "c"]}
    result = filter_by_tags(data, exclude_tags=["a", "d"], exclude_mode=mode)
    assert (result is None) == (mode == "any")


def test_invalid_include_mode():
    with pytest.raises(ValueError):
        filter_by_tags(simple_dict, include_tags=["a"], include_mode="invalid")


def test_invalid_exclude_mode():
    with pytest.raises(ValueError):
        filter_by_tags(simple_dict, exclude_tags=["a"], exclude_mode="invalid")


def test_deep_nested_structure():
    deep_nested = {"l1": {"l2": {"l3": {"content": "Deep", "tags": ["deep"]}}}}
    result = filter_by_tags(deep_nested, include_tags=["deep"])
    assert result["l1"]["l2"]["l3"] == "Deep"


def test_mixed_data_types():
    mixed_data = {
        "dict": {"content": "Dict", "tags": ["dict"]},
        "list": [{"content": "List1", "tags": ["list"]}, {"content": "List2", "tags": ["list"]}],
        "string": "Just a string",
        "number": 42,
    }
    result = filter_by_tags(mixed_data, include_tags=["list"])
    assert "dict" not in result
    assert len(result["list"]) == 2
    assert "string" in result
    assert "number" in result


def test_empty_data():
    assert filter_by_tags({}) == {}
    assert filter_by_tags([]) == []


def test_none_data():
    assert filter_by_tags(None) is None


# Add more tests as needed
