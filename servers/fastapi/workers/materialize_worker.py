import time

from redis import Redis
from rq import Queue, Worker

from services.materialize_job_queue import (
    get_materialize_queue_name,
    get_materialize_redis_url,
)


def _connect_redis_with_retry() -> Redis:
    redis_url = get_materialize_redis_url()
    last_error: Exception | None = None
    for _ in range(30):
        redis_conn = Redis.from_url(redis_url)
        try:
            redis_conn.ping()
            return redis_conn
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"Redis is unavailable for materialize worker: {last_error}")


def main() -> None:
    redis_conn = _connect_redis_with_retry()
    queue = Queue(get_materialize_queue_name(), connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
