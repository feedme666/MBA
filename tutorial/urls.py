from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings #追加
from django.views.static import serve  #追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pdfmr/', include('pdfmr.urls')),
    path('', include('accounts.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  #追加
    path('keijiban/',include('keijiban.urls')), #追加
]

