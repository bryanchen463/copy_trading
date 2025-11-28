"""账户管理服务"""
import time
import secrets
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Account, CopyTrade, Transaction
import logging

logger = logging.getLogger(__name__)

class AccountService:
    """账户管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_account_info(self, wallet_address: str) -> Dict:
        """获取账户信息"""
        try:
            # 获取或创建账户
            account = self.db.query(Account).filter(
                Account.wallet_address == wallet_address
            ).first()
            
            if not account:
                account = Account(
                    wallet_address=wallet_address,
                    total_balance=0.0,
                    available_balance=0.0,
                    total_deposited=0.0,
                    total_withdrawn=0.0
                )
                self.db.add(account)
                self.db.commit()
            
            # 获取活跃持仓
            active_trades = self.db.query(CopyTrade).filter(
                and_(
                    CopyTrade.wallet_address == wallet_address,
                    CopyTrade.status == "active"
                )
            ).all()
            
            # 计算总收益
            all_trades = self.db.query(CopyTrade).filter(
                CopyTrade.wallet_address == wallet_address
            ).all()
            
            total_profit = sum(trade.profit for trade in all_trades)
            total_deposited = account.total_deposited or 0.0
            
            # 计算收益率
            if total_deposited > 0:
                total_profit_rate = (total_profit / total_deposited) * 100
            else:
                total_profit_rate = 0.0
            
            # 计算已用保证金
            used_margin = sum(trade.amount * trade.leverage for trade in active_trades)
            
            # 构建持仓列表
            positions = []
            for trade in active_trades:
                positions.append({
                    "vault_address": trade.vault_address,
                    "vault_name": trade.vault_name,
                    "amount": trade.amount,
                    "profit": trade.profit,
                    "profit_rate": trade.profit_rate,
                    "status": trade.status,
                    "leverage": trade.leverage
                })
            
            # 更新账户总余额（基于实际计算）
            account.total_balance = account.total_deposited - account.total_withdrawn + total_profit
            account.available_balance = account.total_balance - used_margin
            account.last_updated = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "wallet_address": wallet_address,
                "total_balance": round(account.total_balance, 2),
                "available_balance": round(account.available_balance, 2),
                "total_profit": round(total_profit, 2),
                "total_profit_rate": round(total_profit_rate, 2),
                "active_positions": len(active_trades),
                "total_deposited": round(total_deposited, 2),
                "total_withdrawn": round(account.total_withdrawn or 0.0, 2),
                "used_margin": round(used_margin, 2),
                "positions": positions
            }
        except Exception as e:
            logger.error(f"获取账户信息失败: {str(e)}")
            raise
    
    def deposit(self, wallet_address: str, amount: float, transaction_hash: Optional[str] = None) -> Dict:
        """充值"""
        try:
            if amount <= 0:
                raise ValueError("充值金额必须大于0")
            
            account = self.db.query(Account).filter(
                Account.wallet_address == wallet_address
            ).first()
            
            if not account:
                account = Account(
                    wallet_address=wallet_address,
                    total_balance=0.0,
                    available_balance=0.0,
                    total_deposited=0.0
                )
                self.db.add(account)
            
            # 更新账户
            account.total_deposited += amount
            account.total_balance += amount
            account.available_balance += amount
            account.last_updated = datetime.utcnow()
            
            # 创建交易记录
            transaction = Transaction(
                id=f"tx_{int(time.time())}_{secrets.token_hex(4)}",
                wallet_address=wallet_address,
                type="deposit",
                amount=amount,
                status="completed",
                transaction_hash=transaction_hash,
                notes="账户充值"
            )
            self.db.add(transaction)
            
            self.db.commit()
            
            logger.info(f"充值成功: {wallet_address}, 金额: {amount}")
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "amount": amount,
                "transaction_hash": transaction_hash
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"充值失败: {str(e)}")
            raise
    
    def withdraw(self, wallet_address: str, amount: float) -> Dict:
        """提现"""
        try:
            if amount <= 0:
                raise ValueError("提取金额必须大于0")
            
            account = self.db.query(Account).filter(
                Account.wallet_address == wallet_address
            ).first()
            
            if not account:
                raise ValueError("账户不存在")
            
            if account.available_balance < amount:
                raise ValueError(f"可用余额不足，当前可用: ${account.available_balance:.2f}")
            
            # 更新账户
            account.total_withdrawn += amount
            account.total_balance -= amount
            account.available_balance -= amount
            account.last_updated = datetime.utcnow()
            
            # 生成交易哈希（实际应该调用链上交易）
            transaction_hash = f"0x{secrets.token_hex(32)}"
            
            # 创建交易记录
            transaction = Transaction(
                id=f"tx_{int(time.time())}_{secrets.token_hex(4)}",
                wallet_address=wallet_address,
                type="withdraw",
                amount=amount,
                status="completed",
                transaction_hash=transaction_hash,
                notes="账户提现"
            )
            self.db.add(transaction)
            
            self.db.commit()
            
            logger.info(f"提现成功: {wallet_address}, 金额: {amount}")
            
            return {
                "success": True,
                "message": "提取成功",
                "wallet_address": wallet_address,
                "amount": amount,
                "transaction_hash": transaction_hash
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"提现失败: {str(e)}")
            raise

