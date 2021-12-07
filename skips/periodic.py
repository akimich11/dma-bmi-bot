from datetime import datetime
import skips.views as views


def check_and_clear_skips(is_cleared):
    now = datetime.utcnow()
    today_midnight = now.replace(hour=0, minute=2, second=0, microsecond=0)
    if now.day == 1 and now < today_midnight and not is_cleared:
        views.clear_skips()
        return True
    if now.day == 2:
        return False
