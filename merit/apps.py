from django.apps import AppConfig


class MeritConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'merit'
    
    def ready(self):
        """Log CSV loading status when app starts"""
        try:
            from .views import load_merit_data
            df = load_merit_data()
            if df is not None:
                print(f"[MERIT APP] Successfully loaded CSV with {len(df)} rows")
            else:
                print("[MERIT APP] WARNING: Failed to load CSV data!")
        except Exception as e:
            print(f"[MERIT APP] Error during startup: {e}")

