# Twitter 自动回复工作流

一个**半自动化**的 Twitter 运营工具，使用 AI 生成回复建议，通过 Telegram 推送，人工审核后发布。

**核心优势**：无需 Twitter API，使用浏览器自动化 + AI 翻译 + 半自动审核

---

## 🚀 功能特点

| 功能 | 说明 |
|------|------|
| 🔍 **智能搜索** | Playwright 浏览器自动化，无需 Twitter API |
| 🤖 **AI 回复生成** | 火山方舟 DeepSeek-V3.2，生成 3 条不同风格回复 |
| 🌐 **多语言翻译** | 英文/日文推文自动翻译成中文 |
| 📱 **Telegram 推送** | 实时推送推文和回复建议 |
| ✋ **半自动审核** | 人工审核后发布，确保质量 |
| ⏱️ **频率控制** | 可配置执行间隔，避免风控 |
| 🔒 **安全配置** | 环境变量管理，Pre-commit 检查 |

---

## 📋 快速开始

### 1️⃣ 安装依赖

```bash
cd twitter-workflow
pip3 install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2️⃣ 配置环境变量

```bash
cp .env.example .env
vim .env
```

**必须配置**：
```bash
# 火山方舟 AI（推荐）
VOLC_API_KEY=your-api-key-here
VOLC_API_BASE=https://ark.cn-beijing.volces.com/api/coding/v3
VOLC_MODEL=DeepSeek-V3.2

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here

# AI 服务提供商
AI_PROVIDER=volc
```

### 3️⃣ 登录 Twitter

```bash
python3 login_twitter.py
```

会打开浏览器，手动登录 Twitter，Cookie 会自动保存。

### 4️⃣ 配置搜索条件

编辑 `.env` 文件：
```bash
# 搜索关键词（空字符串表示获取首页推文）
TWITTER_SEARCH_QUERY="AI OR 人工智能"

# 筛选条件
TWITTER_MIN_LIKES=10
TWITTER_MIN_VIEWS=0

# 时间范围（小时）
TWITTER_HOURS=24

# 获取数量
TWITTER_NUM_TWEETS=1

# 选择模式：random（随机）, latest（最新）, top（最热）
TWITTER_SELECTION_MODE=random
```

### 5️⃣ 运行工作流

```bash
# 正式运行
python3 main.py

# 查看配置
python3 main.py --show-config

# 检查频率限制
python3 main.py --check-rate
```

---

## 🔄 工作流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  登录 Twitter  │ ──► │  搜索/抓取  │ ──► │  AI 生成回复  │
│  (Cookie)    │     │  推文       │     │  (带翻译)    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  人工审核    │ ◄── │  Telegram   │ ◄── │  选择最佳   │
│  发布回复    │     │  推送消息    │     │  回复       │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 📊 配置说明

### 环境变量（.env）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VOLC_API_KEY` | 火山方舟 API Key | - |
| `VOLC_API_BASE` | API 基础 URL | `https://ark.cn-beijing.volces.com/api/coding/v3` |
| `VOLC_MODEL` | 模型名称 | `DeepSeek-V3.2` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | - |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | - |
| `TWITTER_SEARCH_QUERY` | 搜索关键词 | `""` |
| `TWITTER_MIN_LIKES` | 最小点赞数 | `0` |
| `TWITTER_HOURS` | 时间范围（小时） | `0` |
| `TWITTER_NUM_TWEETS` | 获取数量 | `1` |
| `TWITTER_SELECTION_MODE` | 选择模式 | `random` |

**优先级**：环境变量 > config.json

### config.json

```json
{
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 3,
    "max_per_hour": 20,
    "max_per_day": 100
  },
  "reply": {
    "custom_instructions": "回复要友好、有建设性",
    "language": "中文",
    "styles": ["专业", "幽默", "友好"]
  },
  "telegram": {
    "enabled": true,
    "batch_send": false
  }
}
```

---

## 🌐 多语言支持

### 自动翻译

| 推文语言 | 处理方式 |
|----------|----------|
| 英文 | ✅ 自动翻译成中文 |
| 日文 | ✅ 自动翻译成中文 |
| 中文 | ✅ 不翻译 |

### Telegram 消息格式

