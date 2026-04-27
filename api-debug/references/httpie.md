# httpie 用法

## 安装

```bash
pip install httpie
```

## 基本请求

```bash
http https://api.example.com/users
http GET https://api.example.com/users
http POST https://api.example.com/users name=Alice age:=25
http PUT https://api.example.com/users/1 name=Bob
http DELETE https://api.example.com/users/1
```

## 请求项语法

```bash
# 请求头: Header:Value
http https://api.example.com Authorization:Bearer\ token

# 查询参数: param==value
http https://api.example.com/users page==1 limit==20

# JSON 字段: field=value (字符串), field:=value (原生类型)
http POST https://api.example.com/users \
  name=Alice \
  age:=25 \
  active:=true \
  tags:='["tag1","tag2"]'

# 表单字段
http --form POST https://api.example.com/upload file@photo.jpg

# 原始 JSON
http POST https://api.example.com/users < user.json
echo '{"name":"Alice"}' | http POST https://api.example.com/users
```

## 认证

```bash
# Basic Auth
http -a user:pass https://api.example.com

# Bearer Token
http https://api.example.com Authorization:"Bearer token123"

# 使用 session (保存认证)
http --session=user -a user:pass https://api.example.com/login
http --session=user https://api.example.com/profile
```

## 输出控制

```bash
http -h https://api.example.com          # 只显示响应头
http -b https://api.example.com          # 只显示响应体
http -v https://api.example.com          # 显示完整请求和响应
http --download https://example.com/file.zip  # 下载文件
```
