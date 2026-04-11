from pathlib import Path

import pelican

AUTHOR = "Alberto Donato"
SITENAME = "Alberto Donato"
SITEURL = "http://localhost:8000"

RELATIVE_URLS = True

TIMEZONE = "UTC"

DEFAULT_LANG = "en"
DEFAULT_PAGINATION = 5
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

# URL formats
ARTICLE_URL = "posts/{slug}"
ARTICLE_SAVE_AS = "posts/{slug}.html"
PAGE_URL = "{slug}"
PAGE_SAVE_AS = "{slug}.html"
TAGS_URL = "tags"
TAGS_SAVE_AS = "tags.html"
TAG_URL = "tag/{slug}"
TAG_SAVE_AS = "tag/{slug}.html"
CATEGORIES_URL = "categories"
CATEGORIES_SAVE_AS = "categories.html"
CATEGORY_URL = "category/{slug}"
CATEGORY_SAVE_AS = "category/{slug}.html"
ARCHIVES_URL = "archives"
ARCHIVES_SAVE_AS = "archives/index.html"
YEAR_ARCHIVE_URL = "archives/{date:%Y}/index"
YEAR_ARCHIVE_SAVE_AS = "archives/{date:%Y}/index.html"
MONTH_ARCHIVE_URL = "archives/{date:%Y}/{date:%m}/index"
MONTH_ARCHIVE_SAVE_AS = "archives/{date:%Y}/{date:%m}/index.html"
DAY_ARCHIVE_URL = "archives/{date:%Y}/{date:%m}/{date:%d}/index"
DAY_ARCHIVE_SAVE_AS = "archives/{date:%Y}/{date:%m}/{date:%d}/index.html"

# Links section
LINKS = ()

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

#
# theme-specific settings
#

# Export pelican version to theme
PELICAN_VERSION = pelican.__version__

LICENSE_NAME = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

MASTODON_LINK = "https://hachyderm.io/@ack"

PAGES_ON_MENU = True
INDEXES_ON_MENU = True

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
# theme-specific settings
#

FAVICON_URL = "/favicon.png"
