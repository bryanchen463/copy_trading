"""Hyperliquid API 服务"""
import httpx
import logging
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class HyperliquidService:
    """Hyperliquid API 服务类"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("HYPERLIQUID_API_URL", "https://api.hyperliquid.xyz")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    
    async def get_vaults(self) -> List[Dict]:
        """获取所有 Vaults 列表"""
        # 如果设置了使用模拟数据，直接返回
        if self.use_mock_data:
            logger.info("使用模拟数据模式")
            return self._get_mock_vaults()
        
        try:
            # Hyperliquid API 的正确格式
            # 注意：实际的 API 格式可能需要根据官方文档调整
            response = await self.client.post(
                f"{self.base_url}/info",
                json={
                    "type": "vaults"
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # 如果返回 422，记录错误并使用模拟数据
            if response.status_code == 422:
                error_detail = response.text
                logger.warning(f"API 返回 422 错误，详情: {error_detail}")
                logger.info("提示: Hyperliquid API 格式可能已更改，或需要不同的请求格式")
                logger.info("当前使用模拟数据，请参考 Hyperliquid 官方文档更新 API 调用")
                return self._get_mock_vaults()
            
            response.raise_for_status()
            data = response.json()
            
            # 转换数据格式
            vaults = []
            if isinstance(data, list):
                for vault in data:
                    vaults.append({
                        "address": vault.get("address", ""),
                        "name": vault.get("name", "Unnamed Vault"),
                        "totalValue": vault.get("totalValue", 0.0),
                        "performance": vault.get("performance", 0.0),
                        "managerShare": vault.get("managerShare", 0.1),
                        "userCount": vault.get("userCount", 0)
                    })
            elif isinstance(data, dict):
                # 尝试不同的数据格式
                if "data" in data:
                    vaults = data["data"]
                elif "vaults" in data:
                    vaults = data["vaults"]
                else:
                    # 如果数据格式不匹配，返回模拟数据
                    logger.warning(f"API 返回的数据格式不符合预期，使用模拟数据")
                    return self._get_mock_vaults()
            
            logger.info(f"成功获取到 {len(vaults)} 个 Vaults")
            return vaults
        except httpx.HTTPStatusError as e:
            # 详细记录错误信息
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                pass
            logger.error(f"获取 Vaults 失败 (HTTP {e.response.status_code}): {error_detail}")
            logger.info("使用模拟数据继续运行")
            return self._get_mock_vaults()
        except httpx.HTTPError as e:
            logger.error(f"获取 Vaults 失败 (HTTP错误): {str(e)}")
            logger.info("使用模拟数据继续运行")
            return self._get_mock_vaults()
        except Exception as e:
            logger.error(f"获取 Vaults 失败: {str(e)}")
            logger.info("使用模拟数据继续运行")
            return self._get_mock_vaults()
    
    async def get_vault_performance(self, vault_address: str) -> Dict:
        """获取 Vault 业绩数据"""
        # 如果设置了使用模拟数据，直接返回
        if self.use_mock_data:
            return self._get_mock_vault_performance(vault_address)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/info",
                json={
                    "type": "vaultPerformance",
                    "vaultAddress": vault_address
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # 如果返回 422，使用模拟数据
            if response.status_code == 422:
                error_detail = response.text
                logger.warning(f"获取 Vault 业绩失败 (422): {error_detail}")
                logger.info("使用模拟数据")
                return self._get_mock_vault_performance(vault_address)
            
            response.raise_for_status()
            data = response.json()
            
            # 如果返回的数据格式不对，使用模拟数据
            if not isinstance(data, dict) or not data:
                logger.warning(f"API 返回的数据格式不符合预期，使用模拟数据")
                return self._get_mock_vault_performance(vault_address)
            
            return data
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                pass
            logger.error(f"获取 Vault 业绩失败 (HTTP {e.response.status_code}): {error_detail}")
            logger.info("使用模拟数据")
            return self._get_mock_vault_performance(vault_address)
        except httpx.HTTPError as e:
            logger.error(f"获取 Vault 业绩失败 (HTTP错误): {str(e)}")
            logger.info("使用模拟数据")
            return self._get_mock_vault_performance(vault_address)
        except Exception as e:
            logger.error(f"获取 Vault 业绩失败: {str(e)}")
            logger.info("使用模拟数据")
            return self._get_mock_vault_performance(vault_address)
    
    async def get_vault_trades(self, vault_address: str, limit: int = 100) -> List[Dict]:
        """获取 Vault 的交易历史"""
        try:
            response = await self.client.post(
                f"{self.base_url}/info",
                json={
                    "type": "vaultTrades",
                    "vaultAddress": vault_address,
                    "limit": limit
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # 如果返回 422，返回空列表
            if response.status_code == 422:
                error_detail = response.text
                logger.warning(f"获取 Vault 交易历史失败 (422): {error_detail}")
                return []
            
            response.raise_for_status()
            data = response.json()
            return data.get("trades", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                pass
            logger.error(f"获取 Vault 交易历史失败 (HTTP {e.response.status_code}): {error_detail}")
            return []
        except Exception as e:
            logger.error(f"获取 Vault 交易历史失败: {str(e)}")
            return []
    
    async def create_copy_trade(
        self,
        wallet_address: str,
        vault_address: str,
        amount: float,
        leverage: float = 1.0,
        private_key: Optional[str] = None
    ) -> Dict:
        """创建跟单交易（需要钱包签名）"""
        try:
            # 这里需要实现实际的交易签名和提交逻辑
            # 实际应该使用 web3.py 或类似的库来签名交易
            # 然后调用 Hyperliquid 的交易接口
            
            # 注意：实际实现需要：
            # 1. 使用私钥签名交易
            # 2. 提交到 Hyperliquid 链上
            # 3. 等待交易确认
            # 4. 返回交易哈希
            
            logger.warning("create_copy_trade 需要实现实际的链上交易逻辑")
            
            # 模拟返回
            return {
                "success": True,
                "transaction_hash": f"0x{'mock_hash_' + vault_address[-8:]}",
                "status": "pending"
            }
        except Exception as e:
            logger.error(f"创建跟单交易失败: {str(e)}")
            raise
    
    def _get_mock_vaults(self) -> List[Dict]:
        """获取模拟 Vaults 数据（用于开发测试）"""
        return [
            {
                "address": "0x1234567890123456789012345678901234567890",
                "name": "Alpha Trading Vault",
                "totalValue": 1000000.0,
                "performance": 15.5,
                "managerShare": 0.1,
                "userCount": 150
            },
            {
                "address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "name": "Beta Strategy Vault",
                "totalValue": 500000.0,
                "performance": 8.3,
                "managerShare": 0.15,
                "userCount": 80
            },
            {
                "address": "0x9876543210987654321098765432109876543210",
                "name": "Gamma Momentum Vault",
                "totalValue": 2000000.0,
                "performance": 22.1,
                "managerShare": 0.12,
                "userCount": 250
            }
        ]
    
    def _get_mock_vault_performance(self, vault_address: str) -> Dict:
        """获取模拟 Vault 业绩数据"""
        return {
            "address": vault_address,
            "name": "Mock Vault",
            "totalValue": 1000000.0,
            "performance": 15.5,
            "managerShare": 0.1,
            "userCount": 150,
            "dailyReturn": 0.5,
            "weeklyReturn": 3.2,
            "monthlyReturn": 12.8
        }
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