```
📌 推文内容
[英文/日文原文]

[翻译]
[中文翻译]

---
💡 回复建议 1:
[风格描述]
[英文/日文回复]

[翻译]
[中文回复]
```

---

## 🔍 Twitter 搜索语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `OR` | 或 | `AI OR 人工智能` |
| `min_faves:N` | 最小点赞数 | `min_faves:100` |
| `min_retweets:N` | 最小转发数 | `min_retweets:50` |
| `-filter:replies` | 排除回复 | `AI -filter:replies` |
| `-filter:retweets` | 排除转推 | `AI -filter:retweets` |
| `from:username` | 指定用户 | `from:elonmusk` |
| `lang:en` | 指定语言 | `lang:en` |

---

## 🛡️ 安全配置

### Pre-commit Hook（已安装）

自动检测敏感信息：
- ❌ API Key 格式
- ❌ Telegram Token
- ❌ .env 文件提交
- ⚠️ 硬编码密码

### .gitignore（已配置）

```bash
.env
twitter_cookies.json
processed_tweets.json
rate_limit_state.json
*.log
```

### 安全检查

```bash
# 手动检查
python3 ~/.npm-global/lib/node_modules/openclaw/skills/security-check/security_check.py --staged
```

---

## 📁 项目结构

```
twitter-workflow/
├── main.py                 # 主工作流脚本
├── twitter_scraper.py      # Twitter 爬虫（Playwright）
├── reply_generator.py      # AI 回复生成（支持翻译）
├── telegram_bot.py         # Telegram 推送
├── login_twitter.py        # Twitter 登录脚本
├── get_chat_id.py          # 获取 Telegram Chat ID
├── config.json             # 基础配置
├── .env                    # 环境变量（不提交）
├── .env.example            # 配置模板
├── .gitignore              # Git 忽略配置
├── requirements.txt        # Python 依赖
└── README.md               # 本文档
```

---

## ⚙️ 高级用法

### 定时任务

```bash
# 每 3 分钟执行一次（与频率限制匹配）
*/3 * * * * cd /path/to/twitter-workflow && python3 main.py >> workflow.log 2>&1
```

### 调试模式

```bash
# 显示浏览器
python3 main.py --visible

# 测试运行（不发送）
python3 main.py --dry-run
```

### 临时覆盖配置

```bash
# 临时使用不同搜索词
TWITTER_SEARCH_QUERY="machine learning" python3 main.py
```

---

## ❓ 常见问题

### Q: Cookie 过期了怎么办？

**A**: 重新运行 `python3 login_twitter.py` 登录即可。

### Q: 搜索结果为 0？

**A**: 放宽筛选条件：
```bash
TWITTER_MIN_LIKES=0
TWITTER_HOURS=24
TWITTER_SEARCH_QUERY=""  # 使用首页模式
```

### Q: Telegram 收不到消息？

**A**: 检查：
1. Bot Token 是否正确
2. Chat ID 是否正确
3. 是否给机器人发送过消息

### Q: AI 回复质量不好？

**A**: 调整 `reply.custom_instructions`：
```json
{
  "reply": {
    "custom_instructions": "回复要专业、简洁，避免过度营销"
  }
}
```

---

## 📚 相关文档

- **SECURITY.md** - 安全配置指南
- **.env.example** - 配置模板

---

## 🎯 最佳实践

### ✅ 推荐

1. 使用环境变量管理敏感信息
2. 合理设置频率限制（3-5 分钟）
3. 定期更换 Cookie
4. 人工审核后再发布
5. 使用 Pre-commit 检查

### ❌ 避免

1. 硬编码 API Key/Token
2. 频率过高（可能被封）
3. 完全自动化（可能违规）
4. 提交 .env 到 git

---

## 📝 更新日志

### v2.0 (2026-03-14)
- ✅ 支持环境变量配置
- ✅ 多语言翻译（英文/日文→中文）
- ✅ Pre-commit 安全检查
- ✅ 清理敏感信息

### v1.0 (2026-03-11)
- ✅ 基础工作流
- ✅ AI 回复生成
- ✅ Telegram 推送

---

## 📄 License

MIT License

---

## 🙏 致谢

- **火山方舟** - AI 模型服务
- **Telegram** - 消息推送
- **Playwright** - 浏览器自动化

---

**开始你的 Twitter 半自动化运营吧！** 🚀
