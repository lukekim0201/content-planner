"""Measures average API response time for the core CRUD endpoints.

This exists because "sub-100ms average response time" isn't worth
claiming anywhere (a resume, a README) unless it's an actual measurement.
Run it against a live server:

    uvicorn app.main:app &
    python benchmark.py

Reports per-endpoint and overall average latency in milliseconds.
"""
import statistics
import time
import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"
N_REQUESTS = 50


def request(method: str, path: str, token: str | None = None, body: dict | None = None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    start = time.perf_counter()
    with urllib.request.urlopen(req) as response:
        payload = response.read()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, json.loads(payload) if payload else None


def time_n(label: str, fn, n: int = N_REQUESTS) -> list[float]:
    timings = [fn() for _ in range(n)]
    avg = statistics.mean(timings)
    p95 = statistics.quantiles(timings, n=20)[18]  # ~95th percentile
    print(f"{label:<32} avg={avg:6.2f}ms  p95={p95:6.2f}ms  (n={n})")
    return timings


def main():
    email = f"bench-{uuid.uuid4().hex[:8]}@example.com"
    password = "benchmark123"

    _, _ = request("POST", "/signup", body={"email": email, "password": password})
    _, login_body = request("POST", "/login", body={"email": email, "password": password})
    token = login_body["access_token"]

    _, project = request("POST", "/projects", token=token, body={"title": "Benchmark Project"})
    project_id = project["id"]
    request("POST", f"/projects/{project_id}/script", token=token, body={"content": "<p>bench</p>"})

    all_timings: list[float] = []

    all_timings += time_n("GET /projects", lambda: request("GET", "/projects", token=token)[0])
    all_timings += time_n(
        "GET /projects/{id}", lambda: request("GET", f"/projects/{project_id}", token=token)[0]
    )
    all_timings += time_n(
        "GET /projects/{id}/full",
        lambda: request("GET", f"/projects/{project_id}/full", token=token)[0],
    )
    all_timings += time_n(
        "PATCH /projects/{id}",
        lambda: request(
            "PATCH", f"/projects/{project_id}", token=token, body={"status": "PRODUCTION"}
        )[0],
    )
    all_timings += time_n(
        "GET /projects/{id}/script",
        lambda: request("GET", f"/projects/{project_id}/script", token=token)[0],
    )
    all_timings += time_n("GET /auth/me", lambda: request("GET", "/auth/me", token=token)[0])

    print("-" * 60)
    print(f"{'OVERALL':<32} avg={statistics.mean(all_timings):6.2f}ms  "
          f"p95={statistics.quantiles(all_timings, n=20)[18]:6.2f}ms  "
          f"(n={len(all_timings)})")


if __name__ == "__main__":
    main()
