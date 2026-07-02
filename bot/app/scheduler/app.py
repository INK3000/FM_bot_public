from os import getenv

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

_jobstore_path = getenv("SCHEDULER_DB_PATH", "/tmp/fm_jobs.sqlite")

main_scheduler = ContextSchedulerDecorator(
    AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(f"sqlite:///{_jobstore_path}")})
)
