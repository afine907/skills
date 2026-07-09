# jq 处理

## 基本操作

```bash
# 格式化
curl -s https://api.example.com/users | jq

# 提取字段
curl -s https://api.example.com/users | jq '.name'
curl -s https://api.example.com/users | jq '.[0].name'

# 数组操作
curl -s https://api.example.com/users | jq '.[]'
curl -s https://api.example.com/users | jq '.[] | .name'
curl -s https://api.example.com/users | jq 'length'
```

## 过滤和搜索

```bash
# 条件过滤
curl -s https://api.example.com/users | jq '.[] | select(.age > 25)'
curl -s https://api.example.com/users | jq '.[] | select(.name | startswith("A"))'

# 构造新对象
curl -s https://api.example.com/users | jq '.[] | {name, email}'
```

## 排序和分组

```bash
# 排序
curl -s https://api.example.com/users | jq 'sort_by(.age)'
curl -s https://api.example.com/users | jq 'sort_by(.age) | reverse'

# 分组统计
curl -s https://api.example.com/users | jq 'group_by(.role) | map({role: .[0].role, count: length})'
```
