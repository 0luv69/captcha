from django.urls import path, include
from captcha.views import *

app_name = "captcha" #namespace


urlpatterns = [
path('get-captcha/', generate_captcha, name='generate_captcha'), #get captcha
path('validate-captcha/', validate_captcha, name='validate_captcha'),#validation check of captcha
path('image/<signed_image_id>/', serve_captcha_image, name='serve_captcha_image'), #serve captcha image

path("c_in/", create_captcha_from_json, name='captcha_in'), #create captcha from json

]