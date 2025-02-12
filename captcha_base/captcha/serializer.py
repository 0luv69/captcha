from rest_framework import serializers
from .models import *


class captchaImgSerializer(serializers.ModelSerializer):
    secure_url = serializers.SerializerMethodField()

    class Meta:
        model = CaptchaImg
        exclude = ('path','name', 'id', )
        read_only_fields = [ 'created_at', 'updated_at']


    def get_secure_url(self, obj: CaptchaImg):
        signer = TimestampSigner()
        signed_id = signer.sign(str(obj.uuid_token))
        return reverse('captcha:serve_captcha_image', kwargs={'signed_image_id': signed_id})

class captchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Captcha
        fields = '__all__'
        read_only_fields = [ 'created_at', 'updated_at']