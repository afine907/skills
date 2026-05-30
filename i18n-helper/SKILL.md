---
name: i18n-helper
description: |
  【国际化】设计和实现国际化(i18n)方案，包含翻译文件结构、动态语言切换、复数处理、日期/数字格式化。

  触发时机：
  - 用户要求"国际化"、"多语言支持"、"i18n"
  - 项目需要支持多种语言
  - 需要从代码中提取翻译文本

  支持前端(React/Vue)和后端(Python/Node)国际化方案。
category: development
---

# i18n Helper — 国际化助手

设计完整的国际化方案，支持多语言、多地区适配。

## 技术选型

| 框架 | 库 | 特点 |
|------|-----|------|
| React | react-i18next | Hook API、丰富功能 |
| Vue | vue-i18n | Vue 3 原生支持 |
| Python | babel + gettext | 标准方案 |
| Node.js | i18next | 跨平台、插件丰富 |

## 翻译文件结构

### 目录结构

```
locales/
├── zh-CN/
│   ├── common.json         # 通用翻译
│   ├── auth.json           # 认证模块
│   ├── order.json          # 订单模块
│   └── index.ts
├── en-US/
│   ├── common.json
│   ├── auth.json
│   ├── order.json
│   └── index.ts
└── index.ts
```

### 翻译文件格式

```json
{
  "common": {
    "ok": "确定",
    "cancel": "取消",
    "save": "保存",
    "delete": "删除",
    "edit": "编辑",
    "loading": "加载中...",
    "noData": "暂无数据",
    "error": "出错了",
    "success": "操作成功"
  },
  "auth": {
    "login": "登录",
    "logout": "退出登录",
    "register": "注册",
    "forgotPassword": "忘记密码",
    "email": "邮箱",
    "password": "密码",
    "loginSuccess": "登录成功",
    "loginFailed": "登录失败"
  },
  "order": {
    "create": "创建订单",
    "list": "订单列表",
    "detail": "订单详情",
    "status": {
      "pending": "待支付",
      "paid": "已支付",
      "shipped": "已发货",
      "completed": "已完成",
      "cancelled": "已取消"
    },
    "count": "共 {{count}} 个订单",
    "total": "总计: {{amount, currency}}"
  }
}
```

## React + react-i18next 实现

### 配置

```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import zhCN from './locales/zh-CN';
import enUS from './locales/en-US';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'zh-CN': { translation: zhCN },
      'en-US': { translation: enUS },
    },
    fallbackLng: 'zh-CN',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

### 使用示例

```tsx
import { useTranslation } from 'react-i18next';

function OrderList() {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('order.list')}</h1>
      <p>{t('order.count', { count: 10 })}</p>
      <p>{t('order.total', { amount: 99.99 })}</p>
      
      <select 
        value={i18n.language} 
        onChange={(e) => i18n.changeLanguage(e.target.value)}
      >
        <option value="zh-CN">中文</option>
        <option value="en-US">English</option>
      </select>
    </div>
  );
}
```

## Python + babel 实现

### 配置

```python
# babel.cfg
[python: **.py]
[jinja2: **/templates/**.html]
encoding = utf-8
```

### 提取翻译文本

```bash
# 提取待翻译文本
pybabel extract -F babel.cfg -o messages.pot .

# 初始化语言目录
pybabel init -i messages.pot -d locales -l zh_CN

# 更新翻译
pybabel update -i messages.pot -d locales -l zh_CN

# 编译翻译文件
pybabel compile -d locales
```

### 使用示例

```python
from flask_babel import gettext, lazy_gettext, format_datetime, format_currency

# 视图函数中
@app.route('/order')
def order_list():
    title = gettext('Order List')
    count_msg = gettext('%(count)d orders', count=10)
    return render_template('order.html', title=title)

# 模板中
# {{ _('Order List') }}
# {{ _('Total: %(amount)s', amount=format_currency(99.99, 'CNY')) }}

# 延迟翻译（用于模块级别）
error_msg = lazy_gettext('Invalid email format')
```

## 翻译最佳实践

### 1. 使用命名空间

```json
// ❌ 扁平结构
{
  "loginButton": "登录",
  "loginTitle": "用户登录",
  "loginError": "登录失败"
}

// ✅ 命名空间
{
  "auth": {
    "login": {
      "button": "登录",
      "title": "用户登录",
      "error": "失败"
    }
  }
}
```

### 2. 处理复数

```json
{
  "cart": {
    "items": {
      "one": "{{count}} 件商品",
      "other": "{{count}} 件商品"
    }
  }
}
```

```typescript
// React
t('cart.items', { count: 5 }) // "5 件商品"
```

### 3. 日期和数字格式化

```typescript
// 使用 Intl API
const formatDate = (date: Date, locale: string) => {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

const formatNumber = (num: number, locale: string) => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: locale === 'zh-CN' ? 'CNY' : 'USD',
  }).format(num);
};
```

## 提取翻译文本

### 自动提取脚本

```python
"""从代码中提取翻译文本"""
import re
import json
from pathlib import Path

def extract_translations(source_dir: str) -> dict:
    """提取所有 t('key') 调用"""
    pattern = re.compile(r"""t\(['"]([^'"]+)['"]\)""")
    translations = {}
    
    for file in Path(source_dir).rglob('*.{ts,tsx,js,jsx}'):
        content = file.read_text()
        matches = pattern.findall(content)
        for key in matches:
            translations[key] = ""  # 待翻译
    
    return translations

# 生成翻译模板
translations = extract_translations('src/')
with open('locales/en-US.json', 'w') as f:
    json.dump(translations, f, indent=2)
```

## 快速使用

```
# 设计国际化方案
为 React 项目设计国际化方案

# 提取翻译文本
从代码中提取所有需要翻译的文本

# 添加新语言
为项目添加日语支持

# 翻译文本
将以下中文翻译为英文：[粘贴文本]
```

## 参考资料

- react-i18next 文档: [references/react-i18next.md](references/react-i18next.md)
- ICU 消息格式: [references/icu-format.md](references/icu-format.md)
