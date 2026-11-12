
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MobileLoginSerializer(TokenObtainPairSerializer):

    username_field = "login_id"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["login_id"] = user.login_id
        token["user_type"] = user.user_type

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "login_id": self.user.login_id,
            "full_name": self.user.full_name,
            "email": self.user.email,
            "mobile": self.user.mobile,
            "user_type": self.user.user_type,
        }

        return data
