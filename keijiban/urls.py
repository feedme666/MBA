from django.conf.urls import url
from keijiban import views

app_name= 'keijiban'
urlpatterns = [
    url('^$', views.kakikomi, name='kakikomi'),
]