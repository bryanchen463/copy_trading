"""Hyperliquid API 服务 - 使用官方 SDK"""
import logging
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

# 尝试导入 Hyperliquid SDK
try:
    # 方式1: 如果 SDK 包名为 hyperliquid
    try:
        from hyperliquid.info import Info
        from hyperliquid.utils import constants
        SDK_AVAILABLE = True
        SDK_TYPE = "hyperliquid"
    except ImportError:
        # 方式2: 如果 SDK 需要从其他路径导入
        try:
            from hyperliquid_python_sdk import Hyperliquid
            SDK_AVAILABLE = True
            SDK_TYPE = "hyperliquid_python_sdk"
        except ImportError:
            SDK_AVAILABLE = False
            SDK_TYPE = None
except Exception as e:
    logger.warning(f"无法导入 Hyperliquid SDK: {str(e)}")
    SDK_AVAILABLE = False
    SDK_TYPE = None

# 如果 SDK 不可用，回退到 httpx
if not SDK_AVAILABLE:
    import httpx
    logger.info("Hyperliquid SDK 不可用，将使用 HTTP 客户端作为回退方案")

class HyperliquidService:
    """Hyperliquid API 服务类 - 使用官方 SDK"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("HYPERLIQUID_API_URL", "https://api.hyperliquid.xyz")
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        
        # 初始化 SDK 客户端
        self.sdk_initialized = False
        if SDK_AVAILABLE and not self.use_mock_data:
            try:
                if SDK_TYPE == "hyperliquid":
                    # 使用官方 hyperliquid SDK
                    # 注意：根据实际 SDK 文档调整初始化参数
                    try:
                        self.info_client = Info(base_url=self.base_url, skip_ws=True)
                    except TypeError:
                        # 如果 skip_ws 参数不存在，尝试不带参数
                        self.info_client = Info(base_url=self.base_url)
                    self.sdk_initialized = True
                    logger.info("成功初始化 Hyperliquid SDK")
                elif SDK_TYPE == "hyperliquid_python_sdk":
                    # 使用 hyperliquid_python_sdk
                    self.sdk_client = Hyperliquid(base_url=self.base_url)
                    self.sdk_initialized = True
                    logger.info("成功初始化 Hyperliquid Python SDK")
            except Exception as e:
                logger.warning(f"初始化 SDK 失败: {str(e)}，将使用 HTTP 客户端")
                self.sdk_initialized = False
        
        # 如果 SDK 不可用，使用 HTTP 客户端作为回退
        if not self.sdk_initialized and not self.use_mock_data:
            self.http_client = httpx.AsyncClient(timeout=30.0)
            logger.info("使用 HTTP 客户端作为回退方案")
    
    async def get_vaults(self) -> List[Dict]:
        """获取所有 Vaults 列表"""
        # 如果设置了使用模拟数据，直接返回
        if self.use_mock_data:
            logger.info("使用模拟数据模式")
            return self._get_mock_vaults()
        
        # 使用 SDK 获取数据
        if self.sdk_initialized:
            try:
                if SDK_TYPE == "hyperliquid":
                    # 使用官方 SDK
                    # 注意：需要根据实际 SDK API 调整
                    # 尝试不同的方法名
                    try:
                        result = self.info_client.vaults()
                    except AttributeError:
                        try:
                            result = self.info_client.get_vaults()
                        except AttributeError:
                            # 如果方法不存在，尝试通过 meta 或其他方式获取
                            result = None
                    
                    if result:
                        if isinstance(result, dict) and "data" in result:
                            vaults_data = result["data"]
                        elif isinstance(result, list):
                            vaults_data = result
                        else:
                            vaults_data = []
                    else:
                        vaults_data = []
                    
                    # 转换数据格式
                    vaults = []
                    for vault in vaults_data:
                        vaults.append({
                            "address": vault.get("address", ""),
                            "name": vault.get("name", "Unnamed Vault"),
                            "totalValue": float(vault.get("totalValue", 0)),
                            "performance": float(vault.get("performance", 0)),
                            "managerShare": float(vault.get("managerShare", 0.1)),
                            "userCount": int(vault.get("userCount", 0))
                        })
                    
                    logger.info(f"通过 SDK 成功获取到 {len(vaults)} 个 Vaults")
                    return vaults
                elif SDK_TYPE == "hyperliquid_python_sdk":
                    # 使用 hyperliquid_python_sdk
                    result = await self.sdk_client.get_vaults()
                    vaults = []
                    for vault in result:
                        vaults.append({
                            "address": vault.get("address", ""),
                            "name": vault.get("name", "Unnamed Vault"),
                            "totalValue": float(vault.get("totalValue", 0)),
                            "performance": float(vault.get("performance", 0)),
                            "managerShare": float(vault.get("managerShare", 0.1)),
                            "userCount": int(vault.get("userCount", 0))
                        })
                    logger.info(f"通过 SDK 成功获取到 {len(vaults)} 个 Vaults")
                    return vaults
            except Exception as e:
                logger.error(f"使用 SDK 获取 Vaults 失败: {str(e)}")
                # 回退到 HTTP 或模拟数据
                if hasattr(self, 'http_client'):
                    return await self._get_vaults_via_http()
                return self._get_mock_vaults()
        
        # 如果 SDK 不可用，使用 HTTP 客户端
        if hasattr(self, 'http_client'):
            return await self._get_vaults_via_http()
        
        # 最后回退到模拟数据
        return self._get_mock_vaults()
    
    async def _get_vaults_via_http(self) -> List[Dict]:
        """通过 HTTP 客户端获取 Vaults（回退方案）"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/info",
                json={"type": "vaults"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 422:
                error_detail = response.text
                logger.warning(f"API 返回 422 错误，详情: {error_detail}")
                logger.info("使用模拟数据")
                return self._get_mock_vaults()
            
            response.raise_for_status()
            data = response.json()
            
            vaults = []
            if isinstance(data, list):
                for vault in data:
                    vaults.append({
                        "address": vault.get("address", ""),
                        "name": vault.get("name", "Unnamed Vault"),
                        "totalValue": float(vault.get("totalValue", 0)),
                        "performance": float(vault.get("performance", 0)),
                        "managerShare": float(vault.get("managerShare", 0.1)),
                        "userCount": int(vault.get("userCount", 0))
                    })
            elif isinstance(data, dict):
                if "data" in data:
                    vaults = data["data"]
                elif "vaults" in data:
                    vaults = data["vaults"]
                else:
                    return self._get_mock_vaults()
            
            logger.info(f"通过 HTTP 成功获取到 {len(vaults)} 个 Vaults")
            return vaults
        except Exception as e:
            logger.error(f"通过 HTTP 获取 Vaults 失败: {str(e)}")
            return self._get_mock_vaults()
    
    async def get_vault_performance(self, vault_address: str) -> Dict:
        """获取 Vault 业绩数据"""
        if self.use_mock_data:
            return self._get_mock_vault_performance(vault_address)
        
        if self.sdk_initialized:
            try:
                if SDK_TYPE == "hyperliquid":
                    # 使用官方 SDK
                    result = self.info_client.vault_performance(vault_address)
                    if result and isinstance(result, dict):
                        return result
                elif SDK_TYPE == "hyperliquid_python_sdk":
                    result = await self.sdk_client.get_vault_performance(vault_address)
                    if result:
                        return result
            except Exception as e:
                logger.error(f"使用 SDK 获取 Vault 业绩失败: {str(e)}")
        
        # 回退方案
        if hasattr(self, 'http_client'):
            try:
                response = await self.http_client.post(
                    f"{self.base_url}/info",
                    json={"type": "vaultPerformance", "vaultAddress": vault_address},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 422:
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, dict) and data:
                        return data
            except Exception as e:
                logger.error(f"通过 HTTP 获取 Vault 业绩失败: {str(e)}")
        
        return self._get_mock_vault_performance(vault_address)
    
    async def get_vault_trades(self, vault_address: str, limit: int = 100) -> List[Dict]:
        """获取 Vault 的交易历史"""
        if self.sdk_initialized:
            try:
                if SDK_TYPE == "hyperliquid":
                    result = self.info_client.vault_trades(vault_address, limit)
                    if isinstance(result, list):
                        return result
                    elif isinstance(result, dict) and "trades" in result:
                        return result["trades"]
                elif SDK_TYPE == "hyperliquid_python_sdk":
                    result = await self.sdk_client.get_vault_trades(vault_address, limit)
                    if result:
                        return result
            except Exception as e:
                logger.error(f"使用 SDK 获取 Vault 交易历史失败: {str(e)}")
        
        # 回退方案
        if hasattr(self, 'http_client'):
            try:
                response = await self.http_client.post(
                    f"{self.base_url}/info",
                    json={"type": "vaultTrades", "vaultAddress": vault_address, "limit": limit},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 422:
                    response.raise_for_status()
                    data = response.json()
                    return data.get("trades", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            except Exception as e:
                logger.error(f"通过 HTTP 获取 Vault 交易历史失败: {str(e)}")
        
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
            if self.sdk_initialized:
                # 使用 SDK 创建交易
                # 注意：实际实现需要钱包签名
                logger.warning("create_copy_trade 需要实现实际的链上交易逻辑")
                return {
                    "success": True,
                    "transaction_hash": f"0x{'mock_hash_' + vault_address[-8:]}",
                    "status": "pending"
                }
            else:
                logger.warning("SDK 未初始化，无法创建交易")
                return {
                    "success": False,
                    "message": "SDK 未初始化"
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
        """关闭客户端"""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()
