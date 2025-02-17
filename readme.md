# Video of Captcha 

[Video of Captcha](https://github.com/user-attachments/assets/1b1cfa69-62f4-46e8-82d5-4e2a52d22b7c)




# Captcha System Documentation

This document explains the design, implementation, and security of a Django-based captcha system. The solution comprises backend logic for generating and validating captcha challenges as well as a frontend component for rendering and user interaction.

## * Overview

The captcha system is designed to prevent automated form submissions by presenting users with a challenge where they must select the correct images among decoys. Key features include:

Secure Image URLs: Images are served using signed URLs that expire after a short period.

UUID-Based Identification: Images are identified by UUIDs (not by primary keys) to improve security.

Server-Side Verification: The correct captcha answer is stored in the server session and compared against the user’s selection.

One-Time Tokens for Sensitive Actions: On successful captcha validation, a one-time token is generated and stored in the session; subsequent sensitive actions (e.g., form submission) require this token.

Delayed Loading & Callback Integration: The captcha is loaded after a configurable delay and integrates with other actions via a callback mechanism.

## * Backend Implementation (Django)

### 2.1 Models

#### CaptchaImg

Purpose:Stores individual captcha images.

##### Key Fields:

* **name**: Human-readable image name.
* **dimensions**: The dimensions of the image (e.g., "100x100").

* **description**: Additional text describing the image (optional).

* **path**: Image file storage field; images are uploaded to a dedicated folder.
* **uuid_token**: A UUID field used as a unique identifier. This token is used in place of the primary key.

* **created_at** & **updated_at**: Timestamps to track creation and modification times.

##### Secure URL Generation:

* A property secure_url is provided that uses Django’s TimestampSigner to generate a signed URL. This URL is time-sensitive (expires after a specified duration) to prevent URL tampering.

#### Captcha

##### * Purpose:

* Represents a complete captcha challenge that aggregates multiple images.

##### * Key Fields:

* **main_captcha**: A Boolean flag indicating if this is the primary captcha.
* **alternative_captcha**: (Self-referencing field) Optionally links to an alternative captcha instance containing decoy images.

* **images**: A many-to-many field linking to one or more CaptchaImg objects.
* **question**: A text field containing the captcha challenge prompt.

* **category**: A category label to group related captchas (e.g., “fish” or “alter_img” for decoys).
* **created_at & updated_at**: Timestamp fields.

### 2.2 Views / API Endpoints

#### generate_captcha

    Purpose:Fetches and builds a captcha challenge.

   ##### Functionality:

    Randomly selects a captcha challenge from the database.

    Retrieves two “correct” images from the selected challenge.

    Retrieves additional decoy images either from an alternative captcha (if present) or from a dedicated “alter_img” category.

    Stores the correct image UUIDs in the user session along with an expiration timestamp.

    Returns a JSON response containing:

    challenge_images: An array of image objects (each with secure URLs).

    challenge_question: The captcha question.

# Example Django View

def generate_captcha(request):
    captcha = Captcha.objects.order_by('?').first()
    images = list(captcha.images.all())
    correct_images = random.sample(images, 2)
    decoy_images = get_decoy_images(captcha)

    request.session['captcha_answer'] = [img.uuid_token for img in correct_images]
    request.session['captcha_expiry'] = time.time() + 300  # Expires in 5 minutes

    return JsonResponse({
        "challenge_images": [img.secure_url for img in correct_images + decoy_images],
        "challenge_question": captcha.question
    })

### 2.3 Session and Token Management

Captcha Answer Storage:The correct image UUIDs are stored in the session as captcha_answer along with an expiration timestamp (captcha_expiry).

One-Time Token Generation:On successful captcha verification, a one-time token (captcha_validated_token) is generated and stored in the session.

##### Token Verification Example

def recaptcha_verification(request):
    user_token = request.POST.get('captcha_validated_token')
    session_token = request.session.pop('captcha_validated_token', None)
    return user_token == session_token

3. Frontend Implementation

### 3.1 JavaScript Logic

Image Rendering & Randomization

async function renderCaptchaImg() {
    const response = await fetch("/generate_captcha");
    const data = await response.json();
    document.getElementById("question").textContent = data.challenge_question;
    renderCaptchaContainer(data.challenge_images);
}

##### Verification Function

async function verifyCaptcha() {
    const response = await fetch("/validate_captcha", {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: JSON.stringify({ "selected_ids": selectedImages })
    });

    const data = await response.json();
    if (data.success) {
        alert("Captcha Verified!");
    } else {
        alert("Incorrect. Try Again.");
    }
}

# * Security Considerations

### 4.1 Backend Security

Signed URLs & Expiration:

Image URLs are signed with a timestamp, ensuring they are valid only for a limited period.

Any attempt to use an expired or tampered URL results in an error.

One-Time Token for Sensitive Actions:

After captcha validation, a one-time token is generated and stored in the session.

Sensitive endpoints (like user registration) require this token.

### 4.2 Session Protection

#### Cookie Settings:

Django session cookies should be secured (using SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, and SESSION_COOKIE_SAMESITE settings).

#### Secret Management:

The Django secret key is used for signing session data and cookies.

# * Conclusion

This captcha system uses a combination of secure backend processing and interactive frontend components to ensure that only human users can perform sensitive actions (such as form submissions). By leveraging secure signed URLs, session-based validation, and one-time tokens, the system offers a robust defense against automated abuse while maintaining a user-friendly interface.

This documentation should serve as a detailed guide for maintaining, extending, or auditing the captcha system in your application.




# Video of captcha workflow
   - How verifyCaptcha works
   - How verification gets verified & Rejected
   - How direct console post is prevented 


[How it works](https://github.com/user-attachments/assets/a793b5f9-22dc-4127-8ae3-a4bed4c5f029)
