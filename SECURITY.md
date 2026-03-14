# 安全配置指南 - 防止敏感信息泄漏

## 🚨 问题

每次推送都可能无意中将个人信息（API Key、Token、密码等）上传到 GitHub。

---

## 🛡️ 解决方案

### 1. Pre-commit Hook（已安装）✅

**位置**：`.git/hooks/pre-commit`

**功能**：
- 自动检测 API Key
- 阻止 .env 文件提交
- 检查 Telegram Token
- 警告密码/密钥配置

**测试**：
```bash
# 尝试提交敏感信息
echo "API_KEY=sk-1234567890abcdefghijklmnop" >> test.py
git add test.py
git commit -m "test"
# 会被阻止
```

---

### 2. .gitignore 配置（已配置）✅

**文件**：`.gitignore`

```bash
# 敏感信息
.env
*.key
*.pem
*.crt

# Cookie 和状态
twitter_cookies.json
processed_tweets.json
rate_limit_state.json
```

**验证**：
```bash
# 检查 .env 是否被忽略
git check-ignore .env
# 应该输出：.env
```

---

### 3. 环境变量管理

**正确做法**：

```bash
# ✅ .env 文件（不提交）
VOLC_API_KEY=your-actual-key-here
TELEGRAM_BOT_TOKEN=your-token-here

# ✅ .env.example 文件（可以提交）
VOLC_API_KEY=your-volc-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

**错误做法**：

```python
# ❌ 硬编码在代码中
API_KEY = "sk-1234567890..."

# ✅ 从环境变量读取
API_KEY = os.getenv("VOLC_API_KEY")
```

---

### 4. 提交前检查清单

**每次提交前执行**：

```bash
# 1. 检查即将提交的文件
git status
git diff --cached --name-only

# 2. 检查是否有敏感信息
git diff --cached | grep -E "sk-|token|password|secret"

# 3. 确认 .env 不在提交列表中
git ls-files --others --exclude-standard | grep "\.env"
```

---

### 5. 如果已经泄漏了怎么办？

**紧急处理步骤**：

```bash
# 1. 立即撤销/轮换泄漏的密钥
#    - 访问云服务控制台
#    - 删除旧 Key
#    - 创建新 Key

# 2. 清理 git 历史
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 3. 强制推送
git push -f origin main

# 4. 通知相关人员密钥已轮换
```

---

## 🔧 工具推荐

### detect-secrets（推荐）

```bash
# 安装
pip3 install detect-secrets

# 初始化
detect-secrets init

# 扫描
detect-secrets scan

# 添加到 pre-commit
detect-secrets hook .secrets.baseline
```

### GitGuardian ggshield

```bash
# 安装
pip3 install ggshield

# 配置
ggshield install -t pre-commit

# 扫描仓库
ggshield scan repo .
```

---

## 📋 最佳实践

### ✅ 应该做的

1. **使用环境变量**
   ```python
   API_KEY = os.getenv("VOLC_API_KEY")
   ```

2. **维护 .env.example**
   ```bash
   # 包含所有需要的变量名，但不包含真实值
   VOLC_API_KEY=your-api-key-here
   ```

3. **定期轮换密钥**
   - 每 3-6 个月更换一次
   - 离职员工立即撤销访问

4. **使用密钥管理服务**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

### ❌ 不应该做的

1. **不要硬编码**
   ```python
   # ❌ 错误
   API_KEY = "sk-1234567890..."
   
   # ✅ 正确
   API_KEY = os.getenv("API_KEY")
   ```

2. **不要提交 .env**
   ```bash
   # ❌ 错误
   git add .env
   
   # ✅ 正确
   echo ".env" >> .gitignore
   ```

3. **不要在日志中打印密钥**
   ```python
   # ❌ 错误
   print(f"Using API Key: {API_KEY}")
   
   # ✅ 正确
   print(f"Using API Key: {API_KEY[:10]}...")
   ```

---

## 🧪 测试安全配置

**测试 pre-commit**：

```bash
# 1. 创建包含敏感信息的文件
echo "API_KEY=sk-1234567890abcdefghijklmnop" > test_secret.py
git add test_secret.py

# 2. 尝试提交
git commit -m "test"
# 应该被阻止

# 3. 清理
git reset test_secret.py
rm test_secret.py
```

**测试 .gitignore**：

```bash
# 1. 创建 .env 文件
echo "SECRET=test" > .env

# 2. 尝试添加
git add .env
# 应该被忽略

# 3. 验证
git status
# .env 不应该出现在列表中
```

---

## 📞 故障排查

### Q: pre-commit 没有生效？

**A**: 检查执行权限
```bash
chmod +x .git/hooks/pre-commit
```

### Q: 误报了怎么办？

**A**: 修改 pre-commit 脚本，添加白名单

### Q: 如何禁用 pre-commit？

**A**: 临时禁用
```bash
git commit --no-verify -m "message"
```
（不推荐，仅用于紧急情况）

---

## 🎯 总结

**当前配置状态**：

| 安全措施 | 状态 | 说明 |
|----------|------|------|
| Pre-commit Hook | ✅ 已安装 | 自动检测敏感信息 |
| .gitignore | ✅ 已配置 | 忽略 .env 等文件 |
| 环境变量 | ✅ 已使用 | 代码中无硬编码 |
| 安全文档 | ✅ 已创建 | 本文件 |

**下次提交前**：
1. Pre-commit 会自动检查
2. 如有问题会阻止提交
3. 修复后重新提交即可

**安全第一！** 🔐
