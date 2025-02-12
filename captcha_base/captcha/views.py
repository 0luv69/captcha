from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils import timezone

from django.db.models import Q
from django.http import JsonResponse
import json, secrets, os
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Captcha, CaptchaImg
from .serializer import captchaImgSerializer, captchaSerializer

TOTAL_CAPTCHA_IMG = 7

def get_random_captcha(request):
    MORE_NEEDED_IMG = TOTAL_CAPTCHA_IMG
    challenge_images = []
    selected_captcha = Captcha.objects.exclude(Q(category="alter_img") | Q(main_captcha=False)).order_by("?").distinct().first()
    # selected_captcha = Captcha.objects.get(category="fish")
    
    correct_images = list(selected_captcha.images.order_by("?").distinct()[0:2])
    correct_ids = [str(img.uuid_token)for img in correct_images]

    MORE_NEEDED_IMG = MORE_NEEDED_IMG - 2


    if selected_captcha.alternative_captcha :
        # If there are other other captchas images of particular catogray, add 3 of them to the challenges
        other_captchas = selected_captcha.alternative_captcha 
        challenge_images = list(other_captchas.images.order_by("?"))[0:3]
        MORE_NEEDED_IMG = MORE_NEEDED_IMG - len(challenge_images )

    if MORE_NEEDED_IMG > 0:
        # If more images are needed, add images from alter_img category
        alter_img = Captcha.objects.get(category="alter_img")
        challenge_images = list(alter_img.images.order_by("?")[0:MORE_NEEDED_IMG]) + challenge_images
    
    challenge_question = selected_captcha.question
    challenge_images = correct_images + challenge_images

    # Store answer in session
    request.session['captcha_answer'] = correct_ids
    request.session['captcha_expiry'] = timezone.now().timestamp() + 300  # 5 minutes expiry

    return {"challenge_images": challenge_images, "challenge_question": challenge_question}


def generate_captcha(request):
    captcha_data = get_random_captcha(request)
    serilized_img = captchaImgSerializer(captcha_data['challenge_images'], many=True)
    captcha_data['challenge_images'] = serilized_img.data

    return JsonResponse(captcha_data)



def validate_captcha(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    data = json.loads(request.body)
    selected_ids = list(map(str, data.get('selected_ids', [])))
    stored_answer = request.session.get('captcha_answer', [])
    expiry_time = request.session.get('captcha_expiry', 0)

    if not stored_answer or timezone.now().timestamp() > expiry_time:
        captcha_data = get_random_captcha(request)
        serilized_img = captchaImgSerializer(captcha_data['challenge_images'], many=True)
        captcha_data['challenge_images'] = serilized_img.data
        return JsonResponse({'success':False,'message': 'CAPTCHA expired', 'captcha': captcha_data}, status=400)
    
    is_valid = (
        len(selected_ids) == len(stored_answer) and
        set(selected_ids) == set(stored_answer)
    )
    
    # Clear session data
    del request.session['captcha_answer']
    del request.session['captcha_expiry']

    captcha_data = get_random_captcha(request)
    serilized_img = captchaImgSerializer(captcha_data['challenge_images'], many=True)
    captcha_data['challenge_images'] = serilized_img.data

    # Generate a one-time token upon successful verification.
    if is_valid:
        token = secrets.token_urlsafe(32)
        request.session['captcha_validated_token'] = token


    return JsonResponse({
        'success': is_valid,
        'message': 'CAPTCHA verified' if is_valid else 'CAPTCHA verification failed',
        'captcha':captcha_data,
        "token": token if is_valid else None
    })



def serve_captcha_image(request, signed_image_id):
    signer = TimestampSigner()  # Use TimestampSigner for time-based tokens
    try:
        # max_age is specified in seconds (e.g., 300 seconds = 5 minutes)
        image_id = signer.unsign(signed_image_id, max_age=300)
    except SignatureExpired:
        return JsonResponse({'error': 'CAPTCHA expired'}, status=400)
    except BadSignature:
        return JsonResponse({'error': 'Invalid image token.'}, status=400)
    
    try:
        captcha_image = get_object_or_404(CaptchaImg, uuid_token=image_id)
    except Http404:
        return JsonResponse({'error': 'Image not found.'}, status=404)
    
    image_path = os.path.join(settings.MEDIA_ROOT, str(captcha_image.path)).replace("\\", "/") # Convert Windows path to Unix path

    if not os.path.exists(image_path):
        return JsonResponse({'error': 'File not found on server.'}, status=404)
    

    response = FileResponse(open(image_path, "rb"), content_type='image/webp')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    return response


def recaptcha_verification(request):
    user_token = request.POST.get('captcha_validated_token')
    session_token = request.session.pop('captcha_validated_token', None)
    if user_token == session_token:
        return True
    return False
    






# Create your tests here.
@csrf_exempt
@require_http_methods(["POST"])
def create_captcha_from_json(request):
    try:
        data = json.loads(request.body)
        
        for category, content in data.items():
            # Create Captcha instance
            captcha = Captcha.objects.create(
                question=content.get('question'),
                category=category
            )
            if content.get('other'):
                other_content = content.get('other')
                alternative_captcha_  = Captcha.objects.create(question=other_content.get('question'),
                                                                category =category + "____other",
                                                                main_captcha = False
                                                                )
                
                # Process each image in the category
                for img_data in other_content.get('images', []):
                    captcha_img = CaptchaImg.objects.create(
                        name=img_data['name'],
                        dimensions=str(img_data['size']),
                        path=img_data['path'],
                        description=img_data.get('type', '')  # Using type as description
                    )
                    alternative_captcha_ .images.add(captcha_img)
                
                captcha.alternative_captcha  = alternative_captcha_ 
                captcha.save()
            
            # Process each image in the category
            for img_data in content.get('images', []):
                captcha_img = CaptchaImg.objects.create(
                    name=img_data['name'],
                    dimensions=str(img_data['size']),
                    path=img_data['path'],
                    description=img_data.get('type', '')  # Using type as description
                )
                captcha.images.add(captcha_img)
            
        return JsonResponse({'status': 'success', 'message': 'Data imported successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

