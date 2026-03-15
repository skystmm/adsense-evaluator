# AdSense Evaluator - Google AdSense 评估工具

一款帮助网站所有者评估其网站是否符合 Google AdSense 接入要求的工具，提供详细的评估报告、问题诊断和 AI 整改建议。

## 🚀 功能特性

- **快速评估**: 输入 URL，30 秒内生成详细评估报告
- **问题诊断**: 根据 AdSense 官方标准识别具体问题
- **AI 增强建议**: 基于 AI 分析提供个性化整改建议
- **历史记录**: 保存评估历史，追踪优化进度

## 📁 项目结构

```
adsense-evaluator/
├── frontend/                 # 前端 (Next.js 14)
│   ├── app/                 # Next.js App Router
│   ├── components/          # React 组件
│   ├── lib/                 # 工具函数
│   └── ...
├── backend/                  # 后端 (FastAPI)
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   ├── ai/                  # AI 评估模块
│   ├── models/              # 数据模型
│   └── ...
├── docs/                     # 文档
│   ├── adsense_evaluator_prd.md
│   └── adsense_evaluator_ui-design.md
└── README.md
```

## 🛠️ 技术栈

### 前端
- Next.js 14 (App Router)
- React 18
- TypeScript
- TailwindCSS
- Framer Motion (动画)
- Recharts (图表)

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- BeautifulSoup4 (网页解析)
- HTTPX (异步 HTTP)

### AI 集成
- OpenAI API (或其他 LLM)
- 内容质量分析
- 个性化建议生成

## 📦 安装和运行

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API 文档访问 http://localhost:8000/docs

## 📊 评估指标

### 内容质量（30 分）
- 原创性
- 内容深度
- 更新频率
- 专业性

### 网站结构（25 分）
- 导航清晰度
- 必要页面完整性
- 内部链接

### 用户体验（25 分）
- 加载速度
- 移动端适配
- 可读性

### 技术合规（20 分）
- HTTPS 支持
- SEO 优化
- 隐私政策

## 🚧 开发状态

当前阶段：**阶段 1 - 项目初始化** ✅

- [x] 创建 GitHub 仓库
- [x] 初始化前端项目
- [x] 初始化后端项目
- [x] 基础项目结构搭建
- [ ] 网站爬取和分析模块
- [ ] 评估打分系统
- [ ] AI 评估集成
- [ ] 报告生成
- [ ] 用户认证
- [ ] 部署上线

## 📝 下一步计划

### 阶段 2 - 核心功能开发
1. 完善网站爬取模块
2. 实现完整的评分系统
3. 集成 AI 分析功能
4. 生成可视化报告

### 阶段 3 - 问题诊断
1. 建设 AdSense 拒接原因库
2. 实现诊断逻辑
3. 生成整改建议

### 阶段 4 - UI/UX 完善
1. 完整前端页面
2. 用户认证系统
3. 历史记录功能
4. 部署上线

## 📄 许可证

MIT License

## ⚠️ 免责声明

本网站与 Google AdSense 无关，仅提供评估参考，不保证评估结果与实际 AdSense 审核结果一致。
