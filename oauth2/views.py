from django.views.generic import base


class AuthorizationView(base.RedirectView):
    url = '/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)


class TokenView(base.RedirectView):
    url = '/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)
