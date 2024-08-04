from typing import Any, Dict, Optional

from cvgen.utils.unwrap import unwrap_content


def filter_by_verbosity(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    verbosity_key: str = "verbosity",
    target_verbosity: float = 1.0,
    config: Optional[Dict[str, Any]] = None,
    should_unwrap: bool = True,
) -> Any:
    filtered = _filter_by_verbosity(
        data, config_key, content_key, verbosity_key, target_verbosity, config
    )

    print(f"{filtered=}")
    if should_unwrap:
        # FIXME: there is no way to check if the data was valid for filtering
        return unwrap_content(filtered)
    return filtered


def _filter_by_verbosity(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    verbosity_key: str = "verbosity",
    target_verbosity: float = 1.0,
    config: Optional[Dict[str, Any]] = None,
) -> Any:
    if config is None:
        config = {}

    if isinstance(data, dict):
        if config_key in data:
            new_config = data[config_key]
            config = {**config, **new_config}

        local_content_key = config.get("content_key", content_key)
        local_verbosity_key = config.get("verbosity_key", verbosity_key)

        if local_content_key in data and local_verbosity_key in data:
            if data[local_verbosity_key] <= target_verbosity:
                filtered_content = _filter_by_verbosity(
                    data[local_content_key],
                    config_key,
                    local_content_key,
                    local_verbosity_key,
                    target_verbosity,
                    config,
                )
                return {**data, local_content_key: filtered_content}
            else:
                return None

        filtered = {}
        for k, v in data.items():
            filtered_v = _filter_by_verbosity(
                v, config_key, local_content_key, local_verbosity_key, target_verbosity, config
            )
            if filtered_v is not None:
                filtered[k] = filtered_v
        return filtered

    elif isinstance(data, list):
        filtered = [
            filtered_item
            for item in data
            if (
                filtered_item := _filter_by_verbosity(
                    item, config_key, content_key, verbosity_key, target_verbosity, config
                )
            )
            is not None
        ]
        return filtered

    else:
        return data
