from django.conf import settings
from django.contrib import auth, messages
from django.utils.http import is_safe_url
from django.views.generic.base import RedirectView

from oauth2client import client

from .utils import do_with_retry


def _get_flow(request):
    """
    Get the oauth flow to use for the given request.The flow can be specified
    in the query string for step 1, and is then stored in the session for
    retrival on step 2.
    """
    flow_name = request.GET.get('flow') or request.session.get(
        settings.GOOGLE_OAUTH2_FLOW_SESSION_KEY, 'default')
    request.session[settings.GOOGLE_OAUTH2_FLOW_SESSION_KEY] = flow_name
    flow_kwargs = settings.GOOGLE_OAUTH2_FLOWS.get(
        flow_name) or settings.GOOGLE_OAUTH2_FLOWS['default']
    flow_kwargs['redirect_uri'] = '{}://{}{}'.format(
        request.scheme,
        request.get_host(),
        str(settings.GOOGLE_OAUTH2_REDIRECT_URI))
    return do_with_retry(
        client.OAuth2WebServerFlow,
        _attempts=5,
        _catch=client.FlowExchangeError,
        **flow_kwargs
    )


def _get_authorize_url(request, state):
    flow = _get_flow(request)
    authorize_url = flow.step1_get_authorize_url(state=state)
    return authorize_url


class OauthStepOne(RedirectView):
    """
    Handle the first step of oauth flow
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        continue_url = self.request.GET.get(auth.REDIRECT_FIELD_NAME)
        state = self.request.GET.get('state')
        if continue_url:
            self.request.session[
                settings.LOGIN_REDIRECT_SESSION_KEY] = continue_url
        authorize_url = _get_authorize_url(self.request, state)
        return authorize_url


class OauthStepTwo(RedirectView):
    """
    Handle second and final step of oauth flow
    """
    def get_redirect_url(self, *args, **kwargs):
        code = self.request.GET.get('code', '')
        flow = _get_flow(self.request)
        try:
            credentials = flow.step2_exchange(code=code)
        except client.FlowExchangeError:
            messages.error(self.request, 'Try connecting your account again.')
            return settings.LOGIN_URL

        # This will use our custom backend to get user info from Google and
        # get or create the User object
        user = auth.authenticate(oauth_credentials=credentials)
        if not user:
            messages.error(self.request, 'Try connecting your account again.')
            return settings.LOGIN_URL

        # associate that user with the current browser session
        auth.login(self.request, user)
        continue_url = self.request.session.pop(
            settings.LOGIN_REDIRECT_SESSION_KEY, None)
        if not continue_url or not is_safe_url(
                url=continue_url, host=self.request.get_host()):
            continue_url = settings.LOGIN_REDIRECT_URL
        return continue_url
