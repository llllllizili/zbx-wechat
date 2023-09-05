"""wechat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from zbx import views as zbx_views

urlpatterns = [
	url(r'^WW_verify_IzaNHpJmAypFKZid.txt',zbx_views.wxrz,name='wxrz'),#域名可信验证
    url(r'^admin/', admin.site.urls),
    url(r'^test/',zbx_views.test,name='test'),
    url(r'^wechat/ack/',zbx_views.ack,name='ack'),
    url(r'^wechat/batch_ack/',zbx_views.batch_ack,name='batch_ack'),
	url(r'^wechat/detial/',zbx_views.detial,name='detial'),
    url(r'^wechat/create_graph/',zbx_views.create_graph,name='create_graph'),
    url(r'^wechat/weiqueren',zbx_views.weiqueren,name='weiqueren'),
    url(r'^wechat/weijiechu',zbx_views.weijiechu,name='weijiechu'),
    url(r'^wechat/search/',zbx_views.search,name='search'),
    url(r'^wechat/search_eventid/',zbx_views.search_eventid,name='search_eventid'),
    url(r'^wechat/wechat_callback',zbx_views.wechat_callback,name='callback'),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
