# from rest_framework_simplejwt.tokens import RefreshToken

# class CustomRefreshToken(RefreshToken):

#     @classmethod
#     def for_user(cls, user, company_display_id):
#         token = super().for_user(user)

#         # Custom claims
#         token['user_id'] = str(user.user_id)
#         token['username'] = user.username
#         token['company_display_id'] = company_display_id

#         return token


import uuid
from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):

    @classmethod
    def for_user(cls, user, company_display_id):
        token = super().for_user(user)

        token["company_display_id"] = company_display_id
        token["jti"] = str(uuid.uuid4())

        return token
