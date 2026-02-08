from django.shortcuts import redirect
import requests

class JWTRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 401 and request.COOKIES.get("refresh_token"):
            # Try refresh
            refresh_response = requests.post(
                request.build_absolute_uri("token/refresh/"),
                cookies=request.COOKIES,
            )
            if refresh_response.status_code == 200:
                return redirect(request.path)

        return response
