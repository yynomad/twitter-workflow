# 快速开始指南

## 1. 安装依赖

```bash
cd /home/ubuntu/twitter-workflow
pip install -r requirements.txt
playwright install chromium
```

## 2. 配置环境变量

```bash
cp .env.example .env
nano .env  # 或使用你喜欢的编辑器
```

填入你的 API 密钥：
- `OPENAI_API_KEY`: OpenAI API 密钥
- `TELEGRAM_BOT_TOKEN`: Telegram 机器人 Token
- `TELEGRAM_CHAT_ID`: 你的 Telegram Chat ID

## 3. 登录 Twitter

```bash
python login_twitter.py
```

会打开浏览器，手动登录 Twitter 后按回车保存 Cookie。

## 4. 获取 Telegram Chat ID

1. 在 Telegram 中搜索你的机器人（用你创建的 Bot Token）
2. 给机器人发送任意消息
3. 运行：
```bash
python get_chat_id.py
```
4. 复制输出的 Chat ID 到 `.env` 文件

## 5. 测试运行

```bash
# 显示浏览器模式，不实际发送
python main.py -q "AI" --visible --dry-run -n 2
```

## 6. 正式运行

```bash
python main.py -q "AI OR 人工智能" -n 5 --min-likes 10
```

## 常见问题

### Cookie 过期了怎么办？
重新运行 `python login_twitter.py` 登录即可。

### 浏览器打不开？
确保安装了 Chromium：`playwright install chromium`

### 搜索结果为空？
- 检查 Twitter 账号是否登录成功
- 尝试更简单的搜索词
- 降低 min-likes 和 min-retweets 的值

### Telegram 收不到消息？
- 检查 Bot Token 是否正确
- 确认 Chat ID 是否正确
- 确保你给机器人发送过消息
