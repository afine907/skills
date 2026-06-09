---
name: accessibility-audit
description: |
  【无障碍审计】检查 Web 应用的无障碍(a11y)合规性，包含 WCAG 2.1 标准检查、ARIA 属性审查、键盘导航测试、屏幕阅读器兼容性。

  触发时机：
  - 用户要求"无障碍检查"、"a11y审计"、"WCAG合规"
  - 需要满足无障碍法规要求
  - 提升产品的可访问性

  输出结构化的无障碍审计报告。
category: quality
---

# Accessibility Audit — 无障碍审计技能

检查 Web 应用的无障碍合规性，确保所有人都能使用。


## Goal

检查 Web 应用的无障碍(a11y)合规性，包含 WCAG 2.1 标准检查、ARIA 属性审查、键盘导航测试、屏幕阅读器兼容性

## Trigger

- 用户要求"无障碍检查"、"a11y审计"、"WCAG合规"
  - 需要满足无障碍法规要求
  - 提升产品的可访问性

## 工作流程

### Step 1: 确定审计范围 (Scope)

- 识别需要审计的页面/组件（首页、表单页、关键交互组件）
- 确定 WCAG 目标级别（A / AA / AAA）
- 收集页面 URL 列表和关键用户路径

### Step 2: 自动化扫描 (Automated Scan)

运行 axe-core + Lighthouse 收集所有违规项：
```bash
# Lighthouse 审计
npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json

# axe-core (Playwright 集成)
npx playwright test --grep "a11y"
```

**成功标准**：获得完整的自动化扫描报告，列出所有 WCAG 违规项。

### Step 3: 手动审查 (Manual Review)

自动化工具无法检测的问题需要手动验证：
1. **键盘导航**：Tab 遍历所有交互元素，确认焦点顺序合理，无键盘陷阱
2. **屏幕阅读器**：使用 NVDA/VoiceOver 测试页面语义是否正确传达
3. **缩放测试**：页面缩放至 200%，确认内容不重叠、不丢失
4. **动态内容**：SPA 路由切换后重新检查，确认新内容可访问

### Step 4: 分类归档 (Categorize)

将发现映射到 POUR 原则，分配严重程度：

| 严重程度 | 定义 | 示例 |
|----------|------|------|
| 严重 | 完全无法访问 | 缺少 alt 属性的图片、无键盘支持的按钮 |
| 重大 | 严重影响使用 | 对比度不足、缺少 ARIA 标签 |
| 中等 | 部分影响使用 | 缺少 label 的输入框 |
| 轻微 | 轻微影响体验 | 冗余的 ARIA 属性 |

### Step 5: 优先级排序 (Prioritize)

使用 影响程度 x 发生频率 矩阵：

|  | 高频率 | 低频率 |
|--|--------|--------|
| **高影响** | P0 立即修复 | P1 本迭代修复 |
| **低影响** | P2 下迭代修复 | P3 记录备查 |

### Step 6: 生成报告 (Report)

使用下方输出模板生成结构化审计报告。

### Step 7: 验证修复 (Verify Fixes)

修复后重新运行 Step 2-3，确认所有问题已解决，无新增问题。

## WCAG 2.1 核心原则

### POUR 原则

| 原则 | 含义 | 检查重点 |
|------|------|----------|
| **P**erceivable | 可感知 | 文本替代、颜色对比、多媒体字幕 |
| **O**perable | 可操作 | 键盘导航、时间充足、无闪烁 |
| **U**nderstandable | 可理解 | 语言清晰、输入帮助、错误提示 |
| **R**obust | 健壮性 | ARIA 属性、语义化 HTML、兼容性 |

## 检查维度

### 1. 文本替代 (1.1)

```html
<!-- ❌ 缺少 alt 属性 -->
<img src="logo.png">

<!-- ✅ 有意义的替代文本 -->
<img src="logo.png" alt="公司名称 Logo">

<!-- ✅ 装饰性图片使用空 alt -->
<img src="decorative.png" alt="" role="presentation">
```

