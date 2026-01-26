import json
import traceback
from typing import Any, Dict

import httpx
from dstack_sdk import AsyncTappdClient
from tee import KeyPairGenerator


PROOF_UPLOAD_URL = "https://proof.t16z.com/api/upload"


async def get_tee_info(agent_account: KeyPairGenerator) -> Dict[str, Any]:
    """
    Fetch TEE attestation info:
      - TCB info from tappd
      - TDX quote for report_data=agent_account.account_id (raw)
      - Upload quote to proof service to get checksum + collateral

    Returns on success:
      {
        "quote_hex": str,
        "collateral": str,  # JSON string
        "checksum": str,
        "tcb_info": str     # minified JSON string
      }

    Returns on failure (keeps your current pattern):
      { "success": False, "error": str }
    """
    print(f"✅ Fetching TEE info for account: {agent_account.account_id}")

    tappd = AsyncTappdClient()

    try:
        # 1) TCB info
        tcb_info_dict = await tappd.get_info()
        if not isinstance(tcb_info_dict, dict) or "tcb_info" not in tcb_info_dict:
            raise ValueError(f"Unexpected get_info() response: {tcb_info_dict!r}")

        parsed_tcb_info = json.loads(tcb_info_dict["tcb_info"])
        # Minified JSON string (stable, no whitespace)
        tcb_info = json.dumps(parsed_tcb_info, ensure_ascii=False, separators=(",", ":"))

        print("✅ TCB Info retrieved successfully.")
        print(f"TCB Info: {tcb_info}")

        # 2) Quote
        quote_response = await tappd.tdx_quote(
            report_data=agent_account.account_id,
            hash_algorithm="raw",
        )

        quote_hex = getattr(quote_response, "quote", None)
        if not isinstance(quote_hex, str) or not quote_hex:
            raise ValueError(f"Unexpected tdx_quote() response: {quote_response!r}")

        if quote_hex.startswith("0x"):
            quote_hex = quote_hex[2:]

        # 3) Upload quote to proof service
        files = {
            # field name = 'hex' (as your existing code)
            "hex": (None, quote_hex, "text/plain"),
        }

        timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                PROOF_UPLOAD_URL,
                files=files,
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            res_data = resp.json()

        if not isinstance(res_data, dict):
            raise ValueError(f"Unexpected proof response JSON: {res_data!r}")

        checksum = res_data.get("checksum")
        quote_collateral = res_data.get("quote_collateral")

        if not isinstance(checksum, str) or not checksum:
            raise ValueError(f"Missing/invalid checksum in proof response: {res_data!r}")

        collateral = json.dumps(quote_collateral, ensure_ascii=False, separators=(",", ":"))

        return {
            "quote_hex": quote_hex,
            "collateral": collateral,
            "checksum": checksum,
            "tcb_info": tcb_info,
        }

    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as e:
        print(f"[ERROR] Failed to fetch TEE info: {e}")
        print(f"[ERROR] Full error details: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        # Catch-all, keeps your current behavior
        print(f"[ERROR] Unexpected failure fetching TEE info: {e}")
        print(f"[ERROR] Full error details: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}