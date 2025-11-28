from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./copy_trading.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # 设置为 True 可以查看 SQL 语句
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型
Base = declarative_base()

# 数据模型
class CopyTrade(Base):
    """跟单交易记录"""
    __tablename__ = "copy_trades"
    
    id = Column(String, primary_key=True, index=True)
    wallet_address = Column(String, index=True, nullable=False)
    vault_address = Column(String, index=True, nullable=False)
    vault_name = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    leverage = Column(Float, default=1.0)
    status = Column(String, default="active")  # active, closed, cancelled
    profit = Column(Float, default=0.0)
    profit_rate = Column(Float, default=0.0)
    transaction_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

class Account(Base):
    """账户信息"""
    __tablename__ = "accounts"
    
    wallet_address = Column(String, primary_key=True, index=True)
    total_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    total_deposited = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(Base):
    """交易记录（充值、提现等）"""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, index=True)
    wallet_address = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # deposit, withdraw, copy_trade
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    transaction_hash = Column(String, nullable=True)
    related_trade_id = Column(String, nullable=True)  # 如果是跟单交易相关
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

class VaultSnapshot(Base):
    """Vault 快照（用于记录历史数据）"""
    __tablename__ = "vault_snapshots"
    
    id = Column(String, primary_key=True, index=True)
    vault_address = Column(String, index=True, nullable=False)
    vault_name = Column(String, nullable=True)
    total_value = Column(Float, nullable=False)
    performance = Column(Float, default=0.0)
    user_count = Column(Integer, default=0)
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False)

# 创建所有表
def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

