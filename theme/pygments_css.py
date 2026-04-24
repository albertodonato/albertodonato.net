import argparse
import re

from pygments.formatters import HtmlFormatter


parser = argparse.ArgumentParser()
parser.add_argument("style")
parser.add_argument("selectors", nargs="+")
args = parser.parse_args()

css = HtmlFormatter(style=args.style).get_style_defs(args.selectors)
# Remove background-only rules so the theme's CSS variables control code block backgrounds
css = re.sub(r"[^{}]+\{background:[^}]+\}\n?", "", css)
print(css)
