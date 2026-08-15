from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer


class SignupView(APIView):
    def post(self, request):
        # every value comes from the request body — nothing hardcoded here
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 with field errors if bad
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )