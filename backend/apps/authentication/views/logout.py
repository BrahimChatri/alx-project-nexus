from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        token = OutstandingToken.objects.get(token=request.auth)
        BlacklistedToken.objects.get_or_create(token=token)
        return Response({"message": "Logged out successfully."})
    except:
        return Response({"error": "Token not found or already blacklisted."}, status=400)
