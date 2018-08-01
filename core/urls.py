from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

import session_csrf

session_csrf.monkeypatch()


urlpatterns = (
    url(r'^_ah/', include('djangae.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include('dashboard.urls'))
)

if settings.DEBUG:  # pragma: no cover
    urlpatterns += tuple(static(
        settings.STATIC_URL, view=serve, show_indexes=True))
