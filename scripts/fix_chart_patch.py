"""Fix chart data POST endpoint - reads form_data from URL query params."""
import json

def init():
    import time
    time.sleep(5)

    from flask import request
    import superset

    app = superset.app

    @app.before_request
    def inject_form_data():
        if request.path == "/api/v1/chart/data" and request.method == "POST":
            fd = request.args.get("form_data")
            if fd:
                try:
                    j = json.loads(fd)
                    request.environ["CONTENT_TYPE"] = "application/json"
                    request._cached_json = (j, j)
                    request.__dict__.pop("is_json", None)
                except Exception:
                    pass

    print("ChartDataRestApi patched! before_request hook installed.", flush=True)
