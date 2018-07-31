from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import logout

from accounts import views

urlpatterns = (
    url(r'^login/$', views.OauthStepOne.as_view(), name='oauth_step_one'),
    url(r'^oauth2callback/$', views.OauthStepTwo.as_view(),
        name='oauth_step_two'),
    url(r'^logout/$', logout, name='logout', kwargs={
        'next_page': settings.LOGIN_REDIRECT_URL
    }),
)
