# 使用示例

## 场景 1：查 Nginx 错误日志

```
用户：连 192.168.1.100，root/abc123，看下 nginx 最近有没有报错
Agent：已连接，执行 tail -n 50 /var/log/nginx/error.log
```

## 场景 2：检查服务器负载

```
用户：帮我看看服务器 10.0.0.5 的磁盘和内存情况
Agent：已连接，执行 df -h && free -h
```

## 场景 3：多命令排查

```
用户：连我的生产服务器 203.0.113.10，deploy/myPass! 
  检查一下：1) Docker 是否在运行 2) 应用端口 3000 是否监听
  3) 最近 10 条应用日志
Agent：依次执行：
  systemctl status docker
  ss -tlnp | grep :3000
  journalctl -u my-app --no-pager -n 10
```

## 场景 4：sudo 提权

```
用户：帮我重启一下 nginx，用户 root，密码 root123
Agent：执行 systemctl restart nginx（sudo 命令自动发送密码）
```

## 场景 5：传文件

```
用户：把本地的 config.yml 传到 192.168.1.100 的 /etc/app/config.yml
Agent：读取文件内容 → base64 编码 → 通过 SFTP 上传
```
