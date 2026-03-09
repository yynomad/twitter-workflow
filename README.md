# Twitter 自动回复工作流

一个半自动化的 Twitter 回复工作流，帮助你快速响应相关推文。

**特点：无需 Twitter API，使用浏览器自动化直接抓取**

## 功能特点

- 🔍 **智能搜索**: 使用 Playwright 浏览器自动化搜索 Twitter，无需 API
- 🤖 **AI 生成回复**: 使用 OpenAI 为每条推文生成 3 条不同风格的回复
- 📱 **Telegram 推送**: 将推文和回复选项发送到你的 Telegram
- ✋ **半自动操作**: 人工审核后再发布，确保回复质量
- 💰 **完全免费**: 无需 Twitter API 付费

## 工作流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  浏览器登录  │ ──► │  抓取搜索页  │ ──► │  AI 生成回复  │ ──► │  Telegram   │
│  Twitter    │     │  提取推文    │     │  3 条回复     │     │  推送消息    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                              │
                                                              ▼
                                                         ┌─────────────┐
                                                         │   人工操作   │
                                                         │  点击链接    │
                                                         └─────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
cd twitter-workflow
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

需要配置：
- **OpenAI API Key**: 用于生成回复
- **Telegram Bot Token**: 用于推送消息

**不需要 Twitter API Key！**

### 3. 登录 Twitter

```bash
python login_twitter.py
```

会打开浏览器，手动登录 Twitter，登录后保存 Cookie。
之后无需再次登录（Cookie 过期前）。

### 4. 获取 Telegram Chat ID

```bash
# 先给机器人发送一条消息，然后运行
python get_chat_id.py
```

### 5. 运行工作流

```bash
# 测试模式（显示浏览器，不实际发送）
python main.py -q "AI OR 人工智能" --visible --dry-run

# 正式运行（无头模式）
python main.py -q "AI" -n 5 --min-likes 10
```

## 使用示例

### 基本用法
```bash
python main.py -q "Python 编程" -n 3
```

### 设置最小互动数
```bash
python main.py -q "机器学习" -n 5 --min-likes 50 --min-retweets 10
```

### 自定义回复风格
```bash
python main.py -q "AI" --instructions "回复要专业、简洁，避免过度营销"
```

### 显示浏览器（调试用）
```bash
python main.py -q "test" --visible --dry-run
```

### 使用配置文件
```bash
python main.py
```

## 配置文件说明

`config.json` 配置文件：

```json
{
  "search_query": "AI OR 人工智能 min_faves:10",  // 搜索查询
  "max_tweets": 5,                                // 每次处理推文数
  "min_likes": 10,                                // 最小点赞数
  "min_retweets": 0,                              // 最小转发数
  "custom_instructions": "回复要友好、有建设性",    // AI 生成指令
  "language": "中文"                              // 回复语言
}
```

## Twitter 搜索语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `OR` | 或 | `AI OR 人工智能` |
| `min_faves:N` | 最小点赞数 | `min_faves:100` |
| `min_retweets:N` | 最小转发数 | `min_retweets:50` |
| `-filter:replies` | 排除回复 | `AI -filter:replies` |
| `-filter:retweets` | 排除转推 | `AI -filter:retweets` |
| `from:username` | 指定用户 | `from:elonmusk` |
| `lang:en` | 指定语言 | `lang:en` |
| `since:YYYY-MM-DD` | 起始日期 | `since:2024-01-01` |
| `until:YYYY-MM-DD` | 结束日期 | `until:2024-12-31` |

## Telegram 消息格式

每条消息包含：
- 📌 推文预览
- 👤 作者信息
- 🔗 推文链接（可点击）
- 💡 3 条建议回复（不同风格）

## 操作说明

1. 收到 Telegram 消息后，点击推文链接
2. 在浏览器中打开推文
3. 选择一条喜欢的回复并复制
4. 粘贴到推文评论区
5. 发布！

## 定时任务（可选）

使用 cron 定时执行：

```bash
# 每 30 分钟执行一次
*/30 * * * * cd /path/to/twitter-workflow && python main.py >> workflow.log 2>&1
```

## 注意事项

- 首次使用需运行 `python login_twitter.py` 登录 Twitter
- Cookie 保存在 `twitter_cookies.json`，过期后需重新登录
- OpenAI API 会产生费用，注意控制使用量
- 已处理的推文会自动记录，避免重复回复
- 建议先使用 `--visible --dry-run` 测试模式验证配置
- 如果 Twitter 页面结构变化，可能需要更新爬虫代码

## 项目结构

```
twitter-workflow/
├── main.py              # 主工作流脚本
├── twitter_scraper.py   # Twitter 爬虫（Playwright）
├── reply_generator.py   # AI 回复生成
├── telegram_bot.py      # Telegram 推送
├── login_twitter.py     # Twitter 登录脚本
├── get_chat_id.py       # 获取 Telegram Chat ID
├── config.json          # 配置文件
├── .env.example         # 环境变量示例
├── requirements.txt     # Python 依赖
└── README.md            # 说明文档
```

## License

MIT
