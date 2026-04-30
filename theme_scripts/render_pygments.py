import argparse
import re

from pygments.formatters import HtmlFormatter

LIGHT_THEME = "friendly"
DARK_THEME = "nord-darker"

LIGHT_SELECTORS = [".highlight", "pre.literal-block"]
DARK_SELECTORS = [
    '[data-theme="dark"] .highlight',
    ':root:not([data-theme="light"]) .highlight',
    '[data-theme="dark"] pre.literal-block',
    ':root:not([data-theme="light"]) pre.literal-block',
]


def pygments_css(style: str, selectors: list[str]) -> str:
    css = HtmlFormatter(style=style).get_style_defs(selectors)
    # Remove background-only rules so the theme's CSS variables control code block backgrounds
    return re.sub(r"[^{}]+\{background:[^}]+\}\n?", "", css)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "light", type=argparse.FileType("w"), help="Light theme CSS output"
    )
    parser.add_argument(
        "dark", type=argparse.FileType("w"), help="Dark theme CSS output"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.light.write(pygments_css(LIGHT_THEME, LIGHT_SELECTORS))
    args.dark.write(pygments_css(DARK_THEME, DARK_SELECTORS))
