"""
URL configuration for LeLuChat_ChatEngine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
    title="LeLuChat API",
    default_version="v1",
    description="API for LeLuChat Engine",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('accounts/', include('users.urls')),
    path('engine/', include('chat.urls')),
]

urlpatterns += [
    re_path(
    r"^swagger(?P<format>\.json|\.yaml)$",
    schema_view.without_ui(cache_timeout=0),
    name="schema-json",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
]
