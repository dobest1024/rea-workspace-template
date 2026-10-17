# 从已脱敏 HAR 重建 API

只分析 SCOPE 指定并人工复查过的 HAR，不访问其中 URL，不读取原始抓包。
先使用 REA inspect-web-network-capture，保存原始证据；引用 entry 序号与 JSON 路径。

清点 method、path、参数名、请求/响应结构、已观察到的状态码及认证 header 名。
本模板脱敏器会替换所有值；[REDACTED]、0、false 都是占位值，不能推断枚举、默认值、
分页边界、必填性或业务规则。未保存的速率限制值及认证类型标为未知。

生成 notes/openapi.yaml（OpenAPI 3.1），给操作附 x-evidence 与推断说明；
只描述抓包实际覆盖的操作，不把样本中出现字段等同于 required。
据此生成 notes/client.ts，基础 URL 和认证由调用方注入，不带真实凭据，不自动发送请求。
验证 schema 和 TypeScript 类型，写清执行过的检查；未安装校验器时记录缺口。
更新架构、未决问题和交接笔记。不得宣称已与真实服务联调。
