from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views

urlpatterns = [
    path("", include("posts.urls")),
    path("auth/", include("users.urls")),
    path('about/', include('django.contrib.flatpages.urls')),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/admin/", admin.site.urls),
]
urlpatterns += [
        path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
        path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
        path('about-author/', views.flatpage, {'url': '/about-author/'},
             name='author'),

        path('about-spec/', views.flatpage, {'url': '/about-spec/'},
             name='spec'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
