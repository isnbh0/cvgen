import pytest

from cvgen.utils.collapse import collapse_keys


def test_simple_collapse():
    data = {"greeting": {"en": "Hello", "es": "Hola", "fr": "Bonjour"}}
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)
    assert result == {"greeting": "Hola"}


def test_nested_collapse():
    data = {
        "greeting": {"en": "Hello", "es": "Hola", "fr": "Bonjour"},
        "farewell": {"en": "Goodbye", "es": "Adiós", "fr": "Au revoir"},
    }
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "fr", config)
    assert result == {"greeting": "Bonjour", "farewell": "Au revoir"}


def test_list_collapse():
    data = [
        {"en": "Hello", "es": "Hola", "fr": "Bonjour"},
        {"en": "Goodbye", "es": "Adiós", "fr": "Au revoir"},
    ]
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)
    assert result == ["Hola", "Adiós"]


def test_default_key():
    data = {"greeting": {"en": "Hello", "fr": "Bonjour"}}
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)
    assert result == {"greeting": "Hello"}


def test_non_dict_non_list():
    data = "Hello"
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)
    assert result == "Hello"


def test_empty_dict():
    data = {}
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    with pytest.raises(ValueError):
        collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)


def test_nested_config():
    data = {
        "config": {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"},
        "greeting": {"en": "Hello", "es": "Hola", "fr": "Bonjour"},
    }
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "fr")
    assert result == {"greeting": "Bonjour"}


def test_override_config():
    data = {
        "config": {"collapsible_keys": ["en", "es", "fr", "de"], "default_key": "en"},
        "level1": {
            "config": {"collapsible_keys": ["en", "de"], "default_key": "de"},
            "greeting": {"en": "Hello", "de": "Hallo"},
        },
    }
    result = collapse_keys(data, "config", "collapsible_keys", "default_key", "de")
    assert result == {"level1": {"greeting": "Hallo"}}


def test_user_key_not_in_collapsible_keys():
    data = {"greeting": {"en": "Hello", "es": "Hola"}}
    config = {"collapsible_keys": ["en", "es"], "default_key": "en"}
    with pytest.raises(ValueError, match="user_key='fr' is not in collapsible_keys="):
        collapse_keys(data, "config", "collapsible_keys", "default_key", "fr", config)


def test_mixed_collapsible_and_non_collapsible_keys():
    data = {"greeting": {"en": "Hello", "es": "Hola", "type": "formal"}}
    config = {"collapsible_keys": ["en", "es"], "default_key": "en"}
    with pytest.raises(ValueError, match="Data contains both collapsible keys and other keys"):
        collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)


def test_missing_user_and_default_keys():
    data = {"greeting": {"fr": "Bonjour"}}
    config = {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"}
    with pytest.raises(
        ValueError,
        match="Data does not have values for either user_key='es' or default_value_key='en'",
    ):
        collapse_keys(data, "config", "collapsible_keys", "default_key", "es", config)


def test_complex_nested_structure():
    data = {
        "config": {"collapsible_keys": ["en", "es", "fr"], "default_key": "en"},
        "menu": {
            "appetizers": [
                {
                    "name": {"en": "Salad", "es": "Ensalada", "fr": "Salade"},
                    "description": {
                        "en": "Fresh garden salad",
                        "es": "Ensalada fresca del jardín",
                        "fr": "Salade fraîche du jardin",
                    },
                },
                {
                    "name": {"en": "Soup", "es": "Sopa", "fr": "Soupe"},
                    "description": {
                        "en": "Tomato soup",
                        "es": "Sopa de tomate",
                        "fr": "Soupe de tomates",
                    },
                },
            ],
            "main_courses": {
                "config": {"collapsible_keys": ["en", "de"], "default_key": "de"},
                "dish1": {"en": "Steak", "de": "Steak"},
                "dish2": {"en": "Fish", "de": "Fisch"},
            },
        },
    }
    result = collapse_keys(
        data, "config", "collapsible_keys", "default_key", "es", raise_on_missing_user_key=False
    )
    expected = {
        "menu": {
            "appetizers": [
                {"name": "Ensalada", "description": "Ensalada fresca del jardín"},
                {"name": "Sopa", "description": "Sopa de tomate"},
            ],
            "main_courses": {"dish1": "Steak", "dish2": "Fisch"},
        }
    }
    assert result == expected


def test_missing_user_key_raise_error():
    data = {"greeting": {"en": "Hello", "es": "Hola"}}
    config = {"collapsible_keys": ["en", "es"], "default_key": "en"}
    with pytest.raises(ValueError, match="user_key='fr' is not in collapsible_keys="):
        collapse_keys(
            data,
            "config",
            "collapsible_keys",
            "default_key",
            "fr",
            config,
            raise_on_missing_user_key=True,
        )


def test_missing_user_key_fallback():
    data = {"greeting": {"en": "Hello", "es": "Hola"}}
    config = {"collapsible_keys": ["en", "es"], "default_key": "en"}
    result = collapse_keys(
        data,
        "config",
        "collapsible_keys",
        "default_key",
        "fr",
        config,
        raise_on_missing_user_key=False,
    )
    assert result == {"greeting": "Hello"}
