from dataclasses import dataclass, field


@dataclass
class RoundLog:
    round_idx: int
    witness_a: int
    expression: str
    computed_value: str
    passed: bool
    note: str


@dataclass
class PrimalityResult:
    algorithm: str
    n: int
    bit_length: int
    is_prime: bool
    verdict: str
    rounds_requested: int
    rounds_run: int
    error_bound: str
    elapsed_ms: float
    pre_filtered: bool
    logs: list[RoundLog] = field(default_factory=list)
