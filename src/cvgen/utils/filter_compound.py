from typing import Any, Dict, List, Optional

from cvgen.utils.filter_by_tags import _filter_by_tags
from cvgen.utils.filter_by_verbosity import _filter_by_verbosity
from cvgen.utils.unwrap import unwrap_content


def filter_compound(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    verbosity_key: str = "verbosity",
    tags_key: str = "tags",
    target_verbosity: float = 1.0,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    include_mode: str = "any",
    exclude_mode: str = "any",
    config: Optional[Dict[str, Any]] = None,
    should_unwrap: bool = True,
) -> Any:
    filtered = _filter_compound(
        data,
        config_key,
        content_key,
        verbosity_key,
        tags_key,
        target_verbosity,
        include_tags,
        exclude_tags,
        include_mode,
        exclude_mode,
        config,
    )

    if should_unwrap:
        return unwrap_content(filtered)
    return filtered


def _filter_compound(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    verbosity_key: str = "verbosity",
    tags_key: str = "tags",
    target_verbosity: float = 1.0,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    include_mode: str = "any",
    exclude_mode: str = "any",
    config: Optional[Dict[str, Any]] = None,
) -> Any:
    if config is None:
        config = {}

    def apply_filters(item: Any) -> Any:
        # Apply verbosity filter
        filtered_by_verbosity = _filter_by_verbosity(
            item, config_key, content_key, verbosity_key, target_verbosity, config
        )

        if filtered_by_verbosity is None:
            return None

        # Apply tags filter
        filtered_by_tags = _filter_by_tags(
            filtered_by_verbosity,
            config_key,
            content_key,
            tags_key,
            include_tags,
            exclude_tags,
            include_mode,
            exclude_mode,
            config,
        )

        return filtered_by_tags

    if isinstance(data, dict):
        if config_key in data:
            new_config = data[config_key]
            config = {**config, **new_config}

        local_content_key = config.get("content_key", content_key)

        if local_content_key in data:
            filtered_content = apply_filters(data)
            if filtered_content is None:
                return None
            return filtered_content

        filtered = {}
        for k, v in data.items():
            if k != config_key:
                filtered_v = _filter_compound(
                    v,
                    config_key,
                    content_key,
                    verbosity_key,
                    tags_key,
                    target_verbosity,
                    include_tags,
                    exclude_tags,
                    include_mode,
                    exclude_mode,
                    config,
                )
                if filtered_v is not None:
                    filtered[k] = filtered_v
        return filtered

    elif isinstance(data, list):
        filtered = [
            filtered_item
            for item in data
            if (
                filtered_item := _filter_compound(
                    item,
                    config_key,
                    content_key,
                    verbosity_key,
                    tags_key,
                    target_verbosity,
                    include_tags,
                    exclude_tags,
                    include_mode,
                    exclude_mode,
                    config,
                )
            )
            is not None
        ]
        return filtered

    else:
        return data
