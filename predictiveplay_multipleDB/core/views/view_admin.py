from operator import sub
from collections import defaultdict

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db import transaction
from django.db.utils import OperationalError
from django.contrib.auth.mixins import UserPassesTestMixin

from core.models import (
    CricketMatchDetails,
    CricketMatchWinnerDetails,
    CricketPlayer,
    UserSubmission,
    Leaderboard,
    LeaderboardUser,
    LeaderboardPoints,
    FinalLeaderboardPoints
)



class ActiveMatchesPageView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")

    def get(self, request, event_id):

        print("Event ID received:", event_id)

        active_matches = CricketMatchDetails.objects.filter(
            event_id=event_id,   # ✅ filter by event
            status_id__in=[1, 2]
        ).order_by("match_date", "match_time")

        print("Total matches found:", active_matches.count())

        context = {
            "matches": active_matches,
            "event_id": event_id
        }

        return render(request, "admin/active_matches.html", context)


class UpdateMatchResultPageView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    def get(self, request, match_id):

        match = get_object_or_404(
            CricketMatchDetails.objects.select_related(
                "team1",
                "team2",
                "event"
            ),
            match_id=match_id,
            is_deleted=False
        )

        teams = [match.team1, match.team2]

        base_players = CricketPlayer.objects.filter(
            team__in=teams,
            is_active=True,
            is_deleted=False
        ).select_related("team")

        mom_players = base_players

        run_scorers = base_players.filter(
            role__in=[
                CricketPlayer.ROLE_BATTER,
                CricketPlayer.ROLE_ALL_ROUNDER
            ]
        )

        wicket_takers = base_players.filter(
            role__in=[
                CricketPlayer.ROLE_ALL_ROUNDER,
                CricketPlayer.ROLE_BOWLER
            ]
        )

        context = {
            "match": match,
            "mom_players": mom_players,
            "run_scorers": run_scorers,
            "wicket_takers": wicket_takers
        }

        return render(
            request,
            "admin/update_match_result.html",
            context
        )

    def post(self, request, match_id):
        match = get_object_or_404(CricketMatchDetails, match_id=match_id)

        winner_team_id = request.POST.get("winner_team")

        # IMPORTANT: use getlist for M2M
        mom_ids = request.POST.getlist("player_of_match")
        mr_ids = request.POST.getlist("most_runs")
        mw_ids = request.POST.getlist("most_wickets")

        winner_obj, created = CricketMatchWinnerDetails.objects.get_or_create(
            event=match.event,
            match=match
        )

        # ✅ FK field (no change)
        winner_obj.winner_team_id = winner_team_id
        winner_obj.save()

        # ✅ ManyToMany fields
        winner_obj.player_of_match_1.set(mom_ids)
        winner_obj.most_runs_player_1.set(mr_ids)
        winner_obj.most_wickets_player_1.set(mw_ids)

        # mark match completed
        match.status_id = CricketMatchDetails.STATUS_COMPLETED
        match.is_active = False
        match.allow_predictions = False
        match.save()

        return redirect("admin-tools-page", match_id=match.match_id)



class AdminToolsPageView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    def get(self, request, match_id):
        context = {
            "match_id": match_id
        }
        return render(request, "admin/admin_tools.html", context)
    

