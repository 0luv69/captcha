from django.contrib import admin

from .models import Captcha, CaptchaImg

# Register your models here.
admin.site.register(Captcha)
admin.site.register(CaptchaImg)