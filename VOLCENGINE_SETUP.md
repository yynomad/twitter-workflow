# Twitter Workflow 火山引擎配置指南

## 🔑 火山引擎 API 配置

### 1️⃣ 获取 API Key

**已配置**：`988d1ddf-132c-45d2-935b-b3bb259bd01d`

如需重新获取：
1. 访问 https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey
2. 登录火山引擎账号
3. 创建或复制 API Key

### 2️⃣ 环境变量配置

`.env` 文件已配置：

```bash
# 火山引擎 API Key
VOLC_API_KEY=988d1ddf-132c-45d2-935b-b3bb259bd01d

# API 基础 URL（可选，默认已配置）
# VOLC_API_BASE=https://ark.cn-beijing.volces.com/api/v3

# 使用的模型（可选，默认：doubao-pro-4k）
# VOLC_MODEL=doubao-pro-4k
```

### 3️⃣ 可用模型

| 模型 | 说明 | 推荐场景 |
|------|------|----------|
| `doubao-pro-4k` | 豆包 Pro，4K 上下文 | 通用场景 ✅ |
| `doubao-lite-4k` | 豆包 Lite，4K 上下文 | 简单任务 |
| `doubao-pro-32k` | 豆包 Pro，32K 上下文 | 长文本分析 |
| `doubao-pro-128k` | 豆包 Pro，128K 上下文 | 超长文本 |

修改模型（可选）：
```bash
# 在 .env 中修改
VOLC_MODEL=doubao-pro-32k
```

---

## 📊 火山引擎 vs OpenAI 对比

| 特性 | 火山引擎 | OpenAI |
|------|----------|--------|
| **价格** | 💰 更便宜 | 💰💰 较贵 |
| **速度** | ⚡ 国内快 | ⚡ 需要代理 |
| **中文支持** | ✅ 优秀 | ✅ 好 |
| **API 兼容** | ✅ 兼容 OpenAI 格式 | - |
| **稳定性** | ✅ 国内稳定 | ⚠️ 需要代理 |

---

## 🚀 测试配置

```bash
# 1. 查看当前配置
python main.py --show-config

# 2. 测试运行（显示浏览器）
python main.py --visible --dry-run

# 3. 正式运行
python main.py
```

---

## 💰 费用说明

**火山引擎定价**（参考）：

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| doubao-lite-4k | ¥0.0003/千 tokens | ¥0.0006/千 tokens |
| doubao-pro-4k | ¥0.0008/千 tokens | ¥0.002/千 tokens |
| doubao-pro-32k | ¥0.005/千 tokens | ¥0.012/千 tokens |

**示例**：
- 每条推文生成 3 条回复 ≈ 500 tokens
- 100 条推文 ≈ ¥0.1-0.5 元

**非常便宜！** 远低于 OpenAI。

---

## ⚠️ 注意事项

1. **API Key 安全**
   - 不要将 `.env` 文件提交到 Git
   - 已添加到 `.gitignore`

2. **模型选择**
   - 默认 `doubao-pro-4k` 性价比最高
   - 如需更好效果可用 `doubao-pro-32k`

3. **速率限制**
   - 火山引擎有 QPS 限制
   - 默认配置已考虑限制

---

## 🔧 故障排查

### 问题 1：API Key 无效

```bash
# 检查 .env 文件
cat .env | grep VOLC_API_KEY

# 确认 Key 格式正确（UUID 格式）
```

### 问题 2：连接超时

```bash
# 检查网络连接
curl https://ark.cn-beijing.volces.com/api/v3

# 可能需要配置代理
```

### 问题 3：模型不可用

```bash
# 查看火山引擎控制台确认模型状态
# 访问：https://console.volcengine.com/ark
```

---

## 📝 完整配置清单

| 配置项 | 状态 | 说明 |
|--------|------|------|
| VOLC_API_KEY | ✅ 已配置 | 火山引擎 API Key |
| VOLC_API_BASE | ✅ 默认 | API 基础 URL |
| VOLC_MODEL | ✅ 默认 | doubao-pro-4k |
| TELEGRAM_BOT_TOKEN | ❓ 待配置 | Telegram 机器人 |
| TELEGRAM_CHAT_ID | ❓ 待配置 | Telegram Chat ID |
| Twitter 登录 | ❓ 待登录 | 运行 `python login_twitter.py` |

---

## 🎯 下一步

1. **配置 Telegram**（如果还没配置）
   ```bash
   # 编辑 .env 文件
   vim .env
   
   # 填入 Telegram 配置
   TELEGRAM_BOT_TOKEN=xxx
   TELEGRAM_CHAT_ID=xxx
   ```

2. **登录 Twitter**
   ```bash
   python login_twitter.py
   ```

3. **测试运行**
   ```bash
   python main.py --visible --dry-run
   ```

4. **正式运行**
   ```bash
   python main.py
   ```

---

有任何问题欢迎查看 CONFIG_GUIDE.md 或提交 Issue！
