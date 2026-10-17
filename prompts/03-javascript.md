# JavaScript / Electron 静态分析

先验证原件并创建 work/input。用 REA analyze-javascript-application 获取模块图，
必要时按本机 help 使用 recover-javascript-sources；也可在独立环境使用已安装的 webcrack。
记录工具、版本、命令和输出路径，不运行样本或 npm install 生命周期脚本。

机械恢复完成后，从入口追踪本轮问题，最多深入 30 个函数。
只对 work 中的副本做语义重命名和短注释，每次记录旧名、新名、证据和置信状态。
检查前后语法及逻辑差异，抽查至少 10% 的重命名；无法证明语义一致时明确记录。
标出 Electron renderer / preload / main / native 边界、IPC 调用及证据断点。
更新 notes，校验 target，保留下一轮起点。
