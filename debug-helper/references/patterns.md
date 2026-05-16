# 常见错误模式库

按语言/框架分类，帮助快速定位根因。仅在 LLM 不熟悉模式时翻查。

## Python 错误模式

| 错误 | 常见根因 | 排查方向 |
|------|----------|----------|
| `KeyError: 'xxx'` | 字典 key 不存在 | 检查数据来源、默认值、get() 方法 |
| `AttributeError: 'NoneType' object has no attribute 'xxx'` | 返回值为 None 后继续调用 | 检查前一步的返回值和异常处理 |
| `IndexError: list index out of range` | 列表为空或下标越界 | 检查列表长度和循环边界 |
| `TypeError: 'int' object is not iterable` | 类型不匹配 | 检查变量类型和预期类型 |
| `ValueError: invalid literal for int()` | 字符串转数字失败 | 检查输入格式、空值处理 |
| `ModuleNotFoundError` | 依赖未安装或导入路径错误 | 检查 `pip list`、`PYTHONPATH`、虚拟环境 |
| `ImportError: cannot import name` | 循环导入或名字变更 | 检查模块依赖图、导出名 |
| `RecursionError: maximum recursion depth exceeded` | 递归无终止条件 | 检查递归基例、循环引用 |
| `ConnectionRefusedError` | 服务未启动或端口不对 | `systemctl status`、`ss -tlnp` |
| `MemoryError` / `OSError: Cannot allocate memory` | 内存不足或泄露 | `free -h`、对象引用是否未释放 |

## Node.js / JavaScript 错误模式

| 错误 | 常见根因 | 排查方向 |
|------|----------|----------|
| `Cannot read property 'xxx' of undefined` | 对象为 undefined 后访问属性 | 检查 API 返回、可选链 `?.` |
| `Cannot read property 'xxx' of null` | 对象为 null | 检查初始化逻辑 |
| `TypeError: xxx is not a function` | 类型错误 | 检查导入是否正确、原型链 |
| `EADDRINUSE` | 端口被占用 | `lsof -i :port` 找占用进程 |
| `ECONNREFUSED` | 连接被拒绝 | 检查服务是否运行、防火墙 |
| `ENOENT: no such file or directory` | 文件不存在 | 检查路径、工作目录 |
| `Module not found: Error: Can't resolve` | 模块未安装或路径错 | 检查 `node_modules`、`import` 路径 |
| `ERR_OUT_OF_MEMORY` | 内存不足 | 检查 `--max-old-space-size`、内存泄露 |
| `heap out of memory` | V8 堆内存不足 | 加大内存限制或排查内存泄露 |

## Go 错误模式

| 错误 | 常见根因 | 排查方向 |
|------|----------|----------|
| `nil pointer dereference` | 空指针访问 | 检查指针初始化、函数返回值是否为 nil |
| `index out of range` | 切片越界 | 检查切片长度和循环边界 |
| `connection refused` | 连接被拒 | 检查服务监听地址、防火墙 |
| `context deadline exceeded` | 请求超时 | 检查下游服务响应时间、网络延迟 |
| `unexpected EOF` | 连接中断 | 检查对端是否主动关闭 |
| `no such host` | DNS 解析失败 | 检查 DNS 配置、hosts 文件 |
| `permission denied` | 权限不足 | 检查文件权限、用户身份 |

## HTTP/API 错误模式

| 状态码 | 常见根因 | 排查方向 |
|--------|----------|----------|
| 400 | 请求参数错误 | 检查 payload 格式、必填字段 |
| 401 | 认证失败 | 检查 token 是否过期、header 格式 |
| 403 | 权限不足 | 检查用户角色、资源权限 |
| 404 | 资源不存在 | 检查 URL 路径、路由配置 |
| 429 | 限流触发 | 检查 QPS、等待重试 |
| 500 | 服务端未捕获异常 | 检查应用日志、异常处理 |
| 502 | 网关/代理错误 | 检查上游服务是否可用 |
| 503 | 服务不可用 | 检查负载、重启状态 |
| 504 | 网关超时 | 检查上游响应时间、超时配置 |

## 系统错误模式

| 错误 | 常见根因 | 排查方向 |
|------|----------|----------|
| `Out of memory` / `OOM killed` | 内存耗尽 | `dmesg \| grep oom`、`free -h` |
| `Disk full` / `No space left` | 磁盘满 | `df -h`、找大文件清理 |
| `Too many open files` | 文件描述符耗尽 | `ulimit -n`、`lsof \| wc -l` |
| `Operation not permitted` | 权限不足 | 检查用户、sudo、SELinux |
| `File exists` | 文件已存在 | 检查是否需 `-f` 或先删除 |
| `No such file or directory` | 路径不存在 | 检查路径、工作目录、挂载点 |
| `Device or resource busy` | 资源占用中 | `lsof`、`fuser` 找占用进程 |
| `Connection timed out` | 连接超时 | 检查网络连通性、防火墙、DNS |
