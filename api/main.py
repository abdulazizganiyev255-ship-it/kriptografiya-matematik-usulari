"""FastAPI adapter for PrimeGuard's existing tested mathematical algorithms.

Run from the repository root:
    python -m uvicorn api.main:app --reload --port 8000
Numbers and random witnesses are transferred as *decimal strings* so that
JavaScript's IEEE-754 Number precision cannot corrupt mathematical evidence.
"""
from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from analytics.benchmark import run_benchmark
from analytics.carmichael import analyze_carmichael
from analytics.round_explainer import build_round_trace
from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.models import PrimalityResult, RoundLog
from core.number_theory import is_prime_deterministic_64
from core.solovay_strassen import solovay_strassen_test

IntRounds = Annotated[int, Field(strict=True, ge=1, le=64)]
AlgoName = Literal["Fermat", "Solovay-Strassen", "Miller-Rabin"]
MAX_DIGITS = 2048

app = FastAPI(
    title="PrimeGuard Mathematical API",
    description="Akademik ehtimoliy tublik tekshiruvlari uchun Python API.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:4173", "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class CheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n: str = Field(min_length=1, max_length=4096)
    k: IntRounds = 20


class CarmichaelRequest(CheckRequest):
    pass


class RoundModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    round_idx: Annotated[int, Field(strict=True, ge=1, le=64)]
    witness_a: str = Field(min_length=1, max_length=2048)
    expression: str = Field(max_length=4096)
    computed_value: str = Field(max_length=4096)
    passed: bool
    note: str = Field(max_length=4096)


class TraceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n: str = Field(min_length=1, max_length=4096)
    algorithm: AlgoName
    log: RoundModel


class BenchmarkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bit_sizes: list[Literal[64, 128, 256, 512]] = Field(
        default_factory=lambda: [64, 128, 256], min_length=1, max_length=3
    )
    k: Annotated[int, Field(strict=True, ge=5, le=64)] = 20
    trials: Annotated[int, Field(strict=True, ge=3, le=12)] = 10


def parse_number(text: str, *, carmichael: bool = False) -> int:
    digits = text.strip().replace(" ", "").replace("_", "")
    if not digits or len(digits) > MAX_DIGITS or not digits.isascii() or not digits.isdigit():
        raise HTTPException(
            status_code=422,
            detail="2 dan boshlangan, ko'pi bilan 2048 raqamli natural son kiriting.",
        )
    n = int(digits)
    if n < 2:
        raise HTTPException(status_code=422, detail="n kamida 2 bo'lishi kerak.")
    if carmichael and (n < 5 or n % 2 == 0 or n > 1_000_000):
        raise HTTPException(
            status_code=422,
            detail="Karmaykl tajribasi uchun 5 dan 1 000 000 gacha toq son kiriting.",
        )
    return n


def result_data(result: PrimalityResult) -> dict:
    """Safely encode witnesses larger than 2**53 for JavaScript consumers."""
    return {
        "algorithm": result.algorithm,
        "verdict": result.verdict,
        "is_prime": result.is_prime,
        "rounds_requested": result.rounds_requested,
        "rounds_run": result.rounds_run,
        "elapsed_ms": result.elapsed_ms,
        "error_bound": result.error_bound,
        "pre_filtered": result.pre_filtered,
        "logs": [
            {**asdict(log), "witness_a": str(log.witness_a)}
            for log in result.logs
        ],
    }


def inspect_number(n: int, k: int) -> dict:
    results = [
        result_data(fermat_test(n, k)),
        result_data(solovay_strassen_test(n, k)),
        result_data(miller_rabin_test(n, k)),
    ]
    proven_composite = any(not result["is_prime"] for result in results)
    reference = is_prime_deterministic_64(n) if n < 2**64 else None
    if proven_composite or reference is False:
        verdict = "composite"
        explanation = "Murakkablik guvohi yoki deterministik etalon topildi."
    elif reference is True:
        verdict = "verified_prime"
        explanation = "64-bitli diapazonda deterministik etalon tublikni tasdiqladi."
    else:
        verdict = "probably_prime"
        explanation = "Raundlar sinovdan o'tdi; bu matematik tublik isboti emas."
    return {
        "n": str(n),
        "bit_length": n.bit_length(),
        "digit_length": len(str(n)),
        "k": k,
        "verdict": verdict,
        "explanation": explanation,
        "algorithms": results,
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "project": "PrimeGuard", "core": "python"}


@app.post("/api/check")
def check_number(payload: CheckRequest) -> dict:
    n = parse_number(payload.n)
    return inspect_number(n, payload.k)


@app.post("/api/trace")
def trace_round(payload: TraceRequest) -> dict:
    n = parse_number(payload.n)
    witness = parse_number(payload.log.witness_a)
    log = RoundLog(
        round_idx=payload.log.round_idx,
        witness_a=witness,
        expression=payload.log.expression,
        computed_value=payload.log.computed_value,
        passed=payload.log.passed,
        note=payload.log.note,
    )
    try:
        trace = build_round_trace(payload.algorithm, n, log)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "steps": [asdict(step) for step in trace.steps],
        "matches_log": trace.matches_log,
        "computed_pass": trace.computed_pass,
        "truncated": trace.truncated,
    }


@app.post("/api/carmichael")
def check_carmichael(payload: CarmichaelRequest) -> dict:
    n = parse_number(payload.n, carmichael=True)
    report = analyze_carmichael(n, payload.k)
    return {
        "n": str(n),
        "is_carmichael": report["is_carmichael"],
        "fermat_fooled": report["fermat_fooled"],
        "factorization_complete": report["factorization_complete"],
        "factors": report["factors"],
        "factor_powers": report["factor_powers"],
        "korselt_details": report["korselt_details"],
        "algorithms": [
            result_data(report["fermat"]),
            result_data(report["solovay_strassen"]),
            result_data(report["miller_rabin"]),
        ],
    }


@app.post("/api/benchmark")
def benchmark(payload: BenchmarkRequest) -> dict:
    if len(payload.bit_sizes) != len(set(payload.bit_sizes)):
        raise HTTPException(status_code=422, detail="Bit uzunliklari takrorlanmasligi kerak.")
    try:
        frame = run_benchmark(
            bit_sizes=sorted(payload.bit_sizes), k=payload.k, trials=payload.trials
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"rows": frame.to_dict(orient="records"), "config": payload.model_dump()}
