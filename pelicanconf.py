AUTHOR = "Aric Maddux"
SITENAME = "The Last Index"
SITEURL = "https://thelastindex.com"

PATH = "content"

TIMEZONE = "America/Indiana/Indianapolis"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


PLUGIN_PATHS = ['plugins/']
PLUGINS = ['artgal']

ARTGAL_DIR = "artgal"
ARTGAL_SAVE_AS = "gallery.html"
ARTGAL_TITLE = "Gallery"

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = "theme/crowsfoot"

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'},
}
