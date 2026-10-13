# 配置说明

ecom-hunter 支持通过配置文件或环境变量传递登录凭据。

## 配置文件

复制 `examples/config.yaml` 到项目根目录，按需修改。

```yaml
pinduoduo:
  headless: true
  account: ""            # 留空从环境变量读取
  password: ""
  user_data_dir: "~/.ecom-hunter/pdd-profile"
  timeout: 30000
  anti_crawl:
    min_delay: 0.5
    max_delay: 2.5
    max_retries: 3
```

## 环境变量

登录凭据可通过环境变量注入，避免明文写进配置：

```bash
export PDD_ACCOUNT="你的账号"
export PDD_PASSWORD="你的密码"
```

## 登录态持久化

各平台引擎使用 Playwright 的 persistent context，
将登录态保存在 `user_data_dir` 指定的目录。

**首次使用建议**：

1. 将 `headless` 设为 `false`
2. 运行采集脚本，在弹出的浏览器中手动完成登录
3. 登录态会自动保存，后续运行无需重复登录