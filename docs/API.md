# AdSense Evaluator API 文档

## 概述

AdSense Evaluator API 提供网站 AdSense 合规性评估功能，包括网站爬取、智能评分、问题诊断和 AI 建议生成。

**基础 URL**: `http://localhost:8000`（本地开发）  
**API 版本**: 1.0.0  
**认证**: 当前无需认证

---

## 接口列表

### 1. 评估网站

**POST** `/api/evaluate/`

评估单个网站是否符合 AdSense 要求。

#### 请求参数

```json
{
  "url": "https://example.com",
  "include_ai_analysis": true,
  "use_playwright": false
}
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | string | 是 | - | 要评估的网站 URL（必须包含 http:// 或 https://） |
| include_ai_analysis | boolean | 否 | true | 是否包含 AI 分析建议 |
| use_playwright | boolean | 否 | false | 是否使用 Playwright 渲染 JavaScript（适合 SPA 网站） |

#### 响应示例

```json
{
  "success": true,
  "url": "https://example.com",
  "overall_score": 72,
  "pass_probability": 65.5,
  "metrics": {
    "content_quality": 25,
    "site_structure": 16,
    "traffic_source": 10,
    "technical_compliance": 15,
    "policy_compliance": 6
  },
  "issues": [
    {
      "category": "policy_compliance",
      "priority": "high",
      "title": "缺少隐私政策页面",
      "description": "AdSense 强制要求网站必须有隐私政策页面",
      "suggestion": "创建隐私政策页面，说明如何收集、使用和保护用户数据",
      "impact": "可能导致申请被直接拒绝"
    }
  ],
  "ai_suggestions": [
    {
      "type": "content_improvement",
      "priority": "high",
      "title": "提升内容质量",
      "description": "当前内容质量得分 25/35",
      "action_items": ["每周发布 2-3 篇原创文章", "每篇文章至少 1000 字"],
      "expected_impact": "+10-15 分",
      "ai_generated": false
    }
  ],
  "report_id": "rpt_abc123def456",
  "rating": "一般 - 基本符合要求，但需要优化",
  "created_at": "2026-03-15T18:30:00.000000"
}
```

#### 评分维度说明

| 维度 | 满分 | 权重 | 说明 |
|------|------|------|------|
| content_quality | 35 | 35% | 内容质量（字数、标题结构、Meta 描述、图片等） |
| site_structure | 20 | 20% | 网站结构（必要页面、导航、内部链接等） |
| traffic_source | 15 | 15% | 流量来源（外部链接、社交媒体、权威性等） |
| technical_compliance | 20 | 20% | 技术合规（HTTPS、加载速度、SEO、可访问性等） |
| policy_compliance | 10 | 10% | 政策遵守（隐私政策、关于我们、联系我们等） |

#### 错误响应

```json
{
  "detail": "无法访问目标网站，请检查 URL 是否正确"
}
```

---

### 2. 批量评估

**POST** `/api/evaluate/batch`

批量评估多个网站（最多 10 个）。

#### 请求参数

```json
[
  {
    "url": "https://example1.com",
    "include_ai_analysis": true
  },
  {
    "url": "https://example2.com",
    "include_ai_analysis": false
  }
]
```

#### 响应示例

```json
[
  {
    "success": true,
    "url": "https://example1.com",
    "overall_score": 72,
    "report_id": "rpt_abc123",
    ...
  },
  {
    "success": false,
    "url": "https://example2.com",
    "error": "无法访问目标网站"
  }
]
```

---

### 3. 获取报告详情

**GET** `/api/reports/{report_id}`

获取指定评估报告的详细信息。

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| report_id | string | 报告 ID（格式：rpt_xxxxxxxxxxxx） |

#### 响应示例

```json
{
  "report_id": "rpt_abc123def456",
  "url": "https://example.com",
  "overall_score": 72,
  "pass_probability": 65.5,
  "metrics": {
    "content_quality": 25,
    "site_structure": 16,
    "traffic_source": 10,
    "technical_compliance": 15,
    "policy_compliance": 6
  },
  "issues": [...],
  "ai_suggestions": [...],
  "rating": "一般 - 基本符合要求，但需要优化",
  "created_at": "2026-03-15T18:30:00.000000",
  "website_data": {
    "title": "Example Website",
    "word_count": 1250,
    "images_count": 8,
    "has_privacy_policy": false,
    ...
  }
}
```

---

### 4. 获取报告列表

**GET** `/api/reports/`

获取所有评估报告列表（支持分页）。

#### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | integer | 50 | 每页数量（最大 100） |
| offset | integer | 0 | 偏移量 |

#### 响应示例

```json
[
  {
    "report_id": "rpt_abc123",
    "url": "https://example.com",
    "overall_score": 72,
    "pass_probability": 65.5,
    "rating": "一般 - 基本符合要求，但需要优化",
    "created_at": "2026-03-15T18:30:00.000000"
  },
  ...
]
```

---

### 5. 删除报告

**DELETE** `/api/reports/{report_id}`

删除指定评估报告。

#### 响应示例

```json
{
  "success": true,
  "message": "报告已删除"
}
```

---

### 6. 获取统计摘要

**GET** `/api/reports/stats/summary`

获取所有报告的统计摘要。

#### 响应示例

```json
{
  "total_reports": 156,
  "average_score": 68.5,
  "average_pass_probability": 62.3,
  "score_distribution": {
    "excellent": 12,
    "good": 45,
    "fair": 58,
    "poor": 32,
    "very_poor": 9
  }
}
```

---

### 7. 获取历史记录

**GET** `/api/history/`

获取评估历史记录（支持筛选和分页）。

#### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | integer | 20 | 每页数量（1-100） |
| offset | integer | 0 | 偏移量 |
| days | integer | 30 | 最近多少天（1-365） |
| min_score | integer | null | 最低分数筛选 |

#### 响应示例

```json
{
  "items": [
    {
      "report_id": "rpt_abc123",
      "url": "https://example.com",
      "overall_score": 72,
      "pass_probability": 65.5,
      "rating": "一般 - 基本符合要求，但需要优化",
      "created_at": "2026-03-15T18:30:00.000000",
      "issues_count": 8,
      "high_priority_issues": 2
    }
  ],
  "total": 156,
  "has_more": true
}
```

---

### 8. 按 URL 查询历史

**GET** `/api/history/url/{url}`

根据 URL 获取该网站的所有历史评估记录。

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| url | string | 网站 URL（需要 URL 编码） |

#### 响应示例

```json
{
  "url": "https://example.com",
  "total_evaluations": 5,
  "evaluations": [
    {
      "report_id": "rpt_abc123",
      "overall_score": 72,
      "created_at": "2026-03-15T18:30:00.000000",
      ...
    },
    ...
  ]
}
```

---

### 9. 获取评分趋势

**GET** `/api/history/trend`

获取评分趋势（最近 N 天的平均分数变化）。

#### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| days | integer | 30 | 天数（1-90） |

#### 响应示例

```json
{
  "days": 30,
  "trend": [
    {
      "date": "2026-03-01",
      "average_score": 65.2,
      "evaluations_count": 5
    },
    {
      "date": "2026-03-02",
      "average_score": 68.7,
      "evaluations_count": 8
    }
  ]
}
```

---

## 数据结构说明

### 问题对象（Issue）

```typescript
{
  category: string;        // 问题类别：content_quality, site_structure, technical_compliance, policy_compliance, user_experience, traffic_source
  priority: string;        // 优先级：high, medium, low
  title: string;           // 问题标题
  description: string;     // 问题描述
  suggestion: string;      // 改进建议
  impact?: string;         // 影响说明
}
```

### AI 建议对象（AI Suggestion）

```typescript
{
  type: string;            // 建议类型：content_improvement, structure_improvement, technical_improvement, overall, benchmark
  priority: string;        // 优先级：high, medium, low
  title: string;           // 建议标题
  description: string;     // 建议描述
  action_items?: string[]; // 具体行动项
  expected_impact?: string;// 预期影响
  ai_generated?: boolean;  // 是否由 AI 生成
  probability?: number;    // 通过概率（仅概率类型）
  weeks?: number;          // 预计周数（仅时间类型）
}
```

---

## 使用示例

### cURL 示例

```bash
# 评估网站
curl -X POST http://localhost:8000/api/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "include_ai_analysis": true
  }'