class UpdateUserSubmissionsView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")

    def post(self, request):

        match_id = request.POST.get("match_id")

        if not match_id:
            return JsonResponse({"error": "match_id required"}, status=400)

        # ---------- FETCH WINNER DETAILS (DEFAULT DB) ----------
        winner = get_object_or_404(
            CricketMatchWinnerDetails.objects.using("default"),
            match_id=match_id
        )

        results = []

        # ---------- LOOP THROUGH COMPANY DBS ----------
        company_dbs = [
            db for db in settings.DATABASES.keys()
            if db != "default"
        ]

        for db_alias in company_dbs:

            try:

                submissions = UserSubmission.objects.using(db_alias).filter(
                    match_id=match_id
                )

                submissions.update(
                    points_winner=0,
                    points_mom=0,
                    points_runs=0,
                    points_wickets=0,
                    flag_winner=False,
                    flag_mom=False,
                    flag_mruns=False,
                    flag_mwickets=False,
                    total_points=0
                )

                updated_count = 0

                winner_mom_ids = set(
                    map(str, winner.player_of_match_1.values_list("pk", flat=True))
                )

                winner_runs_ids = set(
                    map(str, winner.most_runs_player_1.values_list("pk", flat=True))
                )

                winner_wickets_ids = set(
                    map(str, winner.most_wickets_player_1.values_list("pk", flat=True))
                )

                with transaction.atomic(using=db_alias):

                    for sub in submissions:

                        total = 0

                        if sub.predicted_winner_team_id == winner.winner_team_id:
                            sub.points_winner = 3
                            sub.flag_winner = True
                            total += 3

                        # ✅ Player of Match (M2M)
                        if str(sub.predicted_player_of_match_id) in winner_mom_ids:
                            sub.points_mom = 4
                            sub.flag_mom = True
                            total += 4

                        # ✅ Most Runs (M2M)
                        if str(sub.predicted_most_runs_player_id) in winner_runs_ids:
                            sub.points_runs = 2
                            sub.flag_mruns = True
                            total += 2


                        # ✅ Most Wickets (M2M)
                        if str(sub.predicted_most_wickets_taker_id) in winner_wickets_ids:
                            sub.points_wickets = 2
                            sub.flag_mwickets = True
                            total += 2

                        sub.total_points = total

                        sub.save(using=db_alias)

                        updated_count += 1

                results.append({
                    "company_db": db_alias,
                    "updated_records": updated_count,
                    "message": f"User submissions of {db_alias} updated"
                })

            except OperationalError:

                results.append({
                    "company_db": db_alias,
                    "updated_records": 0,
                    "message": f"{db_alias} skipped (table missing)"
                })


        return render(request, "admin/admin_tools.html", {"results": results,"match_id": match_id})


class UpdateLeaderboard1View(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    def post(self, request):

        match_id = request.POST.get("match_id")

        if not match_id:
            return JsonResponse({"error": "match_id required"}, status=400)

        # ---------- FETCH MATCH ----------
        match = get_object_or_404(
            CricketMatchDetails.objects.using("default"),
            match_id=match_id
        )

        event_id = match.event_id

        results = []

        company_dbs = [
            db for db in settings.DATABASES
            if db.startswith("company_")
        ]

        for db_alias in company_dbs:

            company_display_id = db_alias.replace("company_", "").upper()

            try:

                with transaction.atomic(using=db_alias):

                    deleted_count, _ = LeaderboardPoints.objects.using(db_alias).filter(
                        match_id=match_id
                    ).delete()

                    # ✅ Leaderboards
                    leaderboards = Leaderboard.objects.using(db_alias).filter(
                        event_id=event_id,
                        company_display_id=company_display_id
                    )

                    # ✅ All leaderboard users
                    lb_users = LeaderboardUser.objects.using(db_alias).filter(
                        leaderboard_id__in=leaderboards.values_list("leaderboard_id", flat=True),
                        is_deleted=False
                    )

                    # Map user_id → leaderboard_user_ids
                    user_lb_map = {}
                    for lb_user in lb_users:
                        user_lb_map.setdefault(lb_user.user_id, []).append(lb_user)

                    # ✅ Fetch all submissions ONCE
                    submissions = UserSubmission.objects.using(db_alias).filter(
                        match_id=match_id
                    )

                    bulk_data = []

                    for sub in submissions:
                        if sub.user_id not in user_lb_map:
                            continue
                            
                        print("Sub user_id:", sub.user_id)
                        print("Available LB users:", list(user_lb_map.keys())[:5])

                        for lb_user in user_lb_map[sub.user_id]:

                            bulk_data.append(
                                LeaderboardPoints(
                                    leaderboard_user_id=lb_user.leaderboard_user_id,
                                    match_id=match_id,
                                    match_number=match.display_match_id,
                                    points1=sub.total_points,
                                    points2=sub.total_points
                                )
                            )

                    LeaderboardPoints.objects.using(db_alias).bulk_create(bulk_data)

                    results.append({
                        "company_db": db_alias,
                        "deleted_old_records": deleted_count,
                        "created_new_records": len(bulk_data)
                    })

            except Exception as e:

                results.append({
                    "company_db": db_alias,
                    "error": str(e)
                })

        return render(request, "admin/admin_tools.html", {
            "results": results,
            "match_id": match_id
        })
    


class UpdateFinalLeaderboardView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    def post(self, request):

        match_id = request.POST.get("match_id")

        if not match_id:
            return JsonResponse({"error": "match_id required"}, status=400)

        # ---------- FETCH MATCH ----------
        match = CricketMatchDetails.objects.using("default").filter(
            match_id=match_id
        ).first()

        if not match:
            return JsonResponse({"error": "Invalid match_id"}, status=400)

        current_match_number = match.display_match_id
        previous_match_number = current_match_number - 1

        results = []

        # ---------- COMPANY DBS ----------
        company_dbs = [
            db for db in settings.DATABASES
            if db.startswith("company_")
        ]

        for db_alias in company_dbs:

            try:

                with transaction.atomic(using=db_alias):

                    # ✅ Delete only current match records
                    deleted_count, _ = FinalLeaderboardPoints.objects.using(db_alias).filter(
                        match_id=match_id
                    ).delete()

                    # ✅ Fetch only current + previous match points
                    points_qs = list(
                        LeaderboardPoints.objects.using(db_alias).filter(
                            match_number__in=[previous_match_number, current_match_number]
                        )
                    )

                    if not points_qs:
                        results.append({
                            "company_db": db_alias,
                            "message": "No leaderboard points found"
                        })
                        continue

                    # ✅ Split records
                    prev_records = [
                        p for p in points_qs if p.match_number == previous_match_number
                    ]

                    curr_records = [
                        p for p in points_qs if p.match_number == current_match_number
                    ]

                    # ✅ Build cumulative map
                    cumulative_map = defaultdict(int)

                    # previous match
                    for r in prev_records:
                        cumulative_map[r.leaderboard_user_id] = r.points1

                    # current match
                    for r in curr_records:
                        cumulative_map[r.leaderboard_user_id] += r.points1

                    # ✅ Fetch previous ranks
                    if previous_match_number > 0:
                        previous_rank_map = dict(
                            FinalLeaderboardPoints.objects.using(db_alias).filter(
                                match_number=previous_match_number
                            ).values_list("leaderboard_user_id", "rank")
                        )
                    else:
                        previous_rank_map = {}

                    # ✅ Prepare ranking
                    ranking_list = [
                        (user_id, cumulative_map[user_id])
                        for user_id in cumulative_map
                    ]

                    ranking_list.sort(key=lambda x: (-x[1], x[0]))

                    # ✅ Assign ranks
                    current_rank_map = {}
                    rank = 1

                    for idx, (user_id, points) in enumerate(ranking_list):
                        if idx > 0 and points < ranking_list[idx - 1][1]:
                            rank = idx + 1
                        current_rank_map[user_id] = rank

                    # ✅ Build bulk data
                    bulk_data = []

                    for user_id, cumulative_points in ranking_list:
                        bulk_data.append(
                            FinalLeaderboardPoints(
                                leaderboard_user_id=user_id,
                                match_id=match_id,
                                match_number=current_match_number,
                                points1=cumulative_points,
                                points2=cumulative_points,
                                rank=current_rank_map[user_id],
                                previous_rank=previous_rank_map.get(user_id, 0)
                            )
                        )

                    # ✅ Bulk insert
                    FinalLeaderboardPoints.objects.using(db_alias).bulk_create(bulk_data)

                    results.append({
                        "company_db": db_alias,
                        "deleted_old_records": deleted_count,
                        "created_new_records": len(bulk_data)
                    })

            except OperationalError:
                results.append({
                    "company_db": db_alias,
                    "error": "Table not migrated"
                })

            except Exception as e:
                results.append({
                    "company_db": db_alias,
                    "error": str(e)
                })

        return render(request, "admin/admin_tools.html", {
            "results": results,
            "match_id": match_id
        })