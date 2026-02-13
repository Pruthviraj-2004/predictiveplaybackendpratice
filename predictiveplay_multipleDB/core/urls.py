from django import views
from django.urls import path
from core.views.auth import (
    LoginAPIViewV2,
    RefreshTokenAPIView,
    RegisterAPIView,
    LoginAPIViewV1,
    HomeAPIView,
    LogoutAPIView,
)
from core.views.fixtures_view import SelectEventViewV1, FixturesViewV1, FixturesAPIViewV2, SelectEventAPIViewV2
from core.views.matches_views import ActiveMatchesAPIViewV2, MatchPredictionAPIViewV2, MatchPredictionViewV1
from core.views.user_submissions import MySubmissionsAPIViewV2, MySubmissionsViewV1

from rest_framework_simplejwt.views import TokenRefreshView
from core.views.token_refresh import CookieTokenRefreshView
from core.views.leaderboard_views import LeaderboardBoardAPIViewV2, LeaderboardEventsAPIViewV2, UserLeaderboardsByEventAPIViewV2



urlpatterns = [
    path("v1/register/", RegisterAPIView.as_view(), name="register"),
    path("v1/login/", LoginAPIViewV1.as_view(), name="login"),
    path("v1/logout/", LogoutAPIView.as_view(), name="logout"),
    path("v1/home/", HomeAPIView.as_view(), name="home"),
    path("v1/fixtures/events/", SelectEventViewV1.as_view(), name="select_event_v1"),
    path("v1/fixtures/<uuid:event_id>/", FixturesViewV1.as_view(), name="fixtures_v1"),
    path("v1/match/<uuid:match_id>/", MatchPredictionViewV1.as_view(), name="match_prediction"),
    path("v1/my-submissions/", MySubmissionsViewV1.as_view(), name="my_submissions"),


    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/refresh/", RefreshTokenAPIView.as_view(), name="token_refresh"),


    path("v2/login/", LoginAPIViewV2.as_view(), name="login_v2"),
    path("v2/fixtures/events/", SelectEventAPIViewV2.as_view(), name="select_event_v2"),
    path("v2/fixtures/events/<uuid:event_id>/", FixturesAPIViewV2.as_view(), name="fixtures_v2"),
    path("v2/match/<uuid:match_id>/", MatchPredictionAPIViewV2.as_view(), name="match_prediction_v2"),
    path("v2/my-submissions/", MySubmissionsAPIViewV2.as_view(), name="my_submissions_v2"),
    path("v2/leaderboard/events/", LeaderboardEventsAPIViewV2.as_view(), name="leaderboard_events_v2"),
    path("v2/leaderboard/list/by-event/<event_id>/", UserLeaderboardsByEventAPIViewV2.as_view(), name="user_leaderboards_by_event_v2"),
    path("v2/leaderboard/board/<uuid:leaderboard_id>/", LeaderboardBoardAPIViewV2.as_view(), name="leaderboard_board_v2"),
    path("v2/active-matches/", ActiveMatchesAPIViewV2.as_view(), name="active_matches_v2"),


]
