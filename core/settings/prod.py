from .base import *  # noqa

ALLOWED_HOSTS = ['.appspot.com', '.youjudge.co.uk']
DEBUG = False
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 2592000  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# appengine doesnt support https internally to _ah urls need to be exempt
# so that things like task queues etc can run correctly
SECURE_REDIRECT_EXEMPT = [
    r'^_ah/',
]

# use cached template loader in production to speed things up
for template in TEMPLATES:  # noqa
    template['OPTIONS']['debug'] = False
    if template['BACKEND'] == \
            'django.template.backends.django.DjangoTemplates':
        template['OPTIONS']['loaders'] = [
            ('django.template.loaders.cached.Loader',
                template['OPTIONS']['loaders'])
        ]
