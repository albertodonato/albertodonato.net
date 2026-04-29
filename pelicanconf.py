import logging
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)


AUTHOR = "Alberto Donato"
SITENAME = "Alberto Donato"
SITEURL: str = "http://localhost:8000"

RELATIVE_URLS = True

TIMEZONE = "UTC"

DEFAULT_LANG = "en"
DEFAULT_PAGINATION = 5
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

# URL formats
ARTICLE_URL = "blog/posts/{slug}"
ARTICLE_SAVE_AS = "blog/posts/{slug}.html"
PAGE_URL = "blog/{slug}"
PAGE_SAVE_AS = "blog/{slug}.html"
INDEX_URL = "blog"
INDEX_SAVE_AS = "blog/index.html"
TAGS_URL = "blog/tags"
TAGS_SAVE_AS = "blog/tags.html"
TAG_URL = "blog/tag/{slug}"
TAG_SAVE_AS = "blog/tag/{slug}.html"
CATEGORIES_URL = "blog/categories"
CATEGORIES_SAVE_AS = "blog/categories.html"
CATEGORY_URL = "blog/category/{slug}"
CATEGORY_SAVE_AS = "blog/category/{slug}.html"
ARCHIVES_URL = "blog/archives"
ARCHIVES_SAVE_AS = "blog/archives/index.html"
YEAR_ARCHIVE_URL = "blog/archives/{date:%Y}/index"
YEAR_ARCHIVE_SAVE_AS = "blog/archives/{date:%Y}/index.html"
MONTH_ARCHIVE_URL = "blog/archives/{date:%Y}/{date:%m}/index"
MONTH_ARCHIVE_SAVE_AS = "blog/archives/{date:%Y}/{date:%m}/index.html"
DAY_ARCHIVE_URL = "blog/archives/{date:%Y}/{date:%m}/{date:%d}/index"
DAY_ARCHIVE_SAVE_AS = "blog/archives/{date:%Y}/{date:%m}/{date:%d}/index.html"

# Links section
LINKS = (
    ("Blog", "blog"),
    ("Projects", "blog/projects"),
)

# Social links
SOCIAL = (
    ("github", "https://github.com/albertodonato"),
    ("linkedin", "https://www.linkedin.com/in/albertodonato"),
    ("mastodon", "https://hackyderm.io/@ack"),
)

DIRECT_TEMPLATES = ("index", "categories", "tags", "authors", "archives")

USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = "misc"

extra_paths = [
    path.relative_to("content") for path in Path("content/extra").iterdir()
]

STATIC_PATHS = ["images", "files", *extra_paths]
EXTRA_PATH_METADATA = {str(path): {"path": path.name} for path in extra_paths}

THEME = "./theme"

PLUGINS = ["sitemap"]
SEARCH_ENABLED = bool(which("stork"))
if SEARCH_ENABLED:
    PLUGINS.append("search")
else:
    logger.warning("stork executable not found, not enabling search")

#
# plugin: sitemap
#
SITEMAP = {
    "format": "xml",
    "priorities": {"articles": 0.5, "indexes": 0.5, "pages": 0.5},
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly",
    },
}

#
# plugin: pelican-search
#
STORK_INPUT_OPTIONS = {"url_prefix": SITEURL}

#
# theme-specific settings
#

LICENSE_NAME = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

MASTODON_VERIFICATION_LINK = "https://hachyderm.io/@ack"

FAVICON_URL = "/favicon.png"
AVATAR_URL = "/avatar.jpg"
