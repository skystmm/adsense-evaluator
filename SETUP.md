# GitHub 仓库设置指南

## 步骤 1：创建 GitHub 仓库

由于需要用户确认仓库类型（Public），请手动创建：

1. 访问 https://github.com/new
2. 仓库名称：`adsense-evaluator`
3. 选择 **Public** (公开仓库)
4. **不要** 初始化 README（我们已有本地代码）
5. 点击 "Create repository"

## 步骤 2：推送本地代码到 GitHub

创建仓库后，在终端执行以下命令：

```bash
cd /home/openclaw/workspace-assistent/projects/adsense-evaluator

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin git@github.com:YOUR_USERNAME/adsense-evaluator.git

# 或者使用 HTTPS 方式
# git remote add origin https://github.com/YOUR_USERNAME/adsense-evaluator.git

# 推送到 GitHub
git push -u origin main
```

## 步骤 3：验证推送

访问 https://github.com/YOUR_USERNAME/adsense-evaluator 确认代码已推送成功。

## 后续开发

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 项目状态

✅ 阶段 1 完成：
- [x] 项目结构创建
- [x] 前端初始化 (Next.js 14)
- [x] 后端初始化 (FastAPI)
- [x] 文档编写 (PRD + UI 设计)
- [x] 本地 Git 提交完成
- [ ] GitHub 仓库创建（需用户手动）
- [ ] 代码推送到 GitHub（需用户手动）

---

**注意**: 由于安全原因，GitHub 仓库创建需要用户手动确认。请按照上述步骤完成后继续开发。
