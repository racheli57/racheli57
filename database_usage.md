# 从 MySQL 读取政策数据生成推广文章

脚本支持两种模式：

1. 默认模式：使用 `generate_policy_docx.py` 内置的示例政策文章。
2. 数据库模式：通过 `--from-db` 从 MySQL 的 `policy_info` 表读取政策数据，再生成推广文章和 Word 文档。

> 为避免泄露数据库密码，脚本不会硬编码连接信息。请在本地通过环境变量传入 `MYSQL_HOST`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_PORT`、`MYSQL_CHARSET`、`MYSQL_DBNAME`。

## Windows CMD 示例

```bat
set MYSQL_HOST=你的数据库地址
set MYSQL_USER=你的用户名
set MYSQL_PASSWORD=你的密码
set MYSQL_PORT=你的端口
set MYSQL_CHARSET=utf8mb4
set MYSQL_DBNAME=subsidy
python -m pip install PyMySQL
python generate_policy_docx.py --from-db --ids 20260529169799,20260529169800,20260528861258
```

## PowerShell 示例

```powershell
$env:MYSQL_HOST="你的数据库地址"
$env:MYSQL_USER="你的用户名"
$env:MYSQL_PASSWORD="你的密码"
$env:MYSQL_PORT="你的端口"
$env:MYSQL_CHARSET="utf8mb4"
$env:MYSQL_DBNAME="subsidy"
python -m pip install PyMySQL
python generate_policy_docx.py --from-db --ids "20260529169799,20260529169800,20260528861258"
```

## 拉取最新政策

如果不指定 `--ids`，脚本会按 `update_time`、`create_time` 倒序读取最新政策，默认读取 10 条：

```bash
python generate_policy_docx.py --from-db --limit 10
```

生成结果会输出到当前目录，也可以用 `--output-dir` 指定目录：

```bash
python generate_policy_docx.py --from-db --limit 10 --output-dir demo1
```

## 连接失败排查说明

如果本地 cpolar 窗口显示 `Tunnel Status online`，但脚本仍连接失败，通常不是政策脚本本身的问题，而是执行脚本的机器到 cpolar 公网域名之间存在网络或依赖限制。可按下面顺序排查：

1. **确认脚本运行环境能解析 cpolar 域名**：在运行脚本的同一台机器上执行 `ping 19.tcp.vip.cpolar.cn` 或 `nslookup 19.tcp.vip.cpolar.cn`。如果解析失败，说明该环境 DNS 访问不到 cpolar 域名。
2. **确认端口能连通**：执行 `telnet 19.tcp.vip.cpolar.cn 12732`，或用 MySQL 客户端直接连接。如果端口不通，检查 cpolar 隧道是否仍是同一个公网地址和端口。免费版 cpolar 重新启动后，公网端口可能变化。
3. **确认 Python 依赖已安装**：数据库模式需要 `PyMySQL`，先执行 `python -m pip install PyMySQL`。如果安装失败，需要换到能访问 PyPI 的网络，或配置公司内网可用的 pip 镜像源。
4. **确认 MySQL 允许本地转发连接**：截图中的转发目标是 `127.0.0.1:3307`，请确认本机 MySQL 实际监听该端口，且 `root` 用户允许通过该连接方式访问 `subsidy` 数据库。
5. **确认 Windows 防火墙/安全软件未拦截**：虽然 cpolar 显示在线，但本机安全策略仍可能拦截到 MySQL 端口的本地转发访问。

我这边的远程执行容器与您的 Windows 电脑不是同一台机器；即使您本地 cpolar 显示在线，远程容器仍可能因为 DNS、代理或出网规则无法访问 `19.tcp.vip.cpolar.cn:12732`。建议在您本地项目目录运行数据库模式命令，这样脚本与 cpolar/MySQL 处在您可控的网络环境中。
