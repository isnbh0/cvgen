"""Classicko theme for RenderCV - Korean-optimized classic theme."""

from typing import Literal

from rendercv.themes.options import ThemeOptions, theme_options_theme_field_info

# Set default theme name
theme_options_theme_field_info.default = "classicko"


class ClassickoThemeOptions(ThemeOptions):
    """Theme options for classicko theme (Korean-optimized classic).

    This theme is an extension of the classic theme with Korean language support
    and customizable education entry degree column width.
    """

    theme: Literal["classicko"] = theme_options_theme_field_info
