"""跟单交易服务"""
import time
import secrets
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import CopyTrade, Account, Transaction, VaultSnapshot
import logging

logger = logging.getLogger(__name__)

class TradeService:
    """跟单交易服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_copy_trade(
        self,
        wallet_address: str,
        vault_address: str,
        vault_name: str,
        amount: float,
        leverage: float = 1.0
    ) -> Dict:
        """创建跟单交易"""
        try:
            # 生成交易ID
            trade_id = f"trade_{int(time.time())}_{secrets.token_hex(4)}"
            
            # 检查账户余额
            account = self.db.query(Account).filter(
                Account.wallet_address == wallet_address
            ).first()
            
            if not account:
                # 创建新账户
                account = Account(
                    wallet_address=wallet_address,
                    total_balance=0.0,
                    available_balance=0.0,
                    total_deposited=0.0
                )
                self.db.add(account)
                self.db.commit()
            
            # 检查可用余额（这里简化处理，实际应该检查链上余额）
            required_balance = amount * leverage
            if account.available_balance < required_balance:
                raise ValueError(f"可用余额不足，需要 ${required_balance:.2f}，当前可用 ${account.available_balance:.2f}")
            
            # 创建跟单交易记录
            copy_trade = CopyTrade(
                id=trade_id,
                wallet_address=wallet_address,
                vault_address=vault_address,
                vault_name=vault_name,
                amount=amount,
                leverage=leverage,
                status="active",
                profit=0.0,
                profit_rate=0.0
            )
            
            self.db.add(copy_trade)
            
            # 更新账户余额
            account.available_balance -= required_balance
            
            # 创建交易记录
            transaction = Transaction(
                id=f"tx_{int(time.time())}_{secrets.token_hex(4)}",
                wallet_address=wallet_address,
                type="copy_trade",
                amount=amount,
                status="completed",
                related_trade_id=trade_id,
                notes=f"跟单交易: {vault_name}"
            )
            self.db.add(transaction)
            
            self.db.commit()
            self.db.refresh(copy_trade)
            
            logger.info(f"创建跟单交易成功: {trade_id}, 钱包: {wallet_address}, 金额: {amount}")
            
            return {
                "success": True,
                "trade_id": trade_id,
                "vault_address": vault_address,
                "amount": amount,
                "leverage": leverage,
                "wallet_address": wallet_address,
                "status": "active"
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建跟单交易失败: {str(e)}")
            raise
    
    def get_account_trades(
        self,
        wallet_address: str,
        vault_address: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """获取账户的交易历史"""
        try:
            query = self.db.query(CopyTrade).filter(
                CopyTrade.wallet_address == wallet_address
            )
            
            # 应用筛选条件
            if vault_address:
                query = query.filter(CopyTrade.vault_address == vault_address)
            
            if start_time:
                start_dt = datetime.fromtimestamp(start_time)
                query = query.filter(CopyTrade.created_at >= start_dt)
            
            if end_time:
                end_dt = datetime.fromtimestamp(end_time)
                query = query.filter(CopyTrade.created_at <= end_dt)
            
            # 获取总数
            total = query.count()
            
            # 分页
            trades = query.order_by(CopyTrade.created_at.desc()).offset(offset).limit(limit).all()
            
            # 转换为字典
            trades_list = []
            for trade in trades:
                trades_list.append({
                    "id": trade.id,
                    "vault_address": trade.vault_address,
                    "vault_name": trade.vault_name,
                    "type": "copy_trade",
                    "amount": trade.amount,
                    "leverage": trade.leverage,
                    "profit": trade.profit,
                    "profit_rate": trade.profit_rate,
                    "status": trade.status,
                    "created_at": int(trade.created_at.timestamp()),
                    "updated_at": int(trade.updated_at.timestamp()) if trade.updated_at else None
                })
            
            return {
                "trades": trades_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"获取交易历史失败: {str(e)}")
            raise
    
    def update_trade_profit(
        self,
        trade_id: str,
        profit: float,
        profit_rate: float
    ) -> bool:
        """更新交易收益"""
        try:
            trade = self.db.query(CopyTrade).filter(CopyTrade.id == trade_id).first()
            if not trade:
                return False
            
            old_profit = trade.profit
            trade.profit = profit
            trade.profit_rate = profit_rate
            trade.updated_at = datetime.utcnow()
            
            # 更新账户余额
            account = self.db.query(Account).filter(
                Account.wallet_address == trade.wallet_address
            ).first()
            
            if account:
                # 更新总余额（加上收益变化）
                profit_diff = profit - old_profit
                account.total_balance += profit_diff
                account.available_balance += profit_diff
            
            self.db.commit()
            logger.info(f"更新交易收益成功: {trade_id}, 收益: {profit}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新交易收益失败: {str(e)}")
            return False
    
    def close_trade(self, trade_id: str) -> bool:
        """关闭交易"""
        try:
            trade = self.db.query(CopyTrade).filter(CopyTrade.id == trade_id).first()
            if not trade:
                return False
            
            if trade.status != "active":
                return False
            
            trade.status = "closed"
            trade.closed_at = datetime.utcnow()
            trade.updated_at = datetime.utcnow()
            
            # 释放保证金
            account = self.db.query(Account).filter(
                Account.wallet_address == trade.wallet_address
            ).first()
            
            if account:
                # 释放保证金并加上收益
                released_amount = trade.amount * trade.leverage
                account.available_balance += released_amount + trade.profit
            
            self.db.commit()
            logger.info(f"关闭交易成功: {trade_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"关闭交易失败: {str(e)}")
            return False

