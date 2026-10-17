# REA Workspace Template

一个目标一个工作区：保留原件，在副本上分析，用证据支撑结论。适用于源码、APK、原生二进制、JavaScript/Electron、HAR 和未知文件格式。

参考 [zodchiii 的帖子](https://x.com/zodchiii/status/2109623079429460478)，按 [REA 官方文档](https://github.com/morluto/rea) 和本机 REA 6.4.0 的实际命令整理。模型沿用你自己的设置；帖子中的模型规格、成本与耗时没有作为本模板的承诺。

## 快速开始

### 1. 克隆仓库

先安装 Git、Python 3.11+、Node.js 及 npm，以及你要使用的 Claude Code 或 Codex。脚手架脚本只依赖 Python 标准库，不需要 `pip install` 或在本仓库运行 `npm install`。以下命令以 macOS / Linux 终端为例。

```bash
git clone https://github.com/dobest1024/rea-workspace-template.git
cd rea-workspace-template
```

### 2. 安装 REA 并检查连接

如果还没有 REA，安装本模板验证过的版本：

```bash
npm install --global rea-agents@6.4.0
rea --version
rea mcp doctor --json
```

已有可用 REA 的机器只需运行最后两个检查命令。MCP 自检应返回 `healthy: true`。REA 是独立工具，本仓库提供工作区与客户端配置，不包含 REA 程序和反编译引擎。

### 3. 确认客户端配置

仓库已经包含 REA 的项目配置，克隆后无需手动新建配置文件：

| 客户端 | 已提供的文件 | 作用 |
| --- | --- | --- |
| Claude Code | [`.mcp.json`](.mcp.json) | 启动本机 `rea --mcp` |
| Claude Code | [`.claude/settings.json`](.claude/settings.json)、[`CLAUDE.md`](CLAUDE.md) | 文件权限与分析规则 |
| Codex | [`.codex/config.toml`](.codex/config.toml)、[`AGENTS.md`](AGENTS.md) | REA MCP、超时与分析规则 |

选择一个客户端即可。在工作区根目录启动它，按客户端提示信任项目/启用项目 MCP，再通过 `/mcp` 确认 `rea` 连接。已打开的客户端需要重启或开启新会话加载配置。详细配置和 PATH 排查见下方「REA 接入」。

### 4. 导入目标

可以直接把克隆目录作为第一个目标的工作区。也可以保留它作为干净模板，先创建独立工作区（目标路径必须不存在）：

```bash
# 可选：为每个目标创建独立工作区，配置会一并复制
python3 scripts/workspace.py new ../my-analysis
cd ../my-analysis
```

`new` 不复制 `.git`、旧样本或分析结果；创建出来的目录没有指向本模板仓库的 Git remote。

填写 `notes/SCOPE.md` 中的目标、分析授权和本轮问题，导入一份已整理好的样本：

```bash
python3 scripts/workspace.py import /absolute/path/to/app.apk
python3 scripts/workspace.py verify
python3 scripts/workspace.py stage
```

也可以导入一个源码目录。脚本只复制样本，不运行它；生成 SHA-256 基线并将导入文件设为 `0444`。`stage` 生成可写的 `work/input/`，不会覆盖已有分析。一次导入一个目标；多个相关样本先放入工作区外的同一个目录再导入。不要把原始 HAR、凭据文件或无关数据一并导入。

### 5. 开始分析

从实际存放样本的工作区根目录启动客户端，二选一：

```bash
claude
# 或
codex
```

确认 `/mcp` 中的 `rea` 已连接，然后输入：

```text
先读 AGENTS.md 和 notes/SCOPE.md，按 prompts/05-apk.md 分析这个目标。
本轮先给出入口和功能地图；结论要带证据，区分 CONFIRMED 与 GUESS。
```

源码用 `01-map-repo.md`，其他类型见下表。每轮结束运行 `python3 scripts/workspace.py verify`，按 `07-handoff.md` 收尾。安装了 Make 时也可以用 `make verify`、`make stage`、`make doctor` 这些快捷命令。

## 目录

```text
rea-workspace-template/
├── AGENTS.md                    # 通用分析约定，Codex 自动发现
├── CLAUDE.md                    # 引用同一套约定
├── .claude/settings.json        # Claude 文件保护和基础命令规则
├── .mcp.json                    # Claude 项目 REA MCP
├── .codex/config.toml           # Codex 项目 REA MCP
├── target/                     # 原始样本，导入后不修改
├── work/                       # 分析副本、反编译结果、工具数据库
├── notes/
│   ├── SCOPE.md                 # 问题、范围、授权、验收条件
│   ├── ARCHITECTURE.md          # 架构、入口和数据流
│   ├── findings.md              # 逐条结论与证据
│   ├── renames.md               # 符号重命名记录
│   ├── open-questions.md        # 未决问题
│   ├── HANDOFF.md               # 下一轮接续点
│   ├── target-manifest.json     # 导入命令生成的摘要基线
│   └── evidence/               # 工具原始输出
├── prompts/                    # 七套任务提示词
├── templates/notes/            # 创建新目标时使用的干净笔记
├── scripts/                    # Python 标准库脚本，无 pip 依赖
├── tests/                      # 数据保护及失败路径测试
└── docs/                       # 来源、接入与验收记录
```

`target/`、`work/`、原始工具输出及摘要基线已被 Git 忽略。笔记可能包含业务信息，提交或分享前自行检查。新工作区只复制干净笔记模板，不复制旧目标及分析结果。

## REA 接入

需要 Python 3.11+、Node.js 和 REA。当前验证环境为 Node 24.18.0、REA 6.4.0、Python 3.12.7。按 REA 官方要求，Node 支持 22.19+ 的 22.x、24.11+ 的 24.x 或 26+。

配置中没有 API Key，不会覆盖你的模型或登录方式。安装 REA 后，仓库内的配置即提供项目级 MCP 接入。

Claude Code 的 [`.mcp.json`](.mcp.json)：

```json
{
  "mcpServers": {
    "rea": {
      "command": "rea",
      "args": ["--mcp"]
    }
  }
}
```

Codex 的 [`.codex/config.toml`](.codex/config.toml)：

```toml
[mcp_servers.rea]
command = "rea"
args = ["--mcp"]
startup_timeout_sec = 30
tool_timeout_sec = 600
```

两个项目 MCP 配置都启动 `rea --mcp`，需要启动客户端时 PATH 能找到 `rea`；如 GUI 无法找到，可将 `command` 改成本机 `command -v rea` 输出的绝对路径，并确保 Node 在该客户端 PATH 中。此方式使用已安装版本，不在每次启动时通过 npx 下载。升级全局 REA 后重新运行自检。

Claude Code 从项目根启动后检查 `/mcp`；客户端可能要求信任项目或启用项目 MCP。Codex 的项目配置只在受信任项目中生效，重启/开启新会话后检查 `/mcp`。配置项来源见 [OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。本模板不会自动改写用户级配置或批准客户端提示。

REA 官方还有 `rea setup` 向导，可安装官方配套工作流并注册其他客户端。已有本模板的项目配置时无需重复执行；需要向导时先查看其列出的配置范围，避免重复注册。这里提供的是项目规则与提示词，没有冒充或复制官方 REA skill。

### 按分析类型准备引擎

| 分析类型 | 还需要什么 |
| --- | --- |
| 源码、JS / Electron、已保存 HAR | 对应静态流程无需 Ghidra / IDA |
| APK 的 DEX、类与方法 | JADX 和完整 JDK |
| 原生二进制、APK 内的 `.so` | Ghidra、Hopper 或 IDA 等合适的 provider |

按 [REA 官方安装文档](https://github.com/morluto/rea/blob/main/docs/installation.md) 配置引擎路径；商业引擎需要自己的许可证。MCP 连接成功与反编译引擎就绪是两项独立检查。

## 选择工作流

| 输入 | 提示词 | 第一份交付 |
| --- | --- | --- |
| 陌生源码 | `prompts/01-map-repo.md` | 入口、模块图、最多五条数据流 |
| 已脱敏 HAR | `prompts/02-reconstruct-api.md` | OpenAPI 3.1、TypeScript 客户端 |
| JS / Electron | `prompts/03-javascript.md` | 模块边界、恢复结果、重命名记录 |
| 原生二进制 | `prompts/04-native.md` | 首轮最多 30 个函数及证据 |
| APK | `prompts/05-apk.md` | Manifest、类/方法、JNI 和缺失材料 |
| 未知文件格式 | `prompts/06-file-format.md` | 格式假设、Kaitai 定义与解析器 |
| 本轮收尾 | `prompts/07-handoff.md` | 校验结果、进度、未验证项、下一步 |

这些是任务模板，不是已完成的分析产物。使用哪个提示词，就只生成当前需要的输出。

## 常用静态命令

以下在项目根目录执行，将文件名换成实际样本名；每次用新的证据文件名保留记录。

```bash
# APK；需要 JADX 和完整 JDK
rea inspect-android-package "$PWD/work/input/app.apk" --format json > notes/evidence/apk-01.json

# JS / Electron 目录；无需原生反编译器
rea analyze-javascript-application "$PWD/work/input/app" --format json > notes/evidence/js-01.json

# 仅分析已保存的 HAR，不请求其中 URL
rea inspect-web-network-capture "$PWD/work/input/clean.har" har --format json > notes/evidence/har-01.json

# 按选定原生引擎检查，不把 JADX 传给 --provider
rea doctor --provider ghidra --format json
```

JADX 用于 Java/Kotlin DEX；Ghidra/Hopper/IDA 用于 native。安装一个不意味着另一个可用。provider 路径、JDK 和可选工具请按 [REA 安装文档](https://github.com/morluto/rea/blob/main/docs/installation.md) 配置。脚手架不会安装这些大体积依赖，也不会启动样本或设备。

命令退出码非零时检查保存的错误，不把输出文件存在当作分析成功。`make doctor` 证明 MCP 启动与工具目录可用，不证明某个 provider 或目标分析成功。

## HAR 脱敏

在普通终端运行下列命令，原始抓包和初次脱敏输出都放在工作区外，不交给 agent 读取：

```bash
python3 scripts/sanitize_har.py /private/path/raw.har /private/path/clean.har
```

脚本从允许的结构重新生成 HAR：移除 cookie、认证及其他 header 值、URL 用户信息/query/fragment、重定向值、注释和自定义扩展；JSON 正文只保留字段与类型，字符串变为 `[REDACTED]`，数字变为 `0`，布尔变为 `false`。表单仅保留参数名，其他正文和 base64 内容被替换。输出权限为 `0600`，拒绝覆盖任何已有文件。

它是**结构分析副本**，会丢失业务值、时间、认证方案、分页参数值和速率限制值。占位值不能当作真实样本、枚举或默认值。URL 主机/路径和字段名会保留，可能仍含用户 ID、签名路径或自定义敏感信息：人工复查、替换后才导入。不能承诺任意 HAR 自动完全匿名。

复查后运行 `workspace.py import /private/path/clean.har`，再 `make stage`。输出不是回放用抓包，不能据此宣称客户端联调通过。

## 边界与验证

`.claude/settings.json` 使用 `Read` / `Edit` 文件规则，禁止写原件并限制常见联网命令；这不是不可绕过的隔离层，规则不覆盖任意子进程与 MCP 工具。文件 `0444` 也能被拥有者解除；SHA-256 校验用于发现变化，基线本身不是防篡改存储。强隔离应由只读挂载、受控网络及隔离的分析进程提供。

脚本拒绝软链接和特殊文件，避免误跟随外部路径；导入操作不是面向并发修改源目录的取证采集器。先固定好样本再导入。未自动运行目标，不代表解析未知文件没有风险。

```bash
make test
```

测试覆盖新建工作区、样本导入、不覆盖、摘要变化/新增/缺失检测、软链接拒绝，以及 HAR 凭据移除、结构保留和输出权限。验收状态见 [docs/VALIDATION.md](docs/VALIDATION.md)。
