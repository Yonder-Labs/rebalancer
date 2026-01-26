import json
import traceback
import httpx

from dstack_sdk import AsyncTappdClient
from tee import KeyPairGenerator


async def get_tee_info(agent_account: KeyPairGenerator):
    print(f"✅ Registering agent for account: {agent_account.account_id}")
    try:
            
        tcb_info_dict = await AsyncTappdClient().get_info()
        print("✅ TCB Info retrieved successfully.")
        print("TCB Info:", tcb_info_dict)
        
        parsed_tcb_info = json.loads(tcb_info_dict["tcb_info"])
                
        tcb_info = json.dumps(parsed_tcb_info, ensure_ascii=False, separators=(',', ':'))

        quote_response = await AsyncTappdClient().tdx_quote(
            report_data=agent_account.account_id,
            hash_algorithm='raw'
        )
        
        quote_hex = quote_response.quote

        if quote_hex.startswith('0x'):
            quote_hex = quote_hex[2:] 
                
        files = {
            'hex': (None, quote_hex, 'text/plain')  # (filename, data, content_type)
        }
                
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://proof.t16z.com/api/upload',
                files=files,
                headers={'Accept': 'application/json'}
            )
            
            response.raise_for_status()
            res_data = response.json()
                    
            checksum = res_data['checksum']
            collateral = json.dumps(res_data['quote_collateral'])
        
        return {
            "quote_hex": quote_hex,
            "collateral": collateral,
            "checksum": checksum,
            "tcb_info": tcb_info
        }
    
    except Exception as e:
        print(f"[ERROR] Failed to register worker: {str(e)}")
        print(f"[ERROR] Full error details: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}
        