from typing import Any

import pymysql
import pymysql.cursors
from fastapi import HTTPException, status

from .config import Settings
from .schemas import MovieOptionItem

MOVIE_UNAVAILABLE_DETAIL = "电影数据暂时不可用，可以先手动输入选项。"
MOVIE_NOT_ENOUGH_DETAIL = "当前可用电影不足 6 部，可以先手动输入选项。"

MOVIE_QUERY = """
SELECT movieid, name, detail_url, poster, type, actors, release_date, score
FROM maoyan_film
WHERE state = 1
  AND name IS NOT NULL
  AND TRIM(name) <> ''
ORDER BY RAND()
LIMIT 6
"""


def _require_mysql_settings(settings: Settings) -> None:
    if not settings.mysql_host or not settings.mysql_user or not settings.mysql_database:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MOVIE_UNAVAILABLE_DETAIL,
        )


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _row_to_movie_item(row: dict[str, Any]) -> MovieOptionItem | None:
    label = _clean(row.get("name"))
    if not label:
        return None

    return MovieOptionItem(
        label=label,
        movieId=_clean(row.get("movieid")),
        poster=_clean(row.get("poster")),
        type=_clean(row.get("type")),
        actors=_clean(row.get("actors")),
        releaseDate=_clean(row.get("release_date")),
        score=_clean(row.get("score")),
        detailUrl=_clean(row.get("detail_url")),
    )


def get_random_active_movies(settings: Settings) -> list[MovieOptionItem]:
    _require_mysql_settings(settings)

    try:
        connection = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            charset="utf8mb4",
            connect_timeout=settings.mysql_connect_timeout,
            read_timeout=settings.mysql_connect_timeout,
            write_timeout=settings.mysql_connect_timeout,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.MySQLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MOVIE_UNAVAILABLE_DETAIL,
        ) from exc

    try:
        with connection.cursor() as cursor:
            cursor.execute(MOVIE_QUERY)
            rows = cursor.fetchall()
    except pymysql.MySQLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=MOVIE_UNAVAILABLE_DETAIL,
        ) from exc
    finally:
        connection.close()

    movies = [item for row in rows if (item := _row_to_movie_item(row))]
    if len(movies) != 6:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=MOVIE_NOT_ENOUGH_DETAIL,
        )

    return movies
