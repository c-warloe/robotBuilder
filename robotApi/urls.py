from django.conf.urls import url
from robotApi import views

urlpatterns = [
    url(r'^api/component/list/$', views.componentList),
    url(r'^api/component/create/$', views.createComponent),
    url(r'^api/component/addSubcomponent/$', views.addSubcomponent),
    url(r'^api/component/addConnection/$', views.addConnection),
    url(r'^api/component/make/$', views.make),
]