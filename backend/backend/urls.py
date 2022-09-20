"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class MyAPISchemeGenerator(OpenAPISchemaGenerator):
    def __init__(self, info, version='', url=None, patterns=None,
                 urlconf=None):
        url = settings.BASE_URL_DOCUMENTATION_API
        super().__init__(info, version='', url=url, patterns=None,
                         urlconf=None)


schema_view = get_schema_view(
    openapi.Info(
        title="BMeet",
        default_version='1',
        description="Documentation to project BMeet",
        contact=openapi.Contact(email="bmeet.info@mail.ru"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=MyAPISchemeGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/profile/', include('cabinet.urls', namespace='cabinet')),

    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
]
