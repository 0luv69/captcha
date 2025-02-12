
from django.contrib import admin
from django.urls import path,include

from .views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls', namespace='captcha')), #include urls from main app

    path('', home, name='home'), #home page

    path('subbmit_name/', subbmit_name, name='subbmit_name'), #test page

    # path('test/', test_view, name='test'), #test page
]
