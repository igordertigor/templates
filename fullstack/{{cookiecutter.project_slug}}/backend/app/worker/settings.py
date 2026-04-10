{% if cookiecutter.add_arq == "y" %}
from arq.connections import RedisSettings

from app.settings import settings


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


class WorkerSettings:
    functions = []  # register task functions here, e.g. [my_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
{% endif %}
