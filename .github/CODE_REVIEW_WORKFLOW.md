# Git 工作流程 - Code Review 流程

## 🎯 工作流程

**所有代码修改必须通过 Pull Request 流程**

```
需求 → 修改 → 功能分支 → PR → Review → 合并
```

---

## 📋 操作步骤

### AI 助手操作流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/<功能描述>-<日期>
   # 例如：feature/cron-scheduler-20260317
   ```

2. **提交到功能分支**
   ```bash
   git add .
   git commit -m "<类型>: <描述>"
   # 类型：feat, fix, docs, chore, refactor
   git push -u origin <分支名>
   ```

3. **创建 Pull Request**
   ```bash
   gh pr create \
     --title "<类型>: <描述>" \
     --body "## 改动说明\n- 改动 1\n- 改动 2\n\n## 测试\n- [ ] 本地测试"
   ```

4. **等待 Review**
   - 在 PR 中回复评论
   - 根据反馈修改
   - **不直接合并到 main**

5. **合并**（由用户操作）
   - 用户 Review 通过
   - 用户合并到 main

---

## 🚫 禁止操作

```bash
# ❌ 禁止直接提交到 main
git checkout main
git commit -m "xxx"
git push origin main

# ❌ 禁止强制推送
git push -f origin main
```

---

## 📊 分支命名规范

| 类型 | 分支名 | 示例 |
|------|--------|------|
| 新功能 | `feature/xxx-YYYYMMDD` | `feature/cron-scheduler-20260317` |
| Bug 修复 | `fix/xxx-YYYYMMDD` | `fix/login-error-20260317` |
| 文档 | `docs/xxx-YYYYMMDD` | `docs/readme-update-20260317` |
| 重构 | `refactor/xxx-YYYYMMDD` | `refactor/api-module-20260317` |

---

## 🎯 Commit 信息规范

```
<类型>: <简短描述>

## 改动说明
- 改动 1
- 改动 2

## 相关 Issue
- Closes #123
```

**类型**：
- `feat` - 新功能
- `fix` - Bug 修复
- `docs` - 文档更新
- `chore` - 构建/工具
- `refactor` - 重构
- `test` - 测试

---

## 📋 PR 模板

```markdown
## 改动说明
- 

## 测试
- [ ] 本地测试通过
- [ ] 相关测试已更新

## 截图（如适用）

## 相关 Issue
- Closes #
```

---

## ✅ 检查清单

提交前确认：
- [ ] 代码已测试
- [ ] Commit 信息规范
- [ ] 分支名规范
- [ ] 无敏感信息
- [ ] PR 描述清晰

---

## 📞 相关文档

- README.md - 项目说明
- SECURITY.md - 安全配置
- .gitignore - Git 忽略配置

---

**设置日期**: 2026-03-17
**最后更新**: 2026-03-17
