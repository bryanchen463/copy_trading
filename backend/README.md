# 后端服务说明

## 数据库初始化

首次运行时会自动创建数据库文件 `copy_trading.db`。

## 环境变量

创建 `.env` 文件：

```env
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
DATABASE_URL=sqlite:///./copy_trading.db
# 设置为 true 时，将始终使用模拟数据，不调用真实 API
USE_MOCK_DATA=false
```

## 关于 Hyperliquid API 422 错误

如果遇到 HTTP 422 错误，可能的原因：

1. **API 格式已更改**: Hyperliquid API 的请求格式可能已更新，需要参考最新文档
2. **API 端点变更**: 某些端点可能需要不同的请求格式或参数
3. **认证要求**: 某些 API 可能需要认证或特殊权限

**解决方案**:
- 系统会自动回退到模拟数据，确保开发可以继续进行
- 查看日志中的详细错误信息
- 参考 [Hyperliquid 官方文档](https://hyperliquid.gitbook.io/) 更新 API 调用格式
- 或者设置 `USE_MOCK_DATA=true` 直接使用模拟数据

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

