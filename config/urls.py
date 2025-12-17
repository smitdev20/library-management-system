"""
URL configuration for Library Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management API",
        default_version='v1',
        description="API for managing books, loans, and reviews.",
        contact=openapi.Contact(email="contact@library.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Root redirect to API documentation
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='index'),
    
    # Admin panel
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.books.urls')),
    path('api/', include('apps.loans.urls')),
    path('api/', include('apps.reviews.urls')),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]
