"""
MCP Server for Selective Answering Abstention Gatekeeper Skill.
"""

import json
import sys
from client import SelectiveGatekeeper

GATEKEEPER = SelectiveGatekeeper()


def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "evaluate_action",
                    "description": "Evaluate whether agent should execute or abstain based on confidence and risk budget",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "confidence": {"type": "number"},
                            "predicted_action": {"type": "string"},
                            "context_metadata": {"type": "object"}
                        },
                        "required": ["confidence", "predicted_action"]
                    }
                },
                {
                    "name": "set_risk_parameters",
                    "description": "Update confidence threshold and risk cost multipliers",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "confidence_threshold": {"type": "number"},
                            "cost_of_error": {"type": "number"},
                            "cost_of_abstention": {"type": "number"}
                        }
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "evaluate_action":
            res = GATEKEEPER.evaluate_action(
                args["confidence"],
                args["predicted_action"],
                args.get("context_metadata")
            )
            return {"content": [{"type": "text", "text": json.dumps(res)}]}

        elif tool_name == "set_risk_parameters":
            if "confidence_threshold" in args:
                GATEKEEPER.confidence_threshold = args["confidence_threshold"]
            if "cost_of_error" in args:
                GATEKEEPER.cost_of_error = args["cost_of_error"]
            if "cost_of_abstention" in args:
                GATEKEEPER.cost_of_abstention = args["cost_of_abstention"]
            return {"content": [{"type": "text", "text": json.dumps({"status": "parameters_updated"})}]}

        return {"error": f"Unknown tool: {tool_name}"}

    return {"error": f"Unknown method: {method}"}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            resp["id"] = req.get("id")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
