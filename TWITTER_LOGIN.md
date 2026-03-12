# Twitter 自动登录配置指南

## 🔐 两种登录方式

### 方式 1：自动登录（推荐用于服务器）

在 `.env` 文件中配置 Twitter 账号：

```bash
# 编辑 .env 文件
vim .env

# 添加以下配置
TWITTER_USERNAME=你的用户名或邮箱或手机号
TWITTER_PASSWORD=你的密码
```

然后运行登录脚本：

```bash
python3 login_twitter.py
```

脚本会自动：
1. 打开浏览器（无头模式）
2. 输入用户名
3. 输入密码
4. 点击登录
5. 保存 Cookie

---

### 方式 2：手动登录（适合本地开发）

不配置 `TWITTER_USERNAME` 和 `TWITTER_PASSWORD`，运行：

```bash
python3 login_twitter.py
```

会打开浏览器，手动登录后按回车保存 Cookie。

---

## ⚠️ 重要注意事项

### 1. 两步验证（2FA）

如果你的 Twitter 账号开启了**两步验证**，自动登录会检测到并提示你手动完成。

**解决方案**：
- 暂时关闭 2FA
- 或使用手动登录模式
- 或使用应用专用密码（如果 Twitter 支持）

### 2. 登录验证

Twitter 可能会检测异常登录行为，特别是：
- 新 IP 地址
- 新设备
- 频繁登录

**建议**：
- 首次登录使用手动模式
- 在同一台机器上保持 Cookie
- 不要频繁重新登录

### 3. 安全性

**不要将 `.env` 文件提交到 Git！**

项目已配置 `.gitignore` 忽略 `.env` 文件。

---

## 🚀 快速配置

### 步骤 1：编辑 .env 文件

```bash
cd /home/ubuntu/twitter-workflow
vim .env
```

### 步骤 2：添加 Twitter 账号

```bash
# Twitter 配置（用于自动登录）
TWITTER_USERNAME=your_username@example.com
TWITTER_PASSWORD=your_password_here
```

### 步骤 3：运行登录

```bash
python3 login_twitter.py
```

脚本会询问是否使用自动登录，输入 `y` 确认。

### 步骤 4：验证

登录成功后会显示：

```
✅ Cookie 已保存到 twitter_cookies.json
✅ 登录验证成功！

🎉 现在可以运行工作流了:
   python3 main.py
```

---

## 🔧 故障排查

### 问题 1：自动登录失败

**可能原因**：
- Twitter 页面结构变化
- 需要验证码
- 账号被锁定

**解决方案**：
```bash
# 使用手动登录
python3 login_twitter.py
# 选择手动登录模式
```

### 问题 2：检测到两步验证

**说明**：你的账号开启了 2FA

**解决方案**：
1. 等待脚本提示手动完成
2. 或在手机上完成验证
3. 或暂时关闭 2FA

### 问题 3：Cookie 很快过期

**可能原因**：Twitter 强制重新登录

**解决方案**：
- 保持定期使用
- 不要频繁切换 IP
- 使用稳定的网络环境

---

## 📝 配置文件说明

### .env 文件

```bash
# 火山引擎 API
VOLC_API_KEY=988d1ddf-132c-45d2-935b-b3bb259bd01d

# Telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# Twitter 自动登录（可选）
TWITTER_USERNAME=your@email.com
TWITTER_PASSWORD=your_password
```

### twitter_cookies.json

登录成功后自动生成，包含：
- Twitter 会话 Cookie
- 有效期：通常数周到数月
- 不要手动修改

---

## 💡 最佳实践

1. **首次使用手动登录** - 建立信任
2. **保存好 Cookie** - 避免频繁登录
3. **定期使用** - 保持会话活跃
4. **不要共享账号** - 避免风控
5. **使用稳定 IP** - 减少验证

---

有任何问题欢迎查看 README.md 或提交 Issue！
