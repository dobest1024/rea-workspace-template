# 脚手架验收

日期：2026-10-17。此记录是模板的合成样本验收，不代表新工作区的目标已经分析。

## 已执行并通过

- 环境：Node.js 24.18.0、Python 3.12.7、REA 6.4.0；JADX 命令报告 1.5.4。
- `make test`：12 项标准库测试通过，覆盖导入/分析副本、摘要变化/新增/缺失、拒绝覆盖、软链接、干净模板、HAR 值移除及私有输出权限。
- `rea mcp doctor --json`：`healthy: true`，stdio 初始化、170 个工具、6 个提示词和无目标请求全部通过。
- 在含空格的临时路径运行完整 CLI：新建 → 导入合成 JS 应用 → 创建分析副本 → REA 静态分析 → 原件再次校验，全部成功。
- REA 实际返回 `index.js` / `price.js` 的模块、导出和静态关系证据；结果保留静态分析限制，没有执行应用。
- 对含合成 cookie、认证 header、URL 凭据、JSON 与未知扩展字段的 HAR 运行脱敏，再由 REA 读取；实际解析到 1 条 POST 记录，保留字段结构，原有测试凭据未保留。
- JSON 配置与 TOML 配置语法可解析。

本次原始结果位于模板工作区的 `notes/evidence/smoke-summary.json`、`smoke-javascript.json` 和 `smoke-har.json`。这些本地结果按设计不复制到新目标，也不纳入版本控制。

## 尚未验证

- Claude Code / Codex 重启后的项目 MCP UI 接入状态；MCP 服务独立握手已通过。
- 真实 APK 的 JADX 反编译及真实 native 目标的 Ghidra/Hopper/IDA 分析。
- 真实业务 HAR 的完整匿名化、生成 API 客户端与服务端联调。
- 运行时抓取、设备操作、工具安装、模型调用预算与生产环境隔离。

模板目录的 `target/` 保持空白，尚未建立真实目标的摘要基线；此时 `make verify` 应失败，不能误报通过。
