from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    """Страница "О проекте"."""
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страница "Правила"."""
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Кастомная страница 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомная страница 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Кастомная страница 403 CSRF."""
    return render(request, 'pages/403csrf.html', status=403)