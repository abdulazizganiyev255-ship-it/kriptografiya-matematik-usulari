"""Contract tests against the unmodified PrimeGuard mathematical core."""
import pytest

# The existing Streamlit-only CI intentionally does not install FastAPI.
# A separate React/API workflow installs and executes these contract tests.
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["core"] == "python"


def test_known_prime_and_composite():
    prime = client.post("/api/check", json={"n": "17", "k": 5})
    composite = client.post("/api/check", json={"n": "21", "k": 5})
    assert prime.status_code == composite.status_code == 200
    assert prime.json()["verdict"] == "verified_prime"
    assert composite.json()["verdict"] == "composite"
    assert len(composite.json()["algorithms"]) == 3


def test_probable_prime_and_witnesses_are_strings():
    n = "170141183460469231731687303715884105727"  # 2**127 - 1
    response = client.post("/api/check", json={"n": n, "k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["n"] == n
    assert data["verdict"] == "probably_prime"
    assert data["bit_length"] == 127
    for algorithm in data["algorithms"]:
        assert len(algorithm["logs"]) == 3
        assert all(isinstance(log["witness_a"], str) for log in algorithm["logs"])


def test_existing_witness_trace_recomputes_exactly():
    n = "170141183460469231731687303715884105727"
    result = client.post("/api/check", json={"n": n, "k": 1}).json()
    mr = next(a for a in result["algorithms"] if a["algorithm"] == "Miller-Rabin")
    response = client.post("/api/trace", json={
        "n": n, "algorithm": "Miller-Rabin", "log": mr["logs"][0]
    })
    assert response.status_code == 200
    assert response.json()["matches_log"] is True
    assert response.json()["steps"]


def test_carmichael_report_561():
    response = client.post("/api/carmichael", json={"n": "561", "k": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["is_carmichael"] is True
    assert data["fermat_fooled"] is True
    assert data["factors"] == [3, 11, 17]


def test_invalid_inputs_and_resource_bounds():
    for n in ("", "1", "-17", "a3", "9" * 2049):
        assert client.post("/api/check", json={"n": n, "k": 3}).status_code == 422
    assert client.post("/api/check", json={"n": "17", "k": 65}).status_code == 422
    assert client.post("/api/carmichael", json={"n": "1000001", "k": 4}).status_code == 422
    assert client.post("/api/benchmark", json={
        "bit_sizes": [64, 64], "k": 10, "trials": 3
    }).status_code == 422


def test_benchmark_contract_with_small_real_sample():
    response = client.post("/api/benchmark", json={
        "bit_sizes": [64], "k": 5, "trials": 3
    })
    assert response.status_code == 200, response.text
    rows = response.json()["rows"]
    assert len(rows) == 6
    assert {"Algorithm", "Median_Time_ms", "Candidate_Type",
            "Avg_Rounds_Run", "Verdict_Consistency"} <= set(rows[0])
