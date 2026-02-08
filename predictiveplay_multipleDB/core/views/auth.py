from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import CompanyUser
from core.utils.company import get_company_db
from core.utils.passwords import hash_password


class RegisterAPIView(APIView):
    permission_classes = []

    def get(self, request):
        # ✅ Show register page
        return render(request, "register.html")

    def post(self, request):
        data = request.data

        company_display_id = data.get("company_display_id")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")

        if not all([company_display_id, username, email, password, full_name]):
            return Response(
                {"detail": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response(
                {"detail": "Invalid company display ID"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if CompanyUser.objects.using(db_alias).filter(email=email).exists():
            return Response(
                {"detail": "Email already exists"},
                status=status.HTTP_409_CONFLICT
            )

        if CompanyUser.objects.using(db_alias).filter(username=username).exists():
            return Response(
                {"detail": "Username already exists"},
                status=status.HTTP_409_CONFLICT
            )

        CompanyUser.objects.using(db_alias).create(
            company_display_id=company_display_id,
            username=username,
            email=email,
            full_name=full_name,
            password=hash_password(password),
            is_active=True,
            is_email_verified=False,
        )

        return redirect("home")

from django.shortcuts import render, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import CompanyUser
from core.utils.company import get_company_db
from core.utils.passwords import verify_password
from core.accounts.tokens import CustomRefreshToken
from core.models.refresh_token import RefreshToken 

class LoginAPIViewV1(APIView):
    permission_classes = []

    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        company_display_id = request.POST.get("company_display_id")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not all([company_display_id, email, password]):
            return render(request, "login.html", {
                "error": "All fields are required"
            })

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return render(request, "login.html", {
                "error": "Invalid company ID"
            })

        try:
            user = (
                CompanyUser.objects
                .using(db_alias)
                .only(
                    "user_id",
                    "password",
                    "is_active",
                    "is_deleted",
                    "company_display_id",
                )
                .get(
                    email=email,
                    is_deleted=False,
                    company_display_id=company_display_id,
                )
            )

        except CompanyUser.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

        if not user.is_active:
            return render(request, "login.html", {
                "error": "User is inactive"
            })

        if not verify_password(password, user.password):
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

        # ✅ Update last login
        user.last_login_at = timezone.now()
        user.save(using=db_alias)

        # ✅ Mint JWT
        refresh = CustomRefreshToken.for_user(
            user=user,
            company_display_id=company_display_id
        )

        RefreshToken.objects.create(
            jti=refresh["jti"],
            user_id=user.user_id,
            company_display_id=company_display_id,
            expires_at=timezone.now() + refresh.lifetime,
        )

        # ✅ Set JWT in HttpOnly cookie
        response = redirect("home")

        # Access token (short)
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,   # True in prod (HTTPS)
            samesite="Lax",
        )

        # Refresh token (long)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,   # True in prod
            samesite="Lax",
        )

        return response



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.authentication import CookieJWTAuthentication, TokenOnlyJWTAuthentication
from core.permissions import HasValidJWT
from django.shortcuts import render

class HomeAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth

        return render(
            request,
            "home.html",
            {
                "company_display_id": token["company_display_id"],
                "username": token["username"],
                "user_id": token["user_id"],
            }
        )


class LogoutAPIView(APIView):
    permission_classes = []

    def post(self, request):
        response = redirect("login")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.exceptions import TokenError
from core.accounts.tokens import CustomRefreshToken
from core.models.refresh_token import RefreshToken


class RefreshTokenAPIView(APIView):
    permission_classes = []

    def post(self, request):
        raw_refresh = request.COOKIES.get("refresh_token")

        if not raw_refresh:
            return Response(
                {"detail": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = CustomRefreshToken(raw_refresh)
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        jti = refresh.get("jti")

        try:
            token_obj = RefreshToken.objects.get(jti=jti)
        except RefreshToken.DoesNotExist:
            # 🚨 Reuse detected
            return Response(
                {"detail": "Token reuse detected"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if token_obj.is_revoked:
            # 🚨 Reuse detected
            return Response(
                {"detail": "Token revoked"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ✅ Rotate: revoke old refresh token
        token_obj.revoke()

        # ✅ Mint new refresh token
        new_refresh = CustomRefreshToken.for_user(
            user_id=refresh["user_id"],
            company_display_id=refresh["company_display_id"],
        )

        RefreshToken.objects.create(
            jti=new_refresh["jti"],
            user_id=refresh["user_id"],
            company_display_id=refresh["company_display_id"],
            expires_at=timezone.now() + new_refresh.lifetime,
        )

        response = Response(
            {"message": "Token refreshed"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            str(new_refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        response.set_cookie(
            "refresh_token",
            str(new_refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response


from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import CompanyUser
from core.utils.company import get_company_db
from core.utils.passwords import verify_password
from core.accounts.tokens import CustomRefreshToken


class LoginAPIViewV2(APIView):
    permission_classes = []

    def post(self, request):
        company_display_id = request.data.get("company_display_id")
        email = request.data.get("email")
        password = request.data.get("password")

        if not all([company_display_id, email, password]):
            return Response(
                {"detail": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response(
                {"detail": "Invalid company ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = (
                CompanyUser.objects
                .using(db_alias)
                .only(
                    "user_id",
                    "password",
                    "is_active",
                    "is_deleted",
                    "company_display_id",
                )
                .get(
                    email=email,
                    is_deleted=False,
                    company_display_id=company_display_id,
                )
            )
        except CompanyUser.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "User is inactive"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not verify_password(password, user.password):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ✅ Update last login
        user.last_login_at = timezone.now()
        user.save(using=db_alias)

        # ✅ Mint JWT
        refresh = CustomRefreshToken.for_user(
            user=user,
            company_display_id=company_display_id,
        )

        response = Response(
            {
                "message": "Login successful",
                "company_display_id": company_display_id,
            },
            status=status.HTTP_200_OK,
        )

        # ✅ Access token (short-lived)
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,   # True in prod (HTTPS)
            samesite="Lax",
        )

        # ✅ Refresh token (long-lived)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,   # True in prod
            samesite="Lax",
        )

        return response