### 2. 颜色对比 (1.4.3)

| 元素 | 最低对比度 | AAA 级 |
|------|-----------|--------|
| 正常文本 | 4.5:1 | 7:1 |
| 大文本 (18px+) | 3:1 | 4.5:1 |
| UI 组件 | 3:1 | 3:1 |

```css
/* ❌ 对比度不足 */
.text { color: #777; background: #fff; } /* 对比度 4.5:1 勉强 */

/* ✅ 良好对比度 */
.text { color: #595959; background: #fff; } /* 对比度 7:1 */
```

### 3. 键盘导航 (2.1)

```html
<!-- ❌ 不可聚焦的自定义按钮 -->
<div onclick="submit()">提交</div>

<!-- ✅ 可聚焦的语义化按钮 -->
<button type="submit">提交</button>

<!-- ✅ 自定义元素添加键盘支持 -->
<div role="button" tabindex="0" 
     onkeydown="if(event.key==='Enter'||event.key===' ')submit()">
  提交
</div>
```

**键盘操作检查清单**：
- [ ] 所有交互元素可通过 Tab 聚焦
- [ ] 焦点顺序符合逻辑（从左到右，从上到下）
- [ ] 焦点指示器清晰可见
- [ ] 可用 Enter/Space 激活按钮
- [ ] 可用 Escape 关闭弹窗
- [ ] 可用箭头键导航菜单/列表
- [ ] 无键盘陷阱（能进能出）

### 4. ARIA 属性 (4.1.2)

```html
<!-- ❌ 缺少 ARIA 标签的自定义组件 -->
<div class="modal">
  <div class="modal-close">×</div>
  <div class="modal-body">内容</div>
</div>

<!-- ✅ 正确的 ARIA 标注 -->
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal-header">
    <h2 id="modal-title">确认操作</h2>
    <button aria-label="关闭">×</button>
  </div>
  <div class="modal-body">确定要删除吗？</div>
  <div class="modal-footer">
    <button>取消</button>
    <button>确定</button>
  </div>
</div>
```

**常用 ARIA 角色**：

| 角色 | 用途 | 示例 |
|------|------|------|
| `navigation` | 导航区域 | `<nav>` 或 `<div role="navigation">` |
| `search` | 搜索区域 | `<form role="search">` |
| `alert` | 警告消息 | `<div role="alert">错误信息</div>` |
| `dialog` | 对话框 | `<div role="dialog">` |
| `tablist/tab/tabpanel` | 选项卡 | Tab 组件 |
| `menu/menuitem` | 菜单 | 下拉菜单 |
| `progressbar` | 进度条 | `<div role="progressbar">` |

### 5. 表单无障碍 (3.3)

```html
<!-- ❌ 缺少 label -->
<input type="email" placeholder="请输入邮箱">

<!-- ✅ 正确关联 label -->
<label for="email">邮箱地址</label>
<input type="email" id="email" 
       aria-describedby="email-hint email-error"
       aria-invalid="true"
       required>
<span id="email-hint">用于接收验证邮件</span>
<span id="email-error" role="alert">邮箱格式不正确</span>
```

### 6. 多媒体无障碍 (1.2)

```html
<!-- 视频需要字幕和音频描述 -->
<video controls>
  <source src="video.mp4">
  <track kind="captions" src="captions.vtt" srclang="zh" label="中文字幕">
  <track kind="descriptions" src="desc.vtt" srclang="zh" label="音频描述">
</video>
```

## 自动化检查工具

### axe-core 集成

```javascript
// 安装: npm install axe-core @axe-core/playwright

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('页面无障碍检查', async ({ page }) => {
  await page.goto('/');
  
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  
  expect(results.violations).toEqual([]);
});
```

### Lighthouse 检查

