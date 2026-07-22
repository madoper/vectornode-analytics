import os

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "change-me")

_db_host = os.getenv("POSTGRES_HOST", "postgres")
_db_port = os.getenv("POSTGRES_PORT", "5432")
_db_user = os.getenv("POSTGRES_USER", "podft")
_db_pass = os.getenv("POSTGRES_PASSWORD", "podft-secret")
_db_name = os.getenv("POSTGRES_DB", "superset")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{_db_user}:{_db_pass}@"
    f"{_db_host}:{_db_port}/{_db_name}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", "1")

RESULTS_BACKEND = {
    "function": "superset.utils.redis.get_redis_result_backend",
    "key": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
}

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
}

DATA_CACHE_CONFIG = CACHE_CONFIG

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
}

ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}

ROW_LIMIT = 5000

SUPERSET_WEBSERVER_PORT = int(os.getenv("SUPERSET_PORT", 8088))

WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False


class FormDataInjectMiddleware:
    def __init__(self, app):
        self.app = app
        import psycopg2.pool
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            2, 10,
            host="podft-postgres", port=5432,
            user="podft", password="podft-secret",
            database="superset",
            connect_timeout=3,
            options="-c statement_timeout=5000",
        )
        self.qc_cache = {}
        self.qc_cache_ttl = 300
        self.filter_entry_id = 5

    def _get_conn(self):
        return self.pool.getconn()

    def _put_conn(self, conn):
        self.pool.putconn(conn)

    def __call__(self, environ, start_response):
        if (environ.get("PATH_INFO") == "/api/v1/chart/data"
                and environ.get("REQUEST_METHOD") == "POST"):
            from urllib.parse import parse_qs
            import json as _json, io as _io
            qs = environ.get("QUERY_STRING", "")
            params = parse_qs(qs)
            fd = params.get("form_data", [None])[0]
            if fd:
                try:
                    j = _json.loads(fd)
                    sid = j.get("slice_id")
                    dashboard_id = params.get("dashboard_id", [None])[0]
                    if sid and dashboard_id:
                        merged = self._build_query_context_with_filters(sid, environ)
                        if merged:
                            body = _json.dumps(merged).encode()
                            environ["CONTENT_TYPE"] = "application/json"
                            environ["CONTENT_LENGTH"] = str(len(body))
                            environ["wsgi.input"] = _io.BytesIO(body)
                        else:
                            location = "/api/v1/chart/" + str(sid) + "/data/"
                            start_response("302 Found", [
                                ("Location", location),
                                ("Content-Type", "text/plain"),
                            ])
                            return [b"Redirecting to chart data"]
                    elif sid:
                        location = "/api/v1/chart/" + str(sid) + "/data/"
                        start_response("302 Found", [
                            ("Location", location),
                            ("Content-Type", "text/plain"),
                        ])
                        return [b"Redirecting to chart data"]
                    else:
                        body = _json.dumps(j).encode()
                        environ["CONTENT_TYPE"] = "application/json"
                        environ["CONTENT_LENGTH"] = str(len(body))
                        environ["wsgi.input"] = _io.BytesIO(body)
                except Exception:
                    pass
        return self.app(environ, start_response)

    def _get_query_context(self, conn, slice_id):
        import json as _json, time
        now = time.time()
        cached = self.qc_cache.get(slice_id)
        if cached and now - cached[1] < self.qc_cache_ttl:
            return cached[0]
        cur = conn.cursor()
        cur.execute("SELECT query_context FROM slices WHERE id = %s", (int(slice_id),))
        row = cur.fetchone()
        cur.close()
        if not row or not row[0]:
            return None
        qc = _json.loads(row[0])
        self.qc_cache[slice_id] = (qc, now)
        return qc

    def _get_filter_state(self, conn):
        import json as _json
        cur = conn.cursor()
        cur.execute(
            "SELECT convert_from(value, 'UTF8') FROM key_value WHERE id = %s",
            (self.filter_entry_id,),
        )
        row = cur.fetchone()
        cur.close()
        if not row or not row[0]:
            return None
        entry = _json.loads(row[0])
        if not entry or not entry.get("value"):
            return None
        return _json.loads(entry["value"])

    def _build_query_context_with_filters(self, slice_id, environ):
        import json as _json

        conn = None
        try:
            conn = self._get_conn()
            qc = self._get_query_context(conn, slice_id)
            if not qc:
                return None
        except Exception:
            return None
        finally:
            if conn:
                self._put_conn(conn)

        referrer = environ.get("HTTP_REFERER", "")
        nfk = None
        if "native_filters_key=" in referrer:
            nfk = referrer.split("native_filters_key=")[1].split("&")[0]
        if not nfk:
            return qc

        try:
            conn2 = None
            try:
                conn2 = self._get_conn()
                filter_data = self._get_filter_state(conn2)
            finally:
                if conn2:
                    self._put_conn(conn2)

            if not filter_data:
                return qc

            all_filters = []
            for fk, fv in filter_data.items():
                ff = fv.get("extraFormData", {}).get("filters", [])
                all_filters.extend(ff)

            if not all_filters:
                return qc

            for query in qc.get("queries", []):
                existing = query.get("filters", [])
                query["filters"] = existing + all_filters

            return qc
        except Exception:
            return qc


ADDITIONAL_MIDDLEWARE = [FormDataInjectMiddleware]
