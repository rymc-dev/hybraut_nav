@dataclass
class GuardWrapper:
    - name: str
    - guard: GuardInterface
    - cache_enabled: bool
    - cache_ttl: float
    - last_evaluation: Optional[GuardEvaluation]
    - last_evaluation_time: float
    + evaluate(context: EvaluationContext) GuardEvaluation
    + clear_cache()
    + load_guard_from_famd(data: Dict[str, Any]) GuardWrapper

@dataclass
class ResetWrapper:
    - name: str
    - reset: ResetInterface
    + evaluate(context: EvaluationContext) ResetResult
    + load_reset_from_famd(data: Dict[str, Any]) ResetWrapper

class InvariantWrapper:
    - name: str
    - invariant: InvariantInterface
    - violation_count: int
    - max_violations: int
    + evaluate_invariant(context: EvaluationContext) bool
    + reset_violation_count()
    + load_invariant_from_famd(data: Dict[str, Any]) InvariantWrapper


class DynamicsWrapper:
    - name: str
    - dynamics: DynamicsInterface
    + evaluate_dynamics(context: EvaluationContext) Any
    + load_dynamics_from_famd(data: Dict[str, Any]) DynamicsWrapper