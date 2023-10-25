from django.middleware.csrf import get_token

class CsrfMixin:
    def get_context_data(self):
        context = super().get_context_data()
        csrf_token = get_token(self.request)
        context['csrf_token'] = csrf_token
        return context