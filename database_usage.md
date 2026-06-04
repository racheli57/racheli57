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
