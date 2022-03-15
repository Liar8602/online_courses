from django.contrib import admin
from django.urls import path, include

from .settings import DEBUG

import courses.urls
from courses.views import index

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='index'),
    path('index/', index, name='index'),
    path('courses/', include(courses.urls)),
]


if DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns