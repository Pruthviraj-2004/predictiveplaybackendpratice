class SmartDBRouter:
    """
    Deterministic multi-database router.

    Rules:
    - Company model -> default DB only
    - CompanyUser1 model -> company DBs only
    - No heuristic name matching
    - No hardcoded company DB aliases
    """

    # ---------- MODEL GROUPS ----------

    DEFAULT_ONLY_MODELS = {
        "company",
        "cricket_event",
        "cricket_team",
        "cricket_player",
        "cricket_match_details",
        "cricket_match_winner_details",
    }

    COMPANY_ONLY_MODELS = {
        "companyuser",
        "usersubmission",
        "leaderboard",
        "leaderboarduser",
        "leaderboardpoints",
        "refreshtoken",
    }

    # ---------- CORE RESOLUTION ----------

    def _get_model_name(self, model):
        return model._meta.model_name.lower()

    # ---------- READ / WRITE ----------

    def db_for_read(self, model, **hints):
        """
        Route read operations.
        """
        return self._route_model(model, hints)

    def db_for_write(self, model, **hints):
        """
        Route write operations.
        """
        return self._route_model(model, hints)

    def _route_model(self, model, hints):
        """
        Central routing logic.
        """
        if model is None:
            return None

        model_name = self._get_model_name(model)

        # Explicit instance DB (highest priority)
        instance = hints.get("instance")
        if instance is not None and hasattr(instance, "_state"):
            if instance._state.db:
                return instance._state.db

        # Default-only models
        if model_name in self.DEFAULT_ONLY_MODELS:
            return "default"

        # Company-only models
        if model_name in self.COMPANY_ONLY_MODELS:
            # MUST be provided via .using(db)
            return None

        return None

    # ---------- RELATIONS ----------

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only within same database.
        """
        if obj1 is None or obj2 is None:
            return True

        return obj1._state.db == obj2._state.db

    # ---------- MIGRATIONS ----------

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controls where tables are created.
        """
        if model_name is None:
            return None

        model_name = model_name.lower()

        # Company model → default DB only
        if model_name in self.DEFAULT_ONLY_MODELS:
            return db == "default"

        # CompanyUser1 → company DBs only
        if model_name in self.COMPANY_ONLY_MODELS:
            return db != "default"

        return None