# 获取报告
curl http://localhost:8000/api/reports/rpt_abc123def456

# 获取历史记录
curl "http://localhost:8000/api/history/?limit=20&days=7"
```

### JavaScript 示例

```javascript
// 评估网站
const response = await fetch('http://localhost:8000/api/evaluate/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com',
    include_ai_analysis: true,
  }),
});

const data = await response.json();
console.log('总分:', data.overall_score);
console.log('通过概率:', data.pass_probability);
console.log('报告 ID:', data.report_id);

// 获取报告详情
const reportResponse = await fetch(`http://localhost:8000/api/reports/${data.report_id}`);
const report = await reportResponse.json();
console.log('详细报告:', report);
```

### Python 示例

```python
import requests

# 评估网站
response = requests.post('http://localhost:8000/api/evaluate/', json={
    'url': 'https://example.com',
    'include_ai_analysis': True,
})

data = response.json()
print(f"总分：{data['overall_score']}")
print(f"通过概率：{data['pass_probability']}%")

# 获取报告详情
report_response = requests.get(f"http://localhost:8000/api/reports/{data['report_id']}")
report = report_response.json()
print(f"问题数量：{len(report['issues'])}")
```

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误（如 URL 无效） |
| 404 | 资源不存在（如报告 ID 错误） |
| 500 | 服务器内部错误 |

---

## 性能说明

- **单次评估时间**: 通常 5-30 秒（取决于网站大小和复杂度）
- **并发限制**: 最多 5 个并发请求
- **缓存**: 评估结果缓存 24 小时，相同 URL 直接返回缓存
- **批量评估**: 最多 10 个网站/次

---

## 更新日志

### v1.0.0 (2026-03-15)
- 初始版本发布
- 支持网站爬取和分析
- 5 大维度评分系统
- AI 智能建议生成
- 完整的 RESTful API
- 报告存储和查询
