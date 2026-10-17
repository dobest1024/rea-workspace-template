# 来源与落地取舍

核对日期：2026-10-17。

- [原帖](https://x.com/zodchiii/status/2109623079429460478)：采用独立工作区、事实与推断分离、机械工具先行、重命名留痕、分批分析和交接思路；未复制全文。
- [REA 官方仓库](https://github.com/morluto/rea)：确认工具定位、官方包名 `rea-agents`、目标类型及运行时操作边界。
- [REA 安装说明](https://github.com/morluto/rea/blob/main/docs/installation.md)：确认 MCP、provider 与安装方式。远端 main 在读取时已展示 6.5.0 示例，本模板以本机实际可运行的 6.4.0 为验证基线，不宣称最新版本。
- [Claude Code 权限文档](https://code.claude.com/docs/en/permissions)：使用 `Read` / `Edit`，采用项目锚定 `/target/**`；文件规则和命令匹配不是 OS 沙盒。
- [OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)：项目 `.codex/config.toml`、stdio command/args 和超时设置，项目配置需要客户端信任。

为实际工作补充 `work/` 分析副本、SHA-256 基线、保守 HAR 结构脱敏、APK 流程和可验证脚本。
未写死模型；未验证或传播原帖关于模型价格、上下文、星数、耗时和预算的宣传数字。
