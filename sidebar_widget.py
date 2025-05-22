"""
Windows 侧边栏组件模块
提供简单易用的侧边栏嵌入功能

使用示例:
    from sidebar_widget import SidebarWidget
    
    # 在你的窗口类中
    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            # ... 其他初始化代码 ...
            
            # 创建侧边栏组件
            self.sidebar = SidebarWidget(self)
            
            # 添加切换按钮
            toggle_btn = QPushButton("切换侧边栏")
            toggle_btn.clicked.connect(self.sidebar.toggle)
"""

import json
import os
from typing import Optional, Dict, Any, Callable
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt, QObject, Signal
from appbar_helper import AppBar, ABE_LEFT, ABE_RIGHT

class SidebarWidget(QObject):
    """
    侧边栏组件类
    
    提供简单的侧边栏嵌入/取消功能
    """
    
    # 信号定义
    embedded = Signal()      # 嵌入成功信号
    unembedded = Signal()    # 取消嵌入信号
    error = Signal(str)      # 错误信号
    
    def __init__(self, 
                 window: QMainWindow,
                 config_file: str = "sidebar_config.json",
                 default_config: Optional[Dict[str, Any]] = None):
        """
        初始化侧边栏组件
        
        Args:
            window: 要嵌入的主窗口
            config_file: 配置文件路径
            default_config: 默认配置字典
        """
        super().__init__()
        
        self.window = window
        self.config_file = config_file
        self.appbar: Optional[AppBar] = None
        self.is_embedded = False
        
        # 保存窗口状态
        self.saved_geometry = None
        self.saved_window_flags = None
        
        # 默认配置
        self.default_config = default_config or {
            'edge': 'left',        # 'left' 或 'right'
            'width': 300,          # 宽度
            'top_offset': 0,       # 顶部偏移
            'auto_save': True,     # 是否自动保存配置
        }
        
        # 加载配置
        self.config = self.load_config()
        
        # 回调函数
        self.on_embedded: Optional[Callable] = None
        self.on_unembedded: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def set_config(self, **kwargs):
        """
        设置配置参数
        
        支持的参数:
            edge: 'left' 或 'right'
            width: 宽度 (int)
            top_offset: 顶部偏移 (int)
            auto_save: 是否自动保存配置 (bool)
        """
        for key, value in kwargs.items():
            if key in self.default_config:
                self.config[key] = value
            else:
                raise ValueError(f"不支持的配置参数: {key}")
        
        if self.config.get('auto_save', True):
            self.save_config()
    
    def embed(self) -> bool:
        """
        嵌入为侧边栏
        
        Returns:
            bool: 是否成功嵌入
        """
        if self.is_embedded:
            return True
        
        try:
            # 保存当前窗口状态
            self.saved_geometry = self.window.geometry()
            self.saved_window_flags = self.window.windowFlags()
            
            # 获取配置
            edge_str = self.config.get('edge', 'left')
            edge = ABE_LEFT if edge_str == 'left' else ABE_RIGHT
            width = self.config.get('width', 300)
            top_offset = self.config.get('top_offset', 0)
            
            # 获取窗口句柄
            hwnd = int(self.window.winId())
            
            # 设置无边框窗口
            self.window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.window.show()
            
            # 创建并注册AppBar
            self.appbar = AppBar(hwnd, edge=edge, width=width, top_offset=top_offset)
            self.appbar.register()
            
            self.is_embedded = True
            
            # 保存状态到配置
            if self.config.get('auto_save', True):
                self.save_config()
            
            # 发射信号和调用回调
            self.embedded.emit()
            if self.on_embedded:
                self.on_embedded()
            
            return True
            
        except Exception as e:
            error_msg = f"嵌入失败: {str(e)}"
            self.error.emit(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def unembed(self) -> bool:
        """
        取消侧边栏嵌入
        
        Returns:
            bool: 是否成功取消嵌入
        """
        if not self.is_embedded:
            return True
        
        try:
            # 取消注册AppBar
            if self.appbar:
                self.appbar.unregister()
                self.appbar = None
            
            # 恢复窗口标志
            if self.saved_window_flags is not None:
                self.window.setWindowFlags(self.saved_window_flags)
            else:
                self.window.setWindowFlags(Qt.Window)
            
            self.window.show()
            
            # 恢复窗口几何信息
            if self.saved_geometry is not None:
                self.window.setGeometry(self.saved_geometry)
            
            self.is_embedded = False
            
            # 保存状态到配置
            if self.config.get('auto_save', True):
                self.save_config()
            
            # 发射信号和调用回调
            self.unembedded.emit()
            if self.on_unembedded:
                self.on_unembedded()
            
            return True
            
        except Exception as e:
            error_msg = f"取消嵌入失败: {str(e)}"
            self.error.emit(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def toggle(self) -> bool:
        """
        切换侧边栏状态
        
        Returns:
            bool: 操作是否成功
        """
        if self.is_embedded:
            return self.unembed()
        else:
            return self.embed()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_to_save = self.config.copy()
            config_to_save['is_embedded'] = self.is_embedded
            
            # 如果当前不是嵌入状态，保存窗口几何信息
            if not self.is_embedded and self.window:
                geometry = self.window.geometry()
                config_to_save['window_geometry'] = {
                    'x': geometry.x(),
                    'y': geometry.y(),
                    'width': geometry.width(),
                    'height': geometry.height()
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"保存配置失败: {str(e)}"
            self.error.emit(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def load_config(self) -> Dict[str, Any]:
        """从文件加载配置"""
        config = self.default_config.copy()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    config.update(saved_config)
            except Exception as e:
                error_msg = f"加载配置失败: {str(e)}"
                self.error.emit(error_msg)
                if self.on_error:
                    self.on_error(error_msg)
        
        return config
    
    def restore_window_geometry(self):
        """恢复窗口几何信息"""
        window_geometry = self.config.get('window_geometry')
        if window_geometry and self.window:
            from PySide6.QtCore import QRect
            geometry = QRect(
                window_geometry['x'],
                window_geometry['y'],
                window_geometry['width'],
                window_geometry['height']
            )
            self.window.setGeometry(geometry)
    
    def cleanup(self):
        """清理资源（通常在窗口关闭时调用）"""
        if self.is_embedded:
            self.unembed()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前状态信息
        
        Returns:
            dict: 包含当前状态的字典
        """
        return {
            'is_embedded': self.is_embedded,
            'config': self.config.copy(),
            'has_saved_geometry': self.saved_geometry is not None
        }


class SidebarMixin:
    """
    侧边栏混入类
    
    为现有的QMainWindow类添加侧边栏功能
    """
    
    def init_sidebar(self, 
                    config_file: str = "sidebar_config.json",
                    default_config: Optional[Dict[str, Any]] = None,
                    auto_restore: bool = True):
        """
        初始化侧边栏功能
        
        Args:
            config_file: 配置文件路径
            default_config: 默认配置
            auto_restore: 是否自动恢复窗口几何信息
        """
        self.sidebar = SidebarWidget(self, config_file, default_config)
        
        if auto_restore:
            self.sidebar.restore_window_geometry()
        
        # 连接窗口关闭事件
        original_close_event = getattr(self, 'closeEvent', None)
        
        def closeEvent(event):
            self.sidebar.cleanup()
            if original_close_event:
                original_close_event(event)
        
        self.closeEvent = closeEvent
    
    def toggle_sidebar(self):
        """切换侧边栏状态"""
        return self.sidebar.toggle()
    
    def embed_sidebar(self):
        """嵌入侧边栏"""
        return self.sidebar.embed()
    
    def unembed_sidebar(self):
        """取消嵌入侧边栏"""
        return self.sidebar.unembed()