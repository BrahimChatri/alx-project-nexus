from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@require_http_methods(["POST"])
@csrf_exempt
def login_view(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    access = AccessToken.for_user(user)
    return JsonResponse({
        "access": str(access),
    })