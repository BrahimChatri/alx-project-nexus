from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import CustomUser
from backend.utils.encryption import encrypt_data
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

# helper function to check password difficulty
def is_password_strong(password):
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    print("Register view was called!")

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

    if not first_name_raw or not last_name_raw or not full_name_raw:
        return JsonResponse({"error": "First name, last name, and full name are required"}, status=400)
    
    
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
