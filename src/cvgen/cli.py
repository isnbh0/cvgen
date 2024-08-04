import sys
from pathlib import Path
from typing import Dict, List, Optional

import typer
import yaml
from deepdiff import DeepDiff
from pydantic import BaseModel, Field

from cvgen.utils.collapse import collapse_keys
from cvgen.utils.filter_compound import filter_compound


class CollapseConfig(BaseModel):
    config_key: str = Field(
        default="multi_lang_config",
        description="Name of the key that contains the collapsing configuration",
    )
    keys_key: str = Field(
        default="lang_keys",
        description="Name of the key within the config that specifies the collapsible keys",
    )
    default_key: str = Field(
        default="default_lang",
        description="Name of the key within the config that specifies the default key to use",
    )
    user_key: Optional[str] = Field(
        default=None,
        description="Name of the key within the config that specifies the user's selected language",
    )


class FilterConfig(BaseModel):
    config_key: str = Field(
        default="filter_config",
        description="Name of the key that contains the filtering configuration",
    )
    content_key: str = Field(
        default="content", description="Name of the key that contains the content to be filtered"
    )
    verbosity_key: str = Field(
        default="verbosity", description="Name of the key that specifies the verbosity level"
    )
    target_verbosity: float = Field(default=1.0, description="Target verbosity level for filtering")
    tags_key: str = Field(
        default="tags", description="Name of the key that specifies the tags for filtering"
    )
    include_tags: Optional[List[str]] = Field(default=None, description="List of tags to include")
    exclude_tags: Optional[List[str]] = Field(default=None, description="List of tags to exclude")
    include_mode: str = Field(default="any", description="Mode for including tags")
    exclude_mode: str = Field(default="any", description="Mode for excluding tags")


class CompareResult(BaseModel):
    is_equal: bool
    diff: Dict


def filter_yaml(data: Dict, config: FilterConfig) -> Dict:
    return filter_compound(
        data=data,
        config_key=config.config_key,
        content_key=config.content_key,
        verbosity_key=config.verbosity_key,
        target_verbosity=config.target_verbosity,
        tags_key=config.tags_key,
        include_tags=config.include_tags,
        exclude_tags=config.exclude_tags,
        include_mode=config.include_mode,
        exclude_mode=config.exclude_mode,
    )


def collapse_yaml(data: Dict, config: CollapseConfig) -> Dict:
    return collapse_keys(
        data=data,
        config_key=config.config_key,
        keys_key=config.keys_key,
        default_key=config.default_key,
        user_key=config.user_key,
    )


def load_yaml(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def compare_yaml_files(file1: Path, file2: Path) -> CompareResult:
    data1 = load_yaml(str(file1))
    data2 = load_yaml(str(file2))
    if data1 == data2:
        return CompareResult(is_equal=True, diff={})
    else:
        diff = DeepDiff(data1, data2, view="tree")
        return CompareResult(is_equal=False, diff=diff)


def load_yaml_from_file_or_stdin(file_path: Optional[Path]) -> Dict:
    if file_path is None or str(file_path) == "-":
        # Read from stdin if no file path is provided or if it's '-'
        return yaml.safe_load(sys.stdin)
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)


def compare_yaml_content(data1: Dict, data2: Dict) -> CompareResult:
    if data1 == data2:
        return CompareResult(is_equal=True, diff={})
    else:
        diff = DeepDiff(data1, data2, view="tree")
        return CompareResult(is_equal=False, diff=diff)


def output_yaml(processed_dict: Dict, output_file: Optional[Path]):
    processed_yaml = yaml.dump(processed_dict, allow_unicode=True, sort_keys=False)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(processed_yaml)
        typer.echo(f"Processed YAML has been written to {output_file}")
    else:
        typer.echo(processed_yaml)


app = typer.Typer()


@app.command("filter")
def filter_command(
    input_file: Optional[Path] = typer.Argument(
        None, help="Path to the input YAML file (or use stdin if not provided or '-')"
    ),
    config_key: str = typer.Option(
        "filter_config", help="Name of the key that contains the filtering configuration"
    ),
    content_key: str = typer.Option(
        "content", help="Name of the key that contains the content to be filtered"
    ),
    verbosity_key: str = typer.Option(
        "verbosity", help="Name of the key that specifies the verbosity level"
    ),
    target_verbosity: float = typer.Option(1.0, help="Target verbosity level for filtering"),
    tags_key: str = typer.Option(
        "tags", help="Name of the key that specifies the tags for filtering"
    ),
    include_tags: Optional[List[str]] = typer.Option(None, help="List of tags to include"),
    exclude_tags: Optional[List[str]] = typer.Option(None, help="List of tags to exclude"),
    include_mode: str = typer.Option("any", help="Mode for including tags"),
    exclude_mode: str = typer.Option("any", help="Mode for excluding tags"),
    output_file: Optional[Path] = typer.Option(
        None, "--output-file", "-o", help="Path to the output YAML file"
    ),
):
    """
    Filter YAML content based on verbosity levels and tags.
    """
    try:
        filter_config = FilterConfig(
            config_key=config_key,
            content_key=content_key,
            verbosity_key=verbosity_key,
            target_verbosity=target_verbosity,
            tags_key=tags_key,
            include_tags=include_tags,
            exclude_tags=exclude_tags,
            include_mode=include_mode,
            exclude_mode=exclude_mode,
        )

        data = load_yaml_from_file_or_stdin(input_file)
        processed_dict = filter_compound(data, **filter_config.dict())
        output_yaml(processed_dict, output_file)

    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command("collapse")
def collapse_command(
    input_file: Optional[Path] = typer.Argument(
        None, help="Path to the input YAML file (or use stdin if not provided or '-')"
    ),
    config_key: str = typer.Option(
        "multi_lang_config", help="Name of the key that contains the collapsing configuration"
    ),
    keys_key: str = typer.Option(
        "lang_keys", help="Name of the key within the config that specifies the collapsible keys"
    ),
    default_key: str = typer.Option(
        "default_lang",
        help="Name of the key within the config that specifies the default key to use",
    ),
    user_key: Optional[str] = typer.Option(
        None,
        "--user-key",
        "-k",
        help="Name of the key within the config that specifies the user's selected language",
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output-file", "-o", help="Path to the output YAML file"
    ),
):
    """
    Collapse multi-language keys in YAML content.
    """
    try:
        collapse_config = CollapseConfig(
            config_key=config_key, keys_key=keys_key, default_key=default_key, user_key=user_key
        )

        data = load_yaml_from_file_or_stdin(input_file)
        processed_dict = collapse_keys(data, **collapse_config.dict())
        output_yaml(processed_dict, output_file)

    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command("compare")
def compare_command(
    from_file: Optional[Path] = typer.Argument(
        None, help="Path to the source YAML file (or use stdin if not provided or '-')"
    ),
    to: Path = typer.Option(..., help="Path to the target YAML file to compare against"),
):
    """
    Compare two YAML files or compare YAML from stdin/file with another file.
    If 'from_file' is not provided or is '-', input will be read from stdin.
    The 'to' option specifies the file to compare against.
    """
    try:
        data1 = load_yaml_from_file_or_stdin(from_file)
        data2 = load_yaml_from_file_or_stdin(to)

        compare_result = compare_yaml_content(data1, data2)
        if compare_result.is_equal:
            typer.echo("The YAML contents are identical.")
        else:
            typer.echo("The YAML contents are different:")
            typer.echo(compare_result.diff)
    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
