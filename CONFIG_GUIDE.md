# Twitter Workflow 配置指南

## 📋 配置文件结构

`config.json` 包含以下模块：

---

## 🔍 1. 搜索配置 (search)

```json
{
  "search": {
    "query": "AI OR 人工智能",
    "time_range_hours": 24,
    "min_likes": 10,
    "min_retweets": 0,
    "min_views": 1000,
    "exclude_replies": true,
    "exclude_retweets": true,
    "language": "en"
  }
}
```

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `query` | string | Twitter 搜索语句 | `"AI OR 人工智能"` |
| `time_range_hours` | int | 只筛选 X 小时内的推文 | `24` = 最近 24 小时 |
| `min_likes` | int | 最小点赞数 | `10` |
| `min_retweets` | int | 最小转发数 | `5` |
| `min_views` | int | 最小曝光量 | `1000` |
| `exclude_replies` | bool | 排除回复他人的推文 | `true` |
| `exclude_retweets` | bool | 排除转推 | `true` |
| `language` | string | 推文语言 | `en`, `zh`, `ja` |

### 搜索语法示例

```bash
# 基本搜索
"AI"

# 多关键词
"AI OR 人工智能 OR 机器学习"

# 排除特定词
"AI -广告 -推广"

# 指定用户
"from:elonmusk"

# 组合语法
"AI min_faves:100 min_retweets:10 -filter:replies"
```

---

## 🎲 2. 选择配置 (selection)

```json
{
  "selection": {
    "mode": "random",
    "count": 1,
    "sort_by": "engagement"
  }
}
```

| 参数 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| `mode` | string | `random`, `latest`, `top` | 选择模式 |
| `count` | int | 1-10 | 每次选择的推文数量 |
| `sort_by` | string | `engagement`, `likes`, `retweets`, `views` | 排序依据 |

### 选择模式说明

- **`random`**: 随机选择（推荐，避免模式化）
- **`latest`**: 选择最新的推文
- **`top`**: 选择互动数据最高的推文

---

## ⏰ 3. 频率限制配置 (rate_limit)

```json
{
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 30,
    "max_per_hour": 10,
    "max_per_day": 50
  }
}
```

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| `enabled` | bool | 是否启用频率限制 | `true` |
| `interval_minutes` | int | 两次运行之间的最小间隔（分钟） | `30` |
| `max_per_hour` | int | 每小时最大运行次数 | `10` |
| `max_per_day` | int | 每天最大运行次数 | `50` |

### 频率限制示例

**场景 1：每 30 分钟执行一次，每次 1 条**
```json
{
  "interval_minutes": 30,
  "max_per_hour": 2,
  "max_per_day": 24
}
```

**场景 2：每小时执行一次，每次 3 条**
```json
{
  "interval_minutes": 60,
  "max_per_hour": 1,
  "max_per_day": 10
}
```

**场景 3：不限频率（不推荐）**
```json
{
  "enabled": false
}
```

---

## 💬 4. 回复配置 (reply)

```json
{
  "reply": {
    "custom_instructions": "回复要友好、有建设性，可以适当提问或分享相关见解",
    "language": "中文",
    "styles": ["专业", "幽默", "友好"]
  }
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `custom_instructions` | string | AI 生成回复的自定义指令 |
| `language` | string | 回复语言 |
| `styles` | array | 回复风格列表 |

### 自定义指令示例

```json
// 专业技术风格
"回复要专业、简洁，避免过度营销，可以分享相关技术见解"

// 幽默风格
"回复要幽默风趣，可以用一些网络流行语，但要适度"

// 友好互动风格
"回复要友好、有建设性，可以适当提问或分享相关见解"
```

---

## 📱 5. Telegram 配置 (telegram)

```json
{
  "telegram": {
    "enabled": true,
    "batch_send": false
  }
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `enabled` | bool | 是否启用 Telegram 推送 |
| `batch_send` | bool | 是否批量发送（true）还是逐条发送（false） |

---

## 🚀 使用示例

### 示例 1：保守模式（适合新手）

```json
{
  "search": {
    "query": "AI",
    "time_range_hours": 24,
    "min_likes": 50,
    "min_retweets": 5,
    "min_views": 5000
  },
  "selection": {
    "mode": "random",
    "count": 1
  },
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 60,
    "max_per_hour": 1,
    "max_per_day": 10
  }
}
```

**特点**：
- 只选高互动推文
- 每小时最多 1 次
- 每天最多 10 条

---

### 示例 2：积极模式（适合活跃用户）

```json
{
  "search": {
    "query": "AI OR 人工智能 OR 机器学习",
    "time_range_hours": 12,
    "min_likes": 10,
    "min_retweets": 0,
    "min_views": 1000
  },
  "selection": {
    "mode": "random",
    "count": 3
  },
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 30,
    "max_per_hour": 5,
    "max_per_day": 50
  }
}
```

**特点**：
- 搜索范围广
- 每 30 分钟执行一次
- 每次 3 条推文

---

### 示例 3：精准模式（针对特定话题）

```json
{
  "search": {
    "query": "from:OpenAI OR from:Anthropic min_faves:100",
    "time_range_hours": 6,
    "min_likes": 100,
    "min_retweets": 20,
    "min_views": 10000,
    "exclude_replies": true,
    "exclude_retweets": true
  },
  "selection": {
    "mode": "top",
    "count": 1
  },
  "rate_limit": {
    "enabled": true,
    "interval_minutes": 120,
    "max_per_hour": 1,
    "max_per_day": 5
  }
}
```

**特点**：
- 只关注特定账号
- 只选高互动推文
- 频率较低，确保质量

---

## 📊 命令行覆盖配置

```bash
# 查看当前配置
python main.py --show-config

# 检查频率限制状态
python main.py --check-rate

# 临时覆盖搜索查询
python main.py -q "机器学习"

# 临时设置时间范围（6 小时内）
python main.py --hours 6

# 临时设置最小曝光量
python main.py --min-views 5000

# 临时设置选择数量
python main.py -n 3

# 临时设置选择模式
python main.py --mode top

# 组合使用
python main.py -q "AI" --hours 12 --min-likes 50 --mode random -n 1
```

---

## 🔧 频率限制状态文件

`rate_limit_state.json` 自动记录运行状态：

```json
{
  "last_run": "2026-03-11T15:00:00",
  "runs_today": 5,
  "runs_this_hour": 2,
  "last_reset_date": "2026-03-11",
  "last_reset_hour": "2026-03-11 15"
}
```

**不要手动修改此文件**，程序会自动管理。

---

## ⚠️ 注意事项

1. **频率限制建议**
   - 不要太频繁，避免被 Twitter 限制
   - 建议间隔至少 30 分钟
   - 每天不超过 50 次

2. **筛选条件建议**
   - `min_views` 不要设太高，否则可能没有符合条件的推文
   - `time_range_hours` 根据搜索热度调整
   - 热门话题可以用较短时间范围（如 6 小时）

3. **随机模式优势**
   - 避免模式化回复
   - 覆盖更多样化的推文
   - 降低被识别为机器人的风险

---

## 📝 快速开始

1. **编辑配置文件**
   ```bash
   vim config.json
   ```

2. **查看配置**
   ```bash
   python main.py --show-config
   ```

3. **测试运行**
   ```bash
   python main.py --dry-run --visible
   ```

4. **正式运行**
   ```bash
   python main.py
   ```

5. **设置定时任务（可选）**
   ```bash
   # 每 30 分钟执行一次
   */30 * * * * cd /path/to/twitter-workflow && python main.py >> workflow.log 2>&1
   ```

---

有任何问题欢迎查看 README.md 或提交 Issue！
