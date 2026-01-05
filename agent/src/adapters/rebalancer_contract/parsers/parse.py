import json
from typing import Any, Dict, Optional
from engine_types import Flow, TxType

def parse_active_session_info(response: Any) -> Optional[Dict]:
    """
    Parses get_active_session_info response.

    Rust return:
      Option<(u64, Flow, Option<Step>, Option<Step>)>

    JSON examples:
      null
      [nonce, flow, previous_step, pending_step]
    """
    if not hasattr(response, "result"):
        raise ValueError("Invalid response: missing .result")

    try:
        raw = bytes(response.result).decode("utf-8")
        print("Raw active session info:", raw)
        parsed = json.loads(raw)
    except Exception as e:
        raise ValueError(f"Failed to decode active session info: {e}")

    if parsed is None:
        return None

    if not isinstance(parsed, list) or len(parsed) != 4:
        raise ValueError("Invalid active session info format")

    nonce, flow_raw, previous_raw, pending_raw = parsed

    print("Parsed active session info:", parsed)
    
    return {
        "nonce": int(nonce),
        "flow": Flow(flow_raw),
        "previous_step": TxType(previous_raw) if previous_raw is not None else None,
        "pending_step": TxType(pending_raw) if pending_raw is not None else None,
    }