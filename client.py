"""
Selective Answering Abstention Gatekeeper Skill Client
Pure Python Standard Library implementation of selective prediction and optimal abstention (Geifman & El-Yaniv).
Balances empirical risk and coverage targets by deciding whether an agent should
ANSWER autonomously, DELEGATE to tools, or ABSTAIN to human oversight.
"""

from typing import List, Dict, Any, Optional, Tuple


class SelectiveGatekeeper:
    """
    Abstention gatekeeper optimizing the Risk-Coverage profile:
    Risk(f, g) = E[loss(f(x), y) | g(x) = 1]
    Coverage(g) = P(g(x) = 1)
    """

    def __init__(self, confidence_threshold: float = 0.80, cost_of_error: float = 5.0, cost_of_abstention: float = 1.0):
        """
        :param confidence_threshold: Minimum calibrated confidence required to answer autonomously.
        :param cost_of_error: Penalty incurred if the agent answers incorrectly.
        :param cost_of_abstention: Penalty incurred when abstaining / asking a human.
        """
        self.confidence_threshold = confidence_threshold
        self.cost_of_error = cost_of_error
        self.cost_of_abstention = cost_of_abstention
        self.total_queries = 0
        self.answered_queries = 0
        self.abstained_queries = 0

    @property
    def running_coverage(self) -> float:
        """Calculate running coverage proportion of queries answered autonomously."""
        return self.answered_queries / self.total_queries if self.total_queries > 0 else 0.0

    def evaluate_action(self, confidence: float, predicted_action: Any, context_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Decide whether to execute action or abstain based on expected utility.
        Expected cost of answering = (1.0 - confidence) * cost_of_error
        Expected cost of abstaining = cost_of_abstention
        """
        self.total_queries += 1

        cost_answer = (1.0 - confidence) * self.cost_of_error
        cost_abstain = self.cost_of_abstention

        # Decision boundary
        if confidence >= self.confidence_threshold and cost_answer <= cost_abstain:
            decision = "EXECUTE"
            self.answered_queries += 1
            reason = "Confidence exceeds threshold and expected risk is within safety budget."
        elif confidence >= 0.50:
            decision = "DELEGATE_VERIFICATION"
            self.abstained_queries += 1
            reason = "Moderate confidence; secondary verification or tool look-up recommended."
        else:
            decision = "ABSTAIN_HUMAN_IN_THE_LOOP"
            self.abstained_queries += 1
            reason = "Unacceptable error risk; task escalated to human operator."

        return {
            "decision": decision,
            "confidence": confidence,
            "predicted_action": predicted_action,
            "expected_cost_answer": cost_answer,
            "expected_cost_abstain": cost_abstain,
            "running_coverage": self.running_coverage,
            "reason": reason
        }

    def calibrate_threshold_for_target_coverage(self, calibration_confidences: List[float], target_coverage: float) -> float:
        """
        Compute optimal confidence threshold to achieve a desired empirical coverage level.
        """
        if not 0.0 < target_coverage <= 1.0:
            raise ValueError("Target coverage must be in (0.0, 1.0]")
        if not calibration_confidences:
            raise ValueError("Calibration confidences cannot be empty")

        sorted_confs = sorted(calibration_confidences, reverse=True)
        idx = int(len(sorted_confs) * target_coverage) - 1
        idx = max(0, min(idx, len(sorted_confs) - 1))
        
        self.confidence_threshold = sorted_confs[idx]
        return self.confidence_threshold