```bash
# 命令行运行
npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json

# CI 集成
npx lhci autorun --collect.settings.onlyCategories=accessibility
```

## 审计报告模板

```markdown
# 无障碍审计报告

## 概览
- **审计页面**: {页面列表}
- **审计标准**: WCAG 2.1 AA
- **审计时间**: {日期}
- **总体评级**: {A/B/C/D}

## 问题统计

| 严重程度 | 数量 | 影响 |
|----------|------|------|
| 🔴 严重 | {n} | 完全无法访问 |
| 🟠 重大 | {n} | 严重影响使用 |
| 🟡 中等 | {n} | 部分影响使用 |
| 🔵 轻微 | {n} | 轻微影响体验 |

## 问题详情

### 🔴 [严重] {问题标题}
- **WCAG 条款**: {条款编号}
- **影响人群**: {视障/听障/运动障碍/认知障碍}
- **问题描述**: {具体描述}
- **问题代码**:
```html
{问题代码}
```
- **修复建议**:
```html
{修复后代码}
```

## 修复优先级
1. {最紧急的修复}
2. {次紧急的修复}
...
```

## Edge Cases

1. **SPA 动态内容**：如果页面使用客户端渲染（React/Vue），axe-core 需要在 JS 执行完成后运行。在 Playwright 测试中使用 `page.waitForLoadState('networkidle')` 后再执行 axe 扫描，路由切换后重新扫描。
2. **Shadow DOM 组件**：axe-core 可能无法穿透 Shadow DOM 边界。如果扫描结果缺少 Shadow DOM 内部元素，需手动使用浏览器 DevTools 的 Accessibility 面板逐一检查 Shadow Root 内的 ARIA 属性。
3. **第三方小部件（reCAPTCHA、在线客服）**：这些组件不在你的控制范围内。审计时将它们标记为"第三方 - 无法修改"，并在报告中注明，同时检查页面其余部分的无障碍性是否受影响。
4. **Canvas/WebGL 内容**：canvas 元素对屏幕阅读器不可见。如果页面包含 canvas 绘制的内容，需要在 canvas 上添加 `role="img"` 和 `aria-label`，或提供替代文本描述。
5. **axe-core 结果与手动检查冲突**：如果 axe-core 标记某个元素"通过"但手动使用屏幕阅读器测试时发现无法访问，以手动检查结果为准。始终信任键盘和屏幕阅读器的实际体验。
6. **PDF/非 HTML 内容**：PDF 文件的无障碍性需要专门的检查工具（如 PAC2024、Adobe Acrobat Checker），本技能不适用于 PDF 文档审计。

## 不适用

| 场景 | 原因 | 推荐工具 |
|------|------|----------|
| 原生移动应用 | 需要平台专属的无障碍 API | Android: Accessibility Scanner, iOS: Accessibility Inspector |
| 桌面应用程序 | 需要 OS 级别的屏幕阅读器支持 | Windows: Narrator, macOS: VoiceOver |
| PDF/Word 文档 | 需要文档格式专用检查 | PAC2024, Adobe Acrobat Accessibility Checker |
| 纯后端 API | 无 UI 可审计 | 不适用 |

**重定向**：
- 移动应用无障碍审计：使用平台原生工具（Android Accessibility Scanner / iOS Accessibility Inspector）。
- 文档无障碍检查：使用 PAC2024 或 Adobe Acrobat 内置的无障碍检查器。

## 快速使用

```
# 审计整个页面
对当前页面进行无障碍审计

# 检查特定组件
检查这个表单组件的无障碍性

# 生成审计报告
为项目生成 WCAG 2.1 AA 合规报告

# 修复无障碍问题
修复以下代码的无障碍问题：[粘贴代码]
```

## 参考资料

- WCAG 2.1 标准: [references/wcag-checklist.md](references/wcag-checklist.md)
- ARIA 最佳实践: [references/aria-practices.md](references/aria-practices.md)
