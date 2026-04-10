{% if cookiecutter.add_arq == "y" %}
"""
arq task definitions.

Each task is an async function that receives a context dict as its first
argument. Register tasks in WorkerSettings.functions.

Example:

    async def send_email(ctx: dict, recipient: str, subject: str) -> None:
        # ctx["db"] is available if you set it up in startup()
        ...

Enqueue from your FastAPI routes:

    from arq import create_pool
    from app.settings import settings
    from arq.connections import RedisSettings

    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    await redis.enqueue_job("send_email", recipient="user@example.com", subject="Hi")
"""


async def example_task(ctx: dict, message: str) -> str:
    """A placeholder task. Replace or remove."""
    return f"processed: {message}"
{% endif %}
