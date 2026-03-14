# Twitter 搜索配置指南

## 📋 配置方式

**只使用环境变量配置**

所有搜索相关的配置都通过 `.env` 文件的环境变量管理。

---

## 🔧 配置步骤

### 1. 编辑 .env 文件

```bash
vim .env
```

### 2. 设置搜索参数

```bash
# 搜索关键词
TWITTER_SEARCH_QUERY="AI OR 人工智能"

# 筛选条件
TWITTER_MIN_LIKES=10
TWITTER_MIN_RETWEETS=0
TWITTER_MIN_VIEWS=1000

# 时间范围（小时）
TWITTER_HOURS=24

# 获取数量
TWITTER_NUM_TWEETS=1

# 选择模式：random, latest, top
TWITTER_SELECTION_MODE=random
```

### 3. 运行工作流

```bash
python3 main.py
```

---

## 📊 配置项说明

| 环境变量 | 说明 | 默认值 | 示例 |
|----------|------|--------|------|
| `TWITTER_SEARCH_QUERY` | 搜索关键词 | `""` (首页) | `"AI OR 人工智能"` |
| `TWITTER_MIN_LIKES` | 最小点赞数 | `0` | `10` |
| `TWITTER_MIN_RETWEETS` | 最小转发数 | `0` | `5` |
| `TWITTER_MIN_VIEWS` | 最小曝光量 | `0` | `1000` |
| `TWITTER_HOURS` | 时间范围（小时） | `0` | `24` |
| `TWITTER_NUM_TWEETS` | 获取推文数量 | `1` | `3` |
| `TWITTER_SELECTION_MODE` | 选择模式 | `random` | `random` |

---

## 🎯 使用场景示例

### 场景 1：日常监控 AI 动态

**.env 配置**：
```bash
TWITTER_SEARCH_QUERY="AI OR artificial intelligence"
TWITTER_MIN_LIKES=10
TWITTER_HOURS=24
TWITTER_NUM_TWEETS=3
TWITTER_SELECTION_MODE=random
```

**运行**：
```bash
python3 main.py
```

---

### 场景 2：监控热门推文

**.env 配置**：
```bash
TWITTER_SEARCH_QUERY="machine learning"
TWITTER_MIN_LIKES=100
TWITTER_MIN_RETWEETS=20
TWITTER_HOURS=12
TWITTER_SELECTION_MODE=top
```

---

### 场景 3：获取最新推文

**.env 配置**：
```bash
TWITTER_SEARCH_QUERY="deep learning"
TWITTER_HOURS=1
TWITTER_SELECTION_MODE=latest
TWITTER_NUM_TWEETS=5
```

---

### 场景 4：首页模式（不搜索）

**.env 配置**：
```bash
TWITTER_SEARCH_QUERY=""
TWITTER_NUM_TWEETS=1
```

---

## 💡 最佳实践

### ✅ 推荐

1. **定期调整搜索词** - 根据需求更新 `TWITTER_SEARCH_QUERY`
2. **合理设置筛选条件** - 避免太严格导致没有推文
3. **使用首页模式** - 设置空字符串获取最新推文

### ❌ 避免

1. 搜索条件过于严格（可能没有结果）
2. 频繁修改配置（建议固定常用配置）
3. 将 .env 提交到 git

---

## 🔄 配置切换

可以创建多个配置文件快速切换：

```bash
# AI 监控配置
cp .env.ai .env
python3 main.py

# 加密货币监控配置
cp .env.crypto .env
python3 main.py
```

---

## 📚 相关文件

- `.env` - 环境变量配置（不要提交到 git）
- `.env.example` - 配置模板
- `config.json` - 其他配置（频率限制等）

---

## 🧪 测试配置

**查看当前配置**：
```bash
cat .env | grep TWITTER
```

**测试运行**：
```bash
python3 main.py
```
