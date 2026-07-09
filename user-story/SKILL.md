---
name: user-story
description: |
  【用户故事】将业务需求拆解为用户故事，含验收标准、故事点估算、优先级排序。

  触发时机：
  - 用户要求"写用户故事"、"拆解需求为故事"
  - Sprint 规划、需求评审前
category: requirements
---

# User Story — 用户故事

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

将业务需求拆解为可执行的用户故事。

## Workflow

1. **理解需求** — 业务背景、用户角色、目标
2. **拆解故事** — 按用户操作拆分
3. **编写 AC** — 定义验收标准
4. **估算大小** — 故事点 (1/2/3/5/8/13)
5. **排序优先级** — MoSCoW / 价值/复杂度矩阵

## 故事格式

```
As a [用户角色]
I want [功能描述]
So that [业务价值]
```

## 验收标准 (AC)

```
Given [前置条件]
When [操作]
Then [预期结果]
```

## Example

```
用户: 拆解"用户注册"需求

输出:
故事 1: 邮箱注册
  As a 新用户
  I want 使用邮箱注册账号
  So that 可以使用平台功能
  AC:
    Given 用户在注册页面
    When 输入有效邮箱和密码，点击注册
    Then 创建账号，发送验证邮件，跳转到验证页面
    When 输入已注册邮箱
    Then 提示"邮箱已注册"
  故事点: 5

故事 2: 手机号注册
  As a 新用户
  I want 使用手机号注册账号
  So that 更快捷地完成注册
  AC:
    Given 用户在注册页面
    When 输入手机号，获取验证码，输入验证码
    Then 创建账号，自动登录
  故事点: 8

故事 3: 第三方登录
  As a 新用户
  I want 使用微信/GitHub 登录
  So that 无需注册即可使用
  AC:
    Given 用户在登录页面
    When 点击微信登录，授权成功
    Then 自动创建账号并登录
  故事点: 13
```
