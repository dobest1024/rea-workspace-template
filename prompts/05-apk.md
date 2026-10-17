# Android APK 静态分析

先验证原件并创建 work/input。针对 SCOPE 中的 APK，按 rea --help 确认命令：
inspect-android-package → search-android-classes → inspect-android-class →
inspect-android-method → trace-android-references。参数必须从对应 --help 获取。

1. 记录摘要、包名、版本、min/target SDK、Application、启动 Activity、组件声明和权限。
2. 清点 DEX、assets、资源和 native ABI。区分壳/动态加载迹象与已证明的动态加载行为。
3. 从指定功能入口追踪 UI → 业务类 → 网络/数据库/JNI；方法引用带完整签名和所属 DEX。
4. APK 中找不到的运行时 DEX、split APK 或服务端逻辑记为缺失材料，不能宣称还原完整应用。
5. JNI/native 需要独立 provider；Flutter 的引擎/快照元信息不等于 Dart 源码恢复。

默认不安装 APK、不启动应用、不连接设备。只有已有任务授权覆盖运行时操作时才继续。
首轮最多深入 30 个方法，证据保存到 notes/evidence/，更新架构、发现、未决问题和交接。
