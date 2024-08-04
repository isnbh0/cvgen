from typing import Any, Dict, Optional


def collapse_keys(
    data: Any,
    config_key: str,
    keys_key: str,
    default_key: str,
    user_key: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    raise_on_missing_user_key: bool = True,
) -> Any:
    if config is None:
        config = {}

    if isinstance(data, dict):
        # Check if there's a new config at this level
        if config_key in data:
            new_config = data[config_key]
            # Merge the new config with the existing one, prioritizing the new values
            config = {**config, **new_config}

        collapsible_keys = config.get(keys_key, [])
        default_value_key = config.get(default_key)

        if user_key and collapsible_keys and user_key not in collapsible_keys:
            if raise_on_missing_user_key:
                raise ValueError(
                    f"{user_key=} is not in {collapsible_keys=}. Please add it to {keys_key=}"
                )
            else:
                user_key = default_value_key

        if set(data.keys()).intersection(set(collapsible_keys)) and set(data.keys()) - set(
            collapsible_keys
        ):
            raise ValueError(
                f"Data contains both collapsible keys and other keys: {data.keys()=}, {collapsible_keys=}"
            )

        if set(data.keys()).issubset(set(collapsible_keys)):
            if user_key and user_key in data:
                return data[user_key]
            elif default_value_key and default_value_key in data:
                return data[default_value_key]
            else:
                raise ValueError(
                    f"Data does not have values for either {user_key=} or {default_value_key=}: {data=}"
                )

        return {
            k: collapse_keys(
                v, config_key, keys_key, default_key, user_key, config, raise_on_missing_user_key
            )
            for k, v in data.items()
            if k != config_key
        }
    elif isinstance(data, list):
        return [
            collapse_keys(
                item, config_key, keys_key, default_key, user_key, config, raise_on_missing_user_key
            )
            for item in data
        ]
    else:
        return data
