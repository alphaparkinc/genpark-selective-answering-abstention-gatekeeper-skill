"""
Example usage of Selective Answering Abstention Gatekeeper Skill.
"""

from client import SelectiveGatekeeper


def main():
    print("=== Selective Answering Abstention Gatekeeper Demonstration ===")

    gatekeeper = SelectiveGatekeeper(
        confidence_threshold=0.85,
        cost_of_error=10.0,
        cost_of_abstention=1.5
    )

    queries = [
        {"confidence": 0.96, "action": "deploy_smart_contract"},
        {"confidence": 0.88, "action": "update_database_record"},
        {"confidence": 0.72, "action": "refund_customer_payment"},
        {"confidence": 0.35, "action": "delete_production_cluster"}
    ]

    for q in queries:
        res = gatekeeper.evaluate_action(q["confidence"], q["action"])
        print(f"\nAction: {res['predicted_action']}")
        print(f"  Confidence: {res['confidence']:.2f}")
        print(f"  Decision:   {res['decision']}")
        print(f"  Answer Cost: {res['expected_cost_answer']:.2f} vs Abstain Cost: {res['expected_cost_abstain']:.2f}")
        print(f"  Reason:     {res['reason']}")

    print(f"\nFinal Autonomous Coverage: {gatekeeper.running_coverage * 100:.1f}%")


if __name__ == "__main__":
    main()
