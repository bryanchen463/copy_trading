# Hyperliquid 跟单交易网站

一个基于 Hyperliquid 的去中心化跟单交易平台。

## 功能特性

### 核心功能

1. **跟单交易**
   - 浏览所有可用的 Vaults
   - 查看 Vault 详细信息和业绩表现
   - 设置跟单金额和杠杆倍数
   - 一键创建跟单交易

2. **查看交易历史**
   - 查看所有跟单交易记录
   - 支持按 Vault 地址筛选
   - 支持按时间范围筛选
   - 显示交易收益和收益率

3. **管理跟单账户**
   - 查看账户总资产和可用余额
   - 查看总收益和收益率
   - 查看当前持仓列表
   - 提取资金功能
   - 实时更新账户状态

## 技术栈

### 后端
- Python 3.9+
- FastAPI
- SQLAlchemy (SQLite)
- Hyperliquid API

### 前端
- Vue 3
- JavaScript
- Tailwind CSS
- Vite

## 安装和运行

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

后端服务将在 http://localhost:8000 启动

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 环境变量

在 `backend` 目录下创建 `.env` 文件并配置：

```env
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
DATABASE_URL=sqlite:///./copy_trading.db
```

## 数据库

项目使用 SQLite 数据库存储交易和账户数据。首次运行时会自动创建数据库文件 `backend/copy_trading.db`。

数据库表结构：
- `copy_trades`: 跟单交易记录
- `accounts`: 账户信息
- `transactions`: 交易记录（充值、提现等）
- `vault_snapshots`: Vault 快照（历史数据）

## API 文档

后端服务启动后，可以访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 许可证

MIT

