
# 🪟 PySide6 嵌入式桌面侧边栏窗口（AppBar 实现）

本项目展示如何使用 **PySide6 + Win32 API** 实现嵌入 Windows 桌面的侧边栏（AppBar），支持多显示器、高 DPI 缩放，兼容 Win7 / Win10 / Win11，适用于构建如任务栏工具栏、系统辅助工具、AI 提示栏等场景。

---

## ✅ 功能特性

- 使用 `QMainWindow` 构建主界面窗口
- 获取窗口句柄 `self.winId()` 实现 Win32 API 互操作
- 通过 `SHAppBarMessage(ABM_NEW)` 注册 AppBar 窗口
- 支持指定窗口边缘（左/右/上/下）：`ABE_LEFT / ABE_RIGHT / ABE_TOP / ABE_BOTTOM`
- 使用 `SetWindowPos` 精确设置窗口尺寸与位置
- 自动避开系统任务栏，不遮挡用户操作
- 多屏幕兼容，可动态选择注册在哪个显示器
- 高 DPI 缩放兼容，适配不同显示器缩放比例

---

## 🧱 技术要点

### 📌 Win32 API 嵌入桌面

```cpp
APPBARDATA abd = {...};
abd.uEdge = ABE_LEFT; // 可设置为 ABE_RIGHT / ABE_TOP / ABE_BOTTOM
SHAppBarMessage(ABM_NEW, &abd);
```

### 📌 设置窗口位置与层级

```cpp
SetWindowPos(hwnd, HWND_TOPMOST, x, y, width, height, SWP_NOACTIVATE);
```

> 建议设置为 `Qt.Tool` 类型 + 无边框 + 最顶层，确保不打断用户正常焦点切换

---

## 🖥️ 多显示器支持

- 使用 `EnumDisplayMonitors()` 获取所有显示器的矩形信息
- 根据用户选择的显示器和边缘方向注册窗口
- 支持多屏布局、主副屏切换等场景

---

## 🧮 高 DPI 缩放支持

PySide6 默认启用了高 DPI 支持，但与 Win32 API 的坐标需统一。

添加以下代码以防止坐标错位：

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

---

## 🧠 焦点控制与体验优化

- 窗口类型应为 `Qt.Tool`，不会打断其他程序的焦点
- 不建议设为全屏，否则会覆盖任务栏，引起用户困扰
- 避免设置为“焦点强制抢占窗口”

---

## ⚙️ 系统权限与兼容性

| 项目         | 支持情况 |
|--------------|----------|
| 系统版本     | ✅ Win7 / Win10 / Win11 |
| 注册 AppBar  | ✅ 无需管理员权限 |
| 开机自启     | ❗ 需要写注册表或创建计划任务，需管理员权限 |
| 高 DPI 显示  | ✅ PySide6 默认支持，需坐标同步 |
| 多显示器     | ✅ 支持，需使用 Win32 API 获取屏幕信息 |

---

## 🚀 可选增强功能（推荐扩展）

| 功能                      | 技术说明 |
|---------------------------|-----------|
| 自动隐藏/显示侧边栏      | 鼠标靠近屏幕边缘时自动展开 |
| 开机自启                  | 写入注册表 `Run` 或计划任务 |
| 系统托盘图标交互          | 使用 `QSystemTrayIcon` 实现弹出菜单、退出等操作 |
| 实时动态内容展示          | 使用 WebSocket 或后台 AI 接口推送 |
| 窗口点击穿透              | 可设置 `WS_EX_TRANSPARENT` 属性实现“点击穿透”效果 |

---

## 📁 目录结构示意

```bash
sidebar_appbar/
├── main.py                  # 主程序入口
├── appbar_utils.py          # 注册 AppBar 的封装
├── screen_helper.py         # 多屏幕获取与处理
├── resources/
│   └── icon.png             # 托盘图标资源
├── docs/
│   └── demo_screenshot.png  # 效果图
└── README.md
```

---

## 💻 安装依赖

```bash
pip install PySide6
```

---

## 🖼️ 示例效果图

![示例图](docs/demo_screenshot.png)

---

## 🧪 示例代码片段

```python
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt
import ctypes
from appbar_utils import register_appbar, set_window_pos

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFixedWidth(80)
        self.show()
        hwnd = int(self.winId())
        register_appbar(hwnd, edge='left')
        set_window_pos(hwnd, x=0, y=0, w=80, h=QApplication.primaryScreen().size().height())
```

---

## 📜 License

本项目遵循 [MIT License](https://opensource.org/licenses/MIT)

---


欢迎 PR 和 Star 🌟 支持项目发展！
