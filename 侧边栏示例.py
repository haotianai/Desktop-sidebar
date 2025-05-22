"""
侧边栏测试示例
用于测试铺满屏幕高度和推开桌面图标功能
"""

import sys
import traceback
from PySide6.QtWidgets import (QApplication, QPushButton, 
                              QVBoxLayout, QWidget, QLabel, QSpinBox, 
                              QHBoxLayout, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from sidebar_widget import SidebarWidget
from qfluentwidgets import (setTheme, Theme, MSFluentTitleBar, isDarkTheme)

if sys.platform == 'win32' and sys.getwindowsversion().build >= 22000:
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window

class MicaWindow(Window):
    def __init__(self):
        super().__init__()
        self.setTitleBar(MSFluentTitleBar(self))
        if sys.platform == 'win32' and sys.getwindowsversion().build >= 22000:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

class SidebarTestWindow(MicaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("侧边栏测试")
        self.resize(450, 700)
        self.setWindowIcon(QIcon("icon/icon.ico"))
        
        try:
            self.setup_ui()
            self.sidebar = SidebarWidget(self, config_file="sidebar_test.json")
            self.update_sidebar_config()
            
            # 连接信号
            self.sidebar.embedded.connect(self.on_embedded)
            self.sidebar.unembedded.connect(self.on_unembedded)
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            traceback.print_exc()
            raise
    
    def setup_ui(self):
        """创建测试UI"""
        # 创建主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 40, 5, 5)
        
        # 创建主要内容部件
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        layout = QVBoxLayout(self.main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 0, 10, 10)
        
        # 配置区域
        config_frame = QWidget()
        config_frame.setStyleSheet("""
            QWidget { 
                background-color: #2c2c2c;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        config_layout = QVBoxLayout(config_frame)
        
        config_layout.addWidget(QLabel("🔧 侧边栏配置"))
        
        # 方向选择
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("方向:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['左侧', '右侧'])
        self.direction_combo.currentTextChanged.connect(self.update_sidebar_config)
        direction_layout.addWidget(self.direction_combo)
        direction_layout.addStretch()
        config_layout.addLayout(direction_layout)
        
        # 宽度设置
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("宽度:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 600)
        self.width_spin.setValue(430)
        self.width_spin.setSuffix(" px")
        self.width_spin.valueChanged.connect(self.update_sidebar_config)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        config_layout.addLayout(width_layout)
        
        # 顶部偏移设置
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("顶部偏移:"))
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(0, 200)
        self.offset_spin.setValue(0)
        self.offset_spin.setSuffix(" px")
        self.offset_spin.valueChanged.connect(self.update_sidebar_config)
        offset_layout.addWidget(self.offset_spin)
        offset_layout.addStretch()
        config_layout.addLayout(offset_layout)
        
        layout.addWidget(config_frame)
        
        # 控制按钮
        button_frame = QWidget()
        button_frame.setStyleSheet("""
            QWidget { 
                background-color: #2c2c2c;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        button_layout = QVBoxLayout(button_frame)
        
        self.toggle_btn = QPushButton("🔄 切换侧边栏")
        self.toggle_btn.clicked.connect(self.safe_toggle)
        button_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(button_frame)
        
        # 将主部件添加到主布局
        self.mainLayout.addWidget(self.main_widget)
    
    def update_sidebar_config(self):
        """更新侧边栏配置"""
        if hasattr(self, 'sidebar') and self.sidebar is not None:
            try:
                edge = 'left' if self.direction_combo.currentText() == '左侧' else 'right'
                width = self.width_spin.value()
                top_offset = self.offset_spin.value()
                
                self.sidebar.set_config(
                    edge=edge,
                    width=width,
                    top_offset=top_offset,
                    auto_save=True
                )
                
                if self.sidebar.is_embedded:
                    self.sidebar.unembed()
                    self.sidebar.embed()
                
            except Exception as e:
                print(f"⚠️ 配置更新失败: {e}")
    
    def safe_toggle(self):
        """安全的切换方法"""
        try:
            if hasattr(self, 'sidebar') and self.sidebar is not None:
                return self.sidebar.toggle()
            return False
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            return False
    
    def on_embedded(self):
        """侧边栏嵌入回调"""
        self.toggle_btn.setText("🔓 取消嵌入")
    
    def on_unembedded(self):
        """侧边栏取消嵌入回调"""
        self.toggle_btn.setText("📌 嵌入侧边栏")
    
    def closeEvent(self, event):
        """窗口关闭时清理"""
        try:
            if hasattr(self, 'sidebar') and self.sidebar is not None:
                self.sidebar.cleanup()
            super().closeEvent(event)
        except Exception as e:
            print(f"❌ 清理过程出错: {e}")
            super().closeEvent(event)

def main():
    """主函数"""
    try:
        app = QApplication(sys.argv)
        # 设置深色主题
        setTheme(Theme.DARK)
        
        window = SidebarTestWindow()
        window.show()
        
        app.exec()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()