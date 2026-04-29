import argparse
import io
from pathlib import Path
import re
import shutil
import urllib.request
import zipfile

FONT_FAMILIES = [
    "Roboto:ital,wght@0,400;0,500;0,700;1,400",
    "Roboto+Mono:wght@400;500",
]

_families = "&".join(f"family={f}" for f in FONT_FAMILIES)
FONTS_URL = f"https://fonts.googleapis.com/css2?{_families}&display=swap"

# Use a modern UA to get woff2 format
FONTS_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

FONT_AWESOME_VERSION = "6.5.1"
FONT_AWESOME_URL = (
    f"https://github.com/FortAwesome/Font-Awesome/releases/download"
    f"/{FONT_AWESOME_VERSION}/fontawesome-free-{FONT_AWESOME_VERSION}-web.zip"
)

_BLOCK_RE = re.compile(
    r"/\*\s*([^*]+?)\s*\*/\s*@font-face\s*\{([^}]+)\}", re.DOTALL
)


def fetch(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return r.read()


def font_filename(family: str, style: str, weight: str, subset: str) -> str:
    slug = family.lower().replace(" ", "-")
    parts = [slug]
    if style != "normal":
        parts.append(style)
    parts.extend([weight, subset])
    return "-".join(parts) + ".woff2"


def download_google_fonts(out_dir: Path) -> None:
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)

    print("Fetching font CSS from Google Fonts...")
    css = fetch(FONTS_URL, {"User-Agent": FONTS_UA}).decode()

    url_to_local: dict[str, str] = {}
    for match in _BLOCK_RE.finditer(css):
        subset = match.group(1).strip()
        block = match.group(2)

        family_m = re.search(r"font-family:\s*'([^']+)'", block)
        style_m = re.search(r"font-style:\s*(\w+)", block)
        weight_m = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", block)

        if (
            family_m is None
            or style_m is None
            or weight_m is None
            or url_m is None
        ):
            continue

        url = url_m.group(1)
        filename = font_filename(
            family_m.group(1), style_m.group(1), weight_m.group(1), subset
        )
        dest = out_dir / filename
        if dest.exists():
            print(f"  skip {filename} (already exists)")
        else:
            print(f"  downloading {filename}")
            dest.write_bytes(fetch(url))
        url_to_local[url] = filename

    local_css = css
    for url, local in url_to_local.items():
        local_css = local_css.replace(url, local)

    css_out = out_dir / "fonts.css"
    css_out.write_text(local_css)
    print(f"Written {css_out}")


def download_font_awesome(out_dir: Path) -> None:
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)

    prefix = f"fontawesome-free-{FONT_AWESOME_VERSION}-web/"
    print(f"Downloading Font Awesome {FONT_AWESOME_VERSION}...")
    data = fetch(FONT_AWESOME_URL)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for entry in zf.namelist():
            rel = entry.removeprefix(prefix)
            if not rel or entry.endswith("/"):
                continue
            if not (rel.startswith("css/") or rel.startswith("webfonts/")):
                continue
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(entry))
            print(f"  extracted {rel}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "out_dir", type=Path, help="Base assets output directory"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_google_fonts(args.out_dir / "fonts")
    download_font_awesome(args.out_dir / "fontawesome")
