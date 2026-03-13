# Twitter 搜索配置指南

## 📋 配置优先级

```
命令行参数 > 环境变量 > config.json
```

---

## 🔧 三种配置方式

### 方式 1：命令行参数（最高优先级）

**适合**：临时调整，每次运行不同配置

```bash
# 搜索 AI 相关推文，最小 5 个赞，12 小时内
python3 main.py -q "AI" --min-likes 5 --hours 12

# 搜索 3 条推文
python3 main.py -q "人工智能" -n 3

# 使用特定模式（random/latest/top）
python3 main.py --mode latest
```

**常用参数**：
- `-q, --query`: 搜索关键词
- `-n, --num-tweets`: 获取推文数量
- `--min-likes`: 最小点赞数
- `--min-views`: 最小曝光量
- `--hours`: 时间范围（小时）
- `--mode`: 选择模式（random/latest/top）

---

### 方式 2：环境变量（中等优先级）

**适合**：经常变动但不想每次敲命令行

**步骤**：

1. **编辑 .env 文件**：
   ```bash
   vim .env
   ```

2. **添加或修改配置**：
   ```bash
   # Twitter 搜索配置
   TWITTER_SEARCH_QUERY="AI OR 人工智能"
   TWITTER_MIN_LIKES=10
   TWITTER_MIN_RETWEETS=0
   TWITTER_MIN_VIEWS=1000
   TWITTER_HOURS=24
   TWITTER_NUM_TWEETS=1
   TWITTER_SELECTION_MODE=random
   ```

3. **运行工作流**：
   ```bash
   python3 main.py
   # 自动使用 .env 中的配置
   ```

**优势**：
- 修改方便，不需要改代码
- 可以配合脚本动态调整
- 命令行参数仍可覆盖

---

### 方式 3：config.json（最低优先级）

**适合**：长期稳定的默认配置

**文件**：`config.json`

```json
{
  "search": {
    "query": "",
    "time_range_hours": 0,
    "min_likes": 0,
    "min_retweets": 0,
    "min_views": 0
  },
  "selection": {
    "mode": "random",
    "count": 1
  }
}
```

---

## 📊 配置项说明

| 环境变量 | 命令行参数 | 说明 | 默认值 |
|----------|-----------|------|--------|
| `TWITTER_SEARCH_QUERY` | `-q, --query` | 搜索关键词 | `""` (首页) |
| `TWITTER_MIN_LIKES` | `--min-likes` | 最小点赞数 | `0` |
| `TWITTER_MIN_RETWEETS` | `--min-retweets` | 最小转发数 | `0` |
| `TWITTER_MIN_VIEWS` | `--min-views` | 最小曝光量 | `0` |
| `TWITTER_HOURS` | `--hours` | 时间范围（小时） | `0` |
| `TWITTER_NUM_TWEETS` | `-n, --num-tweets` | 获取推文数量 | `1` |
| `TWITTER_SELECTION_MODE` | `--mode` | 选择模式 | `random` |

---

## 🎯 使用场景示例

### 场景 1：日常监控 AI 动态

**.env 配置**：
```bash
TWITTER_SEARCH_QUERY="AI OR artificial intelligence"
TWITTER_MIN_LIKES=10
TWITTER_HOURS=24
TWITTER_NUM_TWEETS=3
```

**运行**：
```bash
python3 main.py
```

---

### 场景 2：临时搜索特定话题

**不修改 .env，直接用命令行**：
```bash
python3 main.py -q "machine learning" --min-likes 50 --hours 12
```

---

### 场景 3：命令行覆盖环境变量

**.env 配置**（默认）：
```bash
TWITTER_SEARCH_QUERY="AI"
TWITTER_MIN_LIKES=10
```

**临时运行不同配置**：
```bash
# 覆盖搜索词和点赞数
python3 main.py -q "deep learning" --min-likes 100
```

---

### 场景 4：多配置切换

**创建多个环境配置文件**：

```bash
# 配置 1：AI 监控
cp .env .env.ai
# 编辑 .env.ai: TWITTER_SEARCH_QUERY="AI"

# 配置 2：加密货币监控
cp .env .env.crypto
# 编辑 .env.crypto: TWITTER_SEARCH_QUERY="crypto OR bitcoin"

# 使用时复制
cp .env.ai .env
python3 main.py
```

---

## 💡 最佳实践

### ✅ 推荐

1. **config.json** 保存最基础的默认配置
2. **.env** 保存经常变动的搜索条件
3. **命令行** 用于临时调整

### ❌ 避免

1. 不要在代码中硬编码配置
2. 不要将 .env 提交到 git
3. 不要频繁修改 config.json

---

## 🧪 测试配置

**查看当前配置**：
```bash
python3 main.py --show-config
```

**测试环境变量**：
```bash
# 临时设置环境变量测试
export TWITTER_SEARCH_QUERY="test"
python3 main.py --show-config
```

---

## 📞 故障排查

### Q: 配置不生效？

**A**: 检查优先级
```bash
# 1. 检查命令行参数是否覆盖
python3 main.py -q "test"  # 命令行优先

# 2. 检查环境变量是否设置
echo $TWITTER_SEARCH_QUERY

# 3. 检查 .env 是否加载
cat .env | grep TWITTER
```

### Q: 如何调试配置？

**A**: 使用 --show-config
```bash
python3 main.py --show-config
```

---

## 📚 相关文件

- `.env` - 环境变量配置（不要提交到 git）
- `.env.example` - 配置模板
- `config.json` - 基础配置文件
- `main.py` - 主程序
