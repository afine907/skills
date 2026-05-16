# 前置环境安装

`remote-exec` 依赖 `paramiko` 库。Agent 会自动尝试安装，但也可以手动装：

```bash
python3 -m pip install paramiko --break-system-packages
```

## 验证安装

```bash
python3 -c "import paramiko; print(paramiko.__version__)"
```

正常输出类似：`5.0.0`

## 可选依赖

无。paramiko 是纯 Python 实现，无需系统级依赖。
