from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..models import CustomUser
from utils.encription import encrypt_data

# helper function to check password difficulty
def is_password_strong(password):
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

@csrf_exempt # For testing only
@require_http_methods(["POST"])
def register_view(request):
    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)
    
    if not is_password_strong(password):
        return JsonResponse({"error": "Password must be at least 8 characters long and contain both letters and numbers"}, status=400)
        
    # Load data 
    first_name_raw = data.get("first_name")
    last_name_raw = data.get("last_name")
    full_name_raw = data.get("full_name")
    address_raw = data.get("address")
    phone_number_raw = data.get("phone_number")

    # encript data
    first_name = encrypt_data(first_name_raw) if first_name_raw else None
    last_name = encrypt_data(last_name_raw) if last_name_raw else None
    full_name = encrypt_data(full_name_raw) if full_name_raw else None
    address = encrypt_data(address_raw) if address_raw else None
    phone_number = encrypt_data(phone_number_raw) if phone_number_raw else None



    user = CustomUser.objects.create_user(
        username=username, 
        password=password, 
        first_name=first_name, 
        last_name=last_name,
        full_name=full_name,
        phone_number=phone_number,
        address=address
        )
    user.save()
    
    return JsonResponse({"message": "User registered successfully"})
