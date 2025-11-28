# 后端服务说明

## 数据库初始化

首次运行时会自动创建数据库文件 `copy_trading.db`。

## 环境变量

创建 `.env` 文件：

```env
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
DATABASE_URL=sqlite:///./copy_trading.db
```

## 运行服务

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload
```

## API 文档

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

## 数据库结构

- `copy_trades`: 跟单交易记录
- `accounts`: 账户信息
- `transactions`: 交易记录（充值、提现等）
- `vault_snapshots`: Vault 快照（历史数据）

