import win32con
import win32gui
import win32api
import ctypes
import json
import os

ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003

ABE_LEFT = 0
ABE_TOP = 1
ABE_RIGHT = 2
ABE_BOTTOM = 3

CONFIG_PATH = 'sidebar_config.json'

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint32),
        ("hWnd", ctypes.c_void_p),
        ("uCallbackMessage", ctypes.c_uint32),
        ("uEdge", ctypes.c_uint32),
        ("rc", ctypes.c_int32 * 4),
        ("lParam", ctypes.c_int32),
    ]

def shappbarmessage(msg, abd):
    shell32 = ctypes.windll.shell32
    return shell32.SHAppBarMessage(msg, ctypes.byref(abd))

class AppBar:
    def __init__(self, hwnd, edge=ABE_LEFT, width=300, height=None, top_offset=0):
        self.hwnd = hwnd
        self.edge = edge
        self.width = width
        self.height = height
        self.top_offset = top_offset

    def register(self):
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.hwnd)
        abd.uCallbackMessage = 0
        abd.uEdge = self.edge
        abd.lParam = 0
        shappbarmessage(ABM_NEW, abd)
        self.set_pos()

    def set_pos(self):
        # 获取屏幕分辨率
        screen = win32api.GetMonitorInfo(win32api.MonitorFromWindow(self.hwnd))
        work_area = screen['Work']      # 工作区域 (排除任务栏)
        monitor_area = screen['Monitor']  # 完整屏幕区域
        
        print(f"[DEBUG] 工作区域: {work_area}")
        print(f"[DEBUG] 完整屏幕: {monitor_area}")
        print(f"[DEBUG] 侧边栏配置: edge={self.edge}, width={self.width}, height={self.height}, top_offset={self.top_offset}")
        
        # 🎯 关键修改：使用完整屏幕区域来实现铺满屏幕高度
        l, t, r, b = monitor_area  # 使用完整屏幕而不是工作区域

        rect = [l, t, r, b]
        if self.edge in (ABE_LEFT, ABE_RIGHT):
            rect[1] += self.top_offset
            # 🔧 铺满屏幕高度：如果没有指定高度，使用完整屏幕高度减去顶部偏移
            if self.height is None:
                rect[3] = b  # 使用屏幕底部，铺满整个高度
            else:
                rect[3] = rect[1] + self.height
            
            if self.edge == ABE_LEFT:
                rect[2] = rect[0] + self.width
            else:
                rect[0] = rect[2] - self.width
        
        # 📐 计算最终尺寸
        final_width = rect[2] - rect[0]
        final_height = rect[3] - rect[1]
        print(f"[DEBUG] 最终矩形: {rect}")
        print(f"[DEBUG] 最终尺寸: 宽度={final_width}px, 高度={final_height}px")
        
        # 🚀 这个部分是关键：告诉Windows为侧边栏保留空间
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.hwnd)
        abd.uCallbackMessage = 0
        abd.uEdge = self.edge
        abd.rc = (ctypes.c_int32 * 4)(*rect)
        abd.lParam = 0

        # 查询位置 - 让Windows调整矩形以避免与其他AppBar冲突
        shappbarmessage(ABM_QUERYPOS, abd)
        print(f"[DEBUG] 查询后的矩形: {list(abd.rc)}")
        
        # 设置位置 - 正式注册这个区域
        shappbarmessage(ABM_SETPOS, abd)
        print(f"[DEBUG] 设置后的矩形: {list(abd.rc)}")
        
        # 🎯 关键：设置窗口位置和大小
        # HWND_TOPMOST 确保窗口始终在最上层
        # SWP_NOACTIVATE 确保窗口不会抢夺焦点
        result = win32gui.SetWindowPos(
            self.hwnd, 
            win32con.HWND_TOPMOST,  # 置顶
            rect[0], rect[1],       # 位置
            rect[2] - rect[0],      # 宽度
            rect[3] - rect[1],      # 高度
            win32con.SWP_NOACTIVATE # 不激活窗口
        )
        
        if result:
            print(f"✅ 窗口位置设置成功")
        else:
            print(f"❌ 窗口位置设置失败")
        
        # 📊 输出最终状态
        actual_rect = win32gui.GetWindowRect(self.hwnd)
        print(f"[DEBUG] 实际窗口矩形: {actual_rect}")
        print(f"[DEBUG] 实际尺寸: 宽度={actual_rect[2]-actual_rect[0]}px, 高度={actual_rect[3]-actual_rect[1]}px")

    def unregister(self):
        print(f"[DEBUG] 开始取消注册AppBar...")
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.hwnd)
        abd.uCallbackMessage = 0
        abd.uEdge = self.edge
        abd.lParam = 0
        result = shappbarmessage(ABM_REMOVE, abd)
        print(f"[DEBUG] 取消注册结果: {result}")

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}