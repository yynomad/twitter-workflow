# Twitter 自动回复工作流

一个**半自动化**的 Twitter 运营工具，使用 AI 生成回复建议，通过 Telegram 推送，人工审核后发布。

**核心优势**：无需 Twitter API，使用浏览器自动化 + AI 生成 + 半自动审核

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

---

## 📋 快速开始

### 1️⃣ 安装依赖

```bash
cd twitter-workflow
pip3 install -r requirements.txt
playwright install chromium
```

### 2️⃣ 配置环境变量

```bash
cp .env.example .env
vim .env
```

**必须配置**：
```bash
# 火山方舟 AI
VOLC_API_KEY=your-api-key-here
VOLC_API_BASE=https://ark.cn-beijing.volces.com/api/coding/v3
VOLC_MODEL=DeepSeek-V3.2

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```

### 3️⃣ 登录 Twitter

```bash
python3 main.py --login
```

会打开浏览器，手动登录 Twitter，Cookie 会自动保存。

### 4️⃣ 配置搜索条件

编辑 `config.json`：
```json
{
  "search": {
    "query": "AI OR 人工智能",
    "time_range_hours": 24,
    "min_likes": 10
  },
  "selection": {
    "mode": "random",
    "count": 1
  },
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 5
  }
}
```

### 5️⃣ 运行工作流

```bash
# 正式运行
python3 main.py

# 测试运行（不发送消息）
python3 main.py --dry-run

# 显示浏览器（调试用）
python3 main.py --visible
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
┌─────────────┐     ┌─────────────┐
│  人工审核    │ ◄── │  Telegram   │
│  发布回复    │     │  推送消息    │
└─────────────┘     └─────────────┘
```

---

## ⏰ 定时任务

```bash
# 每 5 分钟执行一次（与 rate_limit.interval_minutes 匹配）
*/5 * * * * cd /path/to/twitter-workflow && python3 main.py >> workflow.log 2>&1
```

---

## 📊 配置说明

### config.json

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `search.query` | 搜索关键词 | `AI OR 人工智能` |
| `search.time_range_hours` | 时间范围（小时） | `24` |
| `search.min_likes` | 最小点赞数 | `10` |
| `selection.mode` | 选择模式 (random/top) | `random` |
| `selection.count` | 每次选择数量 | `1` |
| `rate_limit.interval_minutes` | 执行间隔（分钟） | `5` |

### 环境变量

| 变量 | 说明 |
|------|------|
| `VOLC_API_KEY` | 火山方舟 API Key |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID |
| `TWITTER_SEARCH_QUERY` | 临时覆盖搜索词 |
| `TWITTER_HOURS` | 临时覆盖时间范围 |
| `TWITTER_MIN_LIKES` | 临时覆盖最小点赞数 |

---

## 📁 项目结构

```
twitter-workflow/
├── main.py                 # 主工作流（含登录功能）
├── twitter_scraper.py      # Twitter 爬虫
├── reply_generator.py      # AI 回复生成
├── telegram_bot.py         # Telegram 推送
├── config.json             # 配置文件
├── .env                    # 环境变量
├── .env.example            # 配置模板
├── requirements.txt        # Python 依赖
└── README.md               # 本文档
```

---

## ❓ 常见问题

### Q: Cookie 过期了怎么办？
**A**: 重新运行 `python3 main.py --login`

### Q: 搜索结果为 0？
**A**: 放宽筛选条件：
```json
{
  "search": {
    "min_likes": 0,
    "time_range_hours": 24
  }
}
```

### Q: Telegram 收不到消息？
**A**: 检查 Bot Token 和 Chat ID 是否正确

---

## 🛡️ 安全提示

1. `.env` 和 `twitter_cookies.json` 不要提交到 git
2. 合理设置频率限制（建议 3-5 分钟）
3. 人工审核后再发布，确保质量

---

**开始你的 Twitter 半自动化运营吧！** 🚀
