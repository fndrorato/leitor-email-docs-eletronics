from app.permissions import GlobalDefaultPermission, IsSelf
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser
from users.serializers import (
    PasswordChangeSerializer,
)


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated, IsSelf, ]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)

