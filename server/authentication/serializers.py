from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import UserCompany


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adiciona campos customizados ao token (opcional)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['user_id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Adiciona campos customizados à resposta
        user = self.user
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['user_id'] = user.id
        
        company_users = UserCompany.objects.filter(user=user)
        data['company'] = []
        data['phone'] = ''
        data['permissions'] = list(user.user_permissions.values_list('codename', flat=True))

        if company_users.exists():
            # Supondo que o código da empresa esteja no campo 'code'
            data['company'] = [uc.company.id for uc in company_users if uc.company]


        return data
