import json
import traceback
from typing import Any, Dict

import httpx
from dstack_sdk import AsyncDstackClient

PROOF_UPLOAD_URL = "https://proof.t16z.com/api/upload"


async def get_tee_info(account_id: str) -> Dict[str, Any]:
    """
    Fetch TEE attestation info:
      - TCB info from tappd
      - TDX quote for report_data=account_id (raw)
      - Upload quote to proof service to get checksum + collateral

    Returns on success:
      {
        "quote_hex": str,
        "collateral": str,  # JSON string
        "checksum": str,
        "tcb_info": str     # minified JSON string
      }

    Returns on failure:
      { "success": False, "error": str }
    """
    print(f"✅ Fetching TEE info for account: {account_id}")

    tappd = AsyncDstackClient()

    try:
        # 1) TCB info (InfoResponse[TcbInfoV03x])
        info_resp = await tappd.info()

        tcb_info = json.dumps(
            info_resp.tcb_info.model_dump(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

        print("✅ TCB Info retrieved successfully.")

        # 2) Quote
        quote_response = await tappd.get_quote(
            report_data=account_id
        )

        quote_hex = getattr(quote_response, "quote", None)
        if not isinstance(quote_hex, str) or not quote_hex:
            raise ValueError(f"Unexpected tdx_quote() response: {quote_response!r}")

        if quote_hex.startswith("0x"):
            quote_hex = quote_hex[2:]

        # 3) Upload quote to proof service
        files = {"hex": (None, quote_hex, "text/plain")}

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

        collateral = json.dumps(
            quote_collateral,
            ensure_ascii=False,
            separators=(",", ":"),
        )

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
        print(f"[ERROR] Unexpected failure fetching TEE info: {e}")
        print(f"[ERROR] Full error details: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}