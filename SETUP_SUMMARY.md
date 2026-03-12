# Twitter Workflow 配置总结

## ✅ 已完成的配置

### 1. 频率限制配置

**配置文件**: `config.json`

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

**说明**:
- ✅ 每 3 分钟执行一次
- ✅ 每小时最多 20 次
- ✅ 每天最多 100 次

---

### 2. AI 服务配置

**配置文件**: `.env`

**当前状态**: ⚠️  需要配置 AI API Key

**可用选项**:

#### 选项 A：火山引擎（当前不可用）
- ❌ 需要激活模型服务
- ❌ 所有测试模型都返回 404

#### 选项 B：DeepSeek（推荐）
- ✅ 无需激活，注册即可用
- ✅ 价格便宜（约 ¥0.002/千 tokens）
- ✅ 中文支持好

**配置步骤**:
1. 访问 https://platform.deepseek.com/api_keys
2. 注册账号并创建 API Key
3. 更新 `.env` 文件：
   ```bash
   DEEPSEEK_API_KEY=sk-your-actual-key-here
   AI_PROVIDER=deepseek
   ```

---

### 3. Twitter Cookie

**状态**: ✅ 已配置

**文件**: `twitter_cookies.json`

**说明**: Cookie 已保存，可以正常访问 Twitter 获取推文。

---

### 4. Telegram 推送

**状态**: ✅ 已配置

**配置**:
- Bot Token: `your-telegram-bot-token-here`
- Chat ID: `8627317531`

---

## 🧪 测试工具

### 火山引擎 API 测试

```bash
cd /home/ubuntu/twitter-workflow
python3 test_volc_api.py
```

**功能**:
- 测试所有可用的火山引擎模型
- 自动更新推荐模型到 `.env`
- 显示详细的错误信息

### DeepSeek API 测试

```bash
cd /home/ubuntu/twitter-workflow
python3 -c "
from reply_generator import ReplyGenerator
generator = ReplyGenerator(provider='deepseek')
replies = generator.generate_replies('Test tweet', 'user', 3)
print(replies)
"
```

---

## 📋 待办事项

### 必须完成

- [ ] **配置 DeepSeek API Key**
  1. 访问 https://platform.deepseek.com/api_keys
  2. 注册并获取 API Key
  3. 更新 `.env` 文件中的 `DEEPSEEK_API_KEY`

### 可选优化

- [ ] 添加更多 AI 服务提供商（OpenAI、Claude 等）
- [ ] 改进推文搜索算法
- [ ] 添加推文内容过滤器
- [ ] 支持多账号管理

---

## 🚀 快速开始

配置好 DeepSeek API Key 后：

```bash
cd /home/ubuntu/twitter-workflow

# 1. 测试 AI 服务
python3 -c "from reply_generator import ReplyGenerator; ReplyGenerator(provider='deepseek')"

# 2. 运行工作流
python3 main.py

# 3. 查看频率限制状态
python3 main.py --check-rate
```

---

## 📊 当前配置概览

| 配置项 | 状态 | 说明 |
|--------|------|------|
| Twitter Cookie | ✅ 有效 | 可正常获取推文 |
| Telegram 推送 | ✅ 已配置 | Bot + Chat ID |
| 频率限制 | ✅ 3 分钟 | 可调整 |
| AI 服务 | ⚠️  待配置 | 需要 DeepSeek API Key |
| 搜索模式 | ✅ 首页模式 | 获取最新推文 |

---

## 💡 故障排查

### 问题 1: AI 服务不可用

**症状**: `Error code: 404` 或 `API Key 未提供`

**解决**:
```bash
# 1. 检查 .env 配置
cat .env | grep DEEPSEEK

# 2. 确保 API Key 正确
# 3. 测试连接
python3 test_volc_api.py
```

### 问题 2: 频率限制阻止运行

**症状**: `距离上次运行仅 X 分钟，需等待 Y 分钟`

**解决**:
```bash
# 临时禁用频率限制
# 编辑 config.json，设置 "enabled": false

# 或者等待指定时间
```

### 问题 3: Twitter Cookie 过期

**症状**: `Twitter 未登录`

**解决**:
```bash
# 重新导入 Cookie
python3 import_twitter_cookies.py
```

---

## 📞 获取帮助

- DeepSeek API 文档：https://platform.deepseek.com/docs
- 项目 Issues: https://github.com/yynomad/twitter-workflow/issues
