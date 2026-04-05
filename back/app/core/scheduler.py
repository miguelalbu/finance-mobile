from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings


def create_scheduler(refresh_fn: Callable) -> BackgroundScheduler:
    """
    Cria e configura o scheduler para atualização periódica das cotações.
    O job executa a cada SCHEDULER_INTERVAL_MINUTES minutos.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=refresh_fn,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id="refresh_assets",
        name="Atualiza cotações dos ativos periodicamente",
        replace_existing=True,
    )
    return scheduler
