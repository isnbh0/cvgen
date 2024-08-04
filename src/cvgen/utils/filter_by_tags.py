from typing import Any, Dict, List, Optional, Union

from cvgen.utils.unwrap import unwrap_content


def filter_by_tags(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    tags_key: str = "tags",
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    include_mode: str = "any",
    exclude_mode: str = "any",
    config: Optional[Dict[str, Any]] = None,
    should_unwrap: bool = True,
) -> Any:
    filtered = _filter_by_tags(
        data,
        config_key,
        content_key,
        tags_key,
        include_tags,
        exclude_tags,
        include_mode,
        exclude_mode,
        config,
    )

    if should_unwrap:
        # FIXME: there is no way to check if the data was valid for filtering
        return unwrap_content(filtered)
    return filtered


def _filter_by_tags(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    tags_key: str = "tags",
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    include_mode: str = "any",
    exclude_mode: str = "any",
    config: Optional[Dict[str, Any]] = None,
) -> Any:
    if config is None:
        config = {}

    if isinstance(data, dict):
        if config_key in data:
            new_config = data[config_key]
            config = {**config, **new_config}

        local_content_key = config.get("content_key", content_key)
        local_tags_key = config.get("tags_key", tags_key)

        if local_content_key in data and local_tags_key in data:
            item_tags = data[local_tags_key]
            if should_include(item_tags, include_tags, exclude_tags, include_mode, exclude_mode):
                filtered_content = _filter_by_tags(
                    data[local_content_key],
                    config_key,
                    local_content_key,
                    local_tags_key,
                    include_tags,
                    exclude_tags,
                    include_mode,
                    exclude_mode,
                    config,
                )
                return {**data, local_content_key: filtered_content}
            else:
                return None

        filtered = {}
        for k, v in data.items():
            if k != config_key:
                filtered_v = _filter_by_tags(
                    v,
                    config_key,
                    local_content_key,
                    local_tags_key,
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
                filtered_item := _filter_by_tags(
                    item,
                    config_key,
                    content_key,
                    tags_key,
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


def should_include(
    item_tags: Union[List[str], str],
    include_tags: Optional[List[str]],
    exclude_tags: Optional[List[str]],
    include_mode: str,
    exclude_mode: str,
) -> bool:
    if isinstance(item_tags, str):
        item_tags = [item_tags]

    if include_tags is None and exclude_tags is None:
        return True

    result: Optional[bool] = None

    if include_tags is not None:
        result = False if result is None else result
        if include_mode == "all":
            result |= all(tag in item_tags for tag in include_tags)
        elif include_mode == "any":
            result |= any(tag in item_tags for tag in include_tags)
        else:
            raise ValueError("Invalid include_mode. Use 'any' or 'all'.")

    if exclude_tags is not None:
        result = True if result is None else result
        if exclude_mode == "all":
            result &= any(tag not in item_tags for tag in exclude_tags)
        elif exclude_mode == "any":
            result &= all(tag not in item_tags for tag in exclude_tags)
        else:
            raise ValueError("Invalid exclude_mode. Use 'any' or 'all'.")

    return result
