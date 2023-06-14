AUTHOR = 'Gioacchino Castorio'
SITENAME = "Gioacchino's Radio Shack"
SITEURL = ''

PATH = 'content'

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'}
}

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
LOAD_CONTENT_CACHE = False

# Blogroll
LINKS = (('GitHub projects', 'https://github.com/castogio'),
         ('qrz.com profile', 'https://www.qrz.com/db/MI0YTF'),)

# Social widget
SOCIAL = ()

DEFAULT_PAGINATION = True

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# THEME = 'themes/Peli-Kiera'
THEME = 'themes/pelican-themes/tuxlite_tbs'
