import pytest

from cvgen.utils.filter_by_verbosity import filter_by_verbosity


@pytest.fixture
def sample_data():
    return {
        "name": "John Doe",
        "details": {"content": {"age": 30, "occupation": "Software Engineer"}, "verbosity": 1.0},
        "skills": [
            {"content": "Python", "verbosity": 1.0},
            {"content": "JavaScript", "verbosity": 1.5},
            {"content": "Rust", "verbosity": 2.0},
        ],
        "projects": {
            "content": [
                {
                    "name": "Project A",
                    "description": {"content": "A simple web app", "verbosity": 1.0},
                    "technologies": [
                        {"content": "React", "verbosity": 1.0},
                        {"content": "Node.js", "verbosity": 1.5},
                    ],
                },
                {
                    "name": "Project B",
                    "description": {
                        "content": "An advanced machine learning model",
                        "verbosity": 2.0,
                    },
                    "technologies": [{"content": "TensorFlow", "verbosity": 2.0}],
                },
            ],
            "verbosity": 1.0,
        },
        "additional_info": {"content": "Some additional information", "verbosity": 3.0},
    }


def test_basic_filtering(sample_data):
    filtered = filter_by_verbosity(sample_data, target_verbosity=1.0)
    print(filtered)
    assert filtered["name"] == "John Doe"
    assert filtered["details"] == {"age": 30, "occupation": "Software Engineer"}
    assert filtered["skills"] == ["Python"]
    assert len(filtered["projects"]) == 2
    assert filtered["projects"][0]["name"] == "Project A"
    assert filtered["projects"][0]["description"] == "A simple web app"
    assert filtered["projects"][0]["technologies"] == ["React"]
    assert filtered["projects"][1]["name"] == "Project B"
    assert "description" not in filtered["projects"][1]
    assert len(filtered["projects"][1]["technologies"]) == 0
    assert "additional_info" not in filtered


def test_higher_verbosity(sample_data):
    filtered = filter_by_verbosity(sample_data, target_verbosity=1.5)
    assert len(filtered["skills"]) == 2
    assert "JavaScript" in filtered["skills"]
    assert "Rust" not in filtered["skills"]
    assert len(filtered["projects"][0]["technologies"]) == 2


def test_maximum_verbosity(sample_data):
    filtered = filter_by_verbosity(sample_data, target_verbosity=3.0)
    expected = {
        "name": "John Doe",
        "details": {"age": 30, "occupation": "Software Engineer"},
        "skills": ["Python", "JavaScript", "Rust"],
        "projects": [
            {
                "name": "Project A",
                "description": "A simple web app",
                "technologies": ["React", "Node.js"],
            },
            {
                "name": "Project B",
                "description": "An advanced machine learning model",
                "technologies": ["TensorFlow"],
            },
        ],
        "additional_info": "Some additional information",
    }
    assert filtered == expected


def test_minimum_verbosity(sample_data):
    filtered = filter_by_verbosity(sample_data, target_verbosity=0.5)
    expected = {
        "name": "John Doe",
        "skills": [],
    }
    assert filtered == expected


def test_empty_input():
    assert filter_by_verbosity({}) == {}
    assert filter_by_verbosity([]) == []


def test_non_dict_non_list_input():
    assert filter_by_verbosity("string") == "string"
    assert filter_by_verbosity(123) == 123
    assert filter_by_verbosity(None) is None


def test_missing_verbosity():
    data = {"content": "test", "unrelated": "value"}
    assert (
        filter_by_verbosity(
            data,
            should_unwrap=False,  # FIXME: this is a hack to simulate ignoring missing verbosity
        )
        == data
    )


def test_missing_content():
    data = {"verbosity": 1.0, "unrelated": "value"}
    assert filter_by_verbosity(data) == data


def test_custom_keys():
    data = {
        "filter_config": {"content_key": "data", "verbosity_key": "level"},
        "item": {"data": "Custom key test", "level": 1.0},
    }
    filtered = filter_by_verbosity(data)
    print(filtered)
    assert filtered == {"item": "Custom key test"}


def test_nested_config():
    data = {
        "outer": {
            "filter_config": {"content_key": "data", "verbosity_key": "level"},
            "item": {"data": "Nested config test", "level": 1.0},
        }
    }
    filtered = filter_by_verbosity(data)
    assert filtered == {"outer": {"item": "Nested config test"}}


def test_list_filtering():
    data = [
        {"content": "Item 1", "verbosity": 1.0},
        {"content": "Item 2", "verbosity": 2.0},
        {"content": "Item 3", "verbosity": 1.5},
    ]
    filtered = filter_by_verbosity(data, target_verbosity=1.5)
    assert filtered == ["Item 1", "Item 3"]


def test_empty_structures_remain():
    data = {"empty_list": [], "empty_dict": {}, "non_empty": {"content": "value", "verbosity": 1.0}}
    filtered = filter_by_verbosity(data)
    expected = {"empty_list": [], "empty_dict": {}, "non_empty": "value"}
    assert filtered == expected


def test_float_verbosity():
    data = [
        {"content": "Item 1", "verbosity": 1.0},
        {"content": "Item 2", "verbosity": 1.1},
        {"content": "Item 3", "verbosity": 1.5},
    ]
    filtered = filter_by_verbosity(data, target_verbosity=1.2)
    assert filtered == ["Item 1", "Item 2"]


def test_config_override():
    data = {
        "filter_config": {"content_key": "data", "verbosity_key": "level"},
        "item1": {"data": "Test 1", "level": 1.0},
        "item2": {
            "filter_config": {"content_key": "info", "verbosity_key": "priority"},
            "info": "Test 2",
            "priority": 1.0,
        },
    }
    filtered = filter_by_verbosity(data)
    assert filtered == {"item1": "Test 1", "item2": "Test 2"}


def test_verbosity_edge_cases():
    data = [
        {"content": "Zero", "verbosity": 0},
        {"content": "Negative", "verbosity": -1},
        {"content": "Very large", "verbosity": 1e10},
        {"content": "Infinity", "verbosity": float("inf")},
    ]
    filtered = filter_by_verbosity(data, target_verbosity=1.0)
    assert filtered == ["Zero", "Negative"]


def test_with_other_keys():
    data = {
        "stuff": [
            {
                "content": "Test",
                "tags": ["a", "b", "c"],
                "verbosity": 1.0,
            },
            {
                "content": "Test 2",
                "tags": ["a", "b"],
                "verbosity": 1.5,
            },
        ]
    }

    filtered = filter_by_verbosity(data, target_verbosity=1.1, should_unwrap=False)
    assert filtered == {
        "stuff": [
            {
                "content": "Test",
                "tags": ["a", "b", "c"],
                "verbosity": 1.0,
            },
        ]
    }
