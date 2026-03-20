from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')), 
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
]

# Обработчики ошибок
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'