from typing import Any, Dict, Optional


def unwrap_content(
    data: Any,
    config_key: str = "filter_config",
    content_key: str = "content",
    config: Optional[Dict[str, Any]] = None,
) -> Any:
    if config is None:
        config = {}

    if isinstance(data, dict):
        if config_key in data:
            new_config = data[config_key]
            config = {**config, **new_config}

        local_content_key = config.get("content_key", content_key)

        if local_content_key in data:
            return unwrap_content(
                data[local_content_key],
                config_key,
                local_content_key,
                config,
            )

        unwrapped = {}
        for k, v in data.items():
            if k != config_key:
                unwrapped[k] = unwrap_content(v, config_key, local_content_key, config)
        return unwrapped

    elif isinstance(data, list):
        return [unwrap_content(item, config_key, content_key, config) for item in data]

    else:
        return data
