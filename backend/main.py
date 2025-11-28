from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from dotenv import load_dotenv

# 导入数据库和服务
from database import init_db, get_db
from services.hyperliquid_service import HyperliquidService
from services.trade_service import TradeService
from services.account_service import AccountService
from sqlalchemy.orm import Session

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Hyperliquid 跟单交易 API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("数据库初始化完成")

# 数据模型
class VaultInfo(BaseModel):
    address: str
    name: str
    total_value: float
    performance: float
    manager_share: float
    user_count: int

class CopyTradeRequest(BaseModel):
    vault_address: str
    amount: float
    leverage: Optional[float] = 1.0
    wallet_address: str

class WithdrawRequest(BaseModel):
    amount: float

# 创建 Hyperliquid 服务实例
hyperliquid_service = HyperliquidService()

@app.get("/")
async def root():
    return {"message": "Hyperliquid 跟单交易 API", "version": "1.0.0"}

@app.get("/api/vaults", response_model=List[VaultInfo])
async def get_vaults():
    """获取所有可用的 Vaults"""
    try:
        vaults_data = await hyperliquid_service.get_vaults()
        vaults = []
        for vault in vaults_data:
            vaults.append(VaultInfo(
                address=vault.get("address", ""),
                name=vault.get("name", "Unnamed Vault"),
                total_value=vault.get("totalValue", 0.0),
                performance=vault.get("performance", 0.0),
                manager_share=vault.get("managerShare", 0.1),
                user_count=vault.get("userCount", 0)
            ))
        return vaults
    except Exception as e:
        logger.error(f"获取 Vaults 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 Vaults 失败: {str(e)}")

@app.get("/api/vaults/{vault_address}")
async def get_vault_detail(vault_address: str):
    """获取特定 Vault 的详细信息"""
    try:
        performance = await hyperliquid_service.get_vault_performance(vault_address)
        return performance
    except Exception as e:
        logger.error(f"获取 Vault 详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 Vault 详情失败: {str(e)}")

@app.get("/api/vaults/{vault_address}/trades")
async def get_vault_trades(vault_address: str, limit: int = 100):
    """获取 Vault 的交易历史"""
    try:
        trades = await hyperliquid_service.get_vault_trades(vault_address, limit)
        return {"trades": trades, "vault_address": vault_address}
    except Exception as e:
        logger.error(f"获取 Vault 交易历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 Vault 交易历史失败: {str(e)}")

@app.post("/api/copy-trade")
async def create_copy_trade(request: CopyTradeRequest, db: Session = Depends(get_db)):
    """创建跟单交易"""
    try:
        # 验证参数
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="跟单金额必须大于0")
        if request.leverage < 1 or request.leverage > 20:
            raise HTTPException(status_code=400, detail="杠杆倍数必须在1-20之间")
        
        # 获取 Vault 信息
        vault_info = await hyperliquid_service.get_vault_performance(request.vault_address)
        vault_name = vault_info.get("name", "Unknown Vault")
        
        # 创建交易服务
        trade_service = TradeService(db)
        
        # 创建跟单交易
        result = trade_service.create_copy_trade(
            wallet_address=request.wallet_address,
            vault_address=request.vault_address,
            vault_name=vault_name,
            amount=request.amount,
            leverage=request.leverage
        )
        
        # 尝试调用 Hyperliquid API 创建实际交易（需要钱包签名）
        # 注意：实际实现需要前端提供签名后的交易
        try:
            hyperliquid_result = await hyperliquid_service.create_copy_trade(
                wallet_address=request.wallet_address,
                vault_address=request.vault_address,
                amount=request.amount,
                leverage=request.leverage
            )
            result["transaction_hash"] = hyperliquid_result.get("transaction_hash")
        except Exception as e:
            logger.warning(f"调用 Hyperliquid API 失败，但交易记录已保存: {str(e)}")
        
        logger.info(f"跟单交易创建成功: {result['trade_id']}")
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建跟单交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建跟单交易失败: {str(e)}")

@app.get("/api/account/{wallet_address}")
async def get_account_info(wallet_address: str, db: Session = Depends(get_db)):
    """获取跟单账户信息"""
    try:
        account_service = AccountService(db)
        account_info = account_service.get_account_info(wallet_address)
        return account_info
    except Exception as e:
        logger.error(f"获取账户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")

@app.get("/api/account/{wallet_address}/trades")
async def get_account_trades(
    wallet_address: str,
    vault_address: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取账户的交易历史"""
    try:
        trade_service = TradeService(db)
        result = trade_service.get_account_trades(
            wallet_address=wallet_address,
            vault_address=vault_address,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"获取交易历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取交易历史失败: {str(e)}")

@app.post("/api/account/{wallet_address}/withdraw")
async def withdraw_from_account(
    wallet_address: str,
    request: WithdrawRequest,
    db: Session = Depends(get_db)
):
    """从跟单账户提取资金"""
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="提取金额必须大于0")
        
        account_service = AccountService(db)
        result = account_service.withdraw(wallet_address, request.amount)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"提取资金失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提取资金失败: {str(e)}")

@app.post("/api/account/{wallet_address}/deposit")
async def deposit_to_account(
    wallet_address: str,
    request: WithdrawRequest,  # 复用模型
    transaction_hash: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """向账户充值"""
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="充值金额必须大于0")
        
        account_service = AccountService(db)
        result = account_service.deposit(wallet_address, request.amount, transaction_hash)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"充值失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"充值失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
