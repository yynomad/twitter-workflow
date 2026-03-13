# Twitter Workflow 配置说明

## 📋 当前配置

### .env 文件

```bash
# 火山方舟 - DeepSeek-V3.2
VOLC_API_KEY=abb7f1e5-37c6-4d6b-b6d3-66a0a9998630
VOLC_API_BASE=https://ark.cn-beijing.volces.com/api/v3
VOLC_MODEL=deepseek-v3-2-251201

# Telegram Bot
TELEGRAM_BOT_TOKEN=8624078810:AAEdRaxkQdE-of-XhOJIXDiOrABAgl16SYw
TELEGRAM_CHAT_ID=8627317531

# AI 服务
AI_PROVIDER=volc
```

---

## 🧪 测试用例

### 运行测试

```bash
cd /home/ubuntu/twitter-workflow
python3 test_api.py
```

### 测试内容

1. **基础 API 测试**
   - 测试火山方舟 API 连接
   - 测试 DeepSeek-V3.2 模型
   - 验证 Token 使用

2. **完整工作流测试**
   - 测试 AI 回复生成
   - 测试配置完整性
   - 验证所有服务

---

## 🔧 开通模型步骤

### 1. 访问控制台

```
https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement
```

### 2. 找到 DeepSeek-V3.2

- 在"模型服务"或"LLM"标签
- 搜索 `DeepSeek-V3.2` 或 `deepseek-v3-2-251201`

### 3. 开通模型

- 点击"开通"或"订阅"
- 确认价格（可能有免费额度）
- 完成开通

### 4. 测试

```bash
python3 test_api.py
```

---

## 🚀 运行工作流

测试通过后：

```bash
cd /home/ubuntu/twitter-workflow

# 运行工作流
python3 main.py

# 查看配置
python3 main.py --show-config

# 检查频率限制状态
python3 main.py --check-rate
```

---

## 📊 配置说明

### 频率限制

```json
{
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 3,
    "max_per_hour": 20,
    "max_per_day": 100
  }
}
```

- 每 **3 分钟** 执行一次
- 每小时最多 **20 次**
- 每天最多 **100 次**

### AI 模型

- **模型**: `deepseek-v3-2-251201` (DeepSeek-V3.2)
- **提供商**: 火山方舟
- **用途**: 生成 Twitter 回复

### Twitter 获取

- **模式**: 首页最新推文
- **数量**: 每次获取 1 条
- **选择**: 最新的一条

### Telegram 推送

- **Bot**: `@TarsAlwaysBot`
- **Chat ID**: `8627317531`
- **功能**: 推送推文和 AI 生成的回复

---

## ⚠️ 常见问题

### Q: 模型返回 404 错误

**A**: 模型未开通

```
Error code: 404 - ModelNotOpen
```

**解决**:
1. 访问控制台开通模型
2. 等待几分钟生效
3. 重新测试

### Q: API Key 无效

**A**: 检查 .env 配置

```bash
cat .env | grep VOLC_API_KEY
```

### Q: Twitter Cookie 过期

**A**: 重新导入 Cookie

```bash
python3 import_twitter_cookies.py
```

---

## 📞 获取帮助

- 火山方舟文档：https://www.volcengine.com/docs/82379/2183190
- 项目 Issues: https://github.com/yynomad/twitter-workflow/issues
