✅ PySide6 窗口处理
QMainWindow 创建主界面

使用 self.winId() 获取 HWND 句柄（与 Win32 互操作）

✅ 嵌入桌面（AppBar）
SHAppBarMessage(ABM_NEW, &APPBARDATA) 注册窗口

指定边缘：ABE_LEFT / ABE_RIGHT / ABE_TOP / ABE_BOTTOM

使用 SetWindowPos 设置尺寸和位置

✅ 兼容性 & 注意点分析
1. 操作系统版本
兼容性好：Win7/10/11 都支持 AppBar 机制

注意事项：Win11 多显示器布局和 DPI 缩放下要特别处理

2. 高DPI缩放问题
PySide6 默认支持高DPI，但 Win32 API 中的像素坐标是逻辑像素

需加上 QApplication.setHighDpiScaleFactorRoundingPolicy 设置防止错位

3. 多显示器支持
系统会把 AppBar 注册在主屏，若要支持副屏，需调用：

EnumDisplayMonitors 获取所有屏幕矩形

动态选屏设置窗口边缘位置

4. 任务栏冲突
Win11 的任务栏固定在下方，但用户可手动更改。AppBar 会自动避开任务栏。

不要设置为全屏窗口，否则会强占任务栏区域，引发用户体验问题

5. 焦点 & 窗口层级
不能设为全局焦点抢占窗口（会影响其他窗口切换）

通常设置为 Qt::Tool 类型 + 无边框 + SetWindowPos(... HWND_TOPMOST ...)

6. 系统权限问题
注册 AppBar 不需要管理员权限

但若需开机自启或修改注册表/服务启动，则需要额外权限

✅ 可选增强功能（后续扩展）
功能	技术要点
自动隐藏/显示侧边栏	监听鼠标位置，控制窗口显隐
开机自启	写入注册表 Run 或使用计划任务
通知交互/图标提醒	使用 QSystemTrayIcon + signal
窗口内容动态更新（如新闻）	AI推送、WebSocket 通信等集成接口
