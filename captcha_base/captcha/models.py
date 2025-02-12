from django.db import models
from django.urls import reverse
from django.core.signing import TimestampSigner
import uuid

class CaptchaImg(models.Model):
    name = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100) # 100x100
    description = models.TextField( null=True, blank=True,default='')
    path = models.ImageField(upload_to='captcha/alter_img/')

    uuid_token =  models.UUIDField(default=uuid.uuid4, editable=True, unique=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def secure_url(self):
        signer = TimestampSigner()
        signed_id = signer.sign(str(self.uuid_token))
        return reverse('captcha:serve_captcha_image', kwargs={'signed_image_id': signed_id})
    

class Captcha(models.Model):
    main_captcha = models.BooleanField(default=True)
    alternative_captcha  = models.ForeignKey('self', related_name='captchas', blank=True, null=True, on_delete=models.CASCADE)
    images = models.ManyToManyField(CaptchaImg, related_name='captchas_images', blank=True, )
    question = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category