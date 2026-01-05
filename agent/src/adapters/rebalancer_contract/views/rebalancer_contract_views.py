import ast
from engine_types import TxType
from utils import parse_activity_log, parse_chain_configs, parse_u32_result, parse_supported_chains
from ..parsers import parse_active_session_info
from ..common import _RebalancerBase

class RebalancerContractViews(_RebalancerBase):
    async def get_all_configs(self):
        chain_config_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_all_configs",
            args={}
        )
        return parse_chain_configs(chain_config_raw)

    async def get_source_chain(self):
        source_chain_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_source_chain",
            args={}
        )
        return parse_u32_result(source_chain_raw)

    async def get_supported_chains(self) -> list[int]:
        supported_chains_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_supported_chains",
            args={}
        )
        return parse_supported_chains(supported_chains_raw)
    
    async def get_active_session_info(self):
        active_session_info = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_active_session_info",
            args={}
        )
        return parse_active_session_info(active_session_info)
    
    async def get_activity_log(self):
        activity_log_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_activity_log",
            args={}
        )
        return parse_activity_log(activity_log_raw)
    
    async def get_signed_payload(self, payload_type: TxType) -> bytes | None:
        print(f"Fetching signed payload for type: {payload_type.name} ({payload_type.value})")
        print(f"payload_type as u8: {payload_type.as_u8}    ")
        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_signed_payload",
            args={"step": payload_type.value}
        )
        
        print(f"get_signed_payload response: {response}")

        if not hasattr(response, "result") or response.result is None:
            return None
        
        print(f"get_signed_payload raw result: {response.result}")

        raw = bytes(response.result).decode("utf-8")

        if raw == "null":
            return None
    
        int_list = ast.literal_eval(raw)
        payload = bytes(int_list)

        signed_rlp = payload[1:]
        
        return signed_rlp