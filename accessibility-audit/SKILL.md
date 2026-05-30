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
