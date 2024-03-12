import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QSplitter

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 创建一个 QTreeWidget 作为左侧的菜单
        menu_tree_widget = QTreeWidget(self)
        menu_tree_widget.setColumnCount(1)  # 设置列数为1
        menu_tree_widget.setHeaderLabels(['菜单'])

        # 添加菜单项
        item1 = QTreeWidgetItem(menu_tree_widget)
        item1.setText(0, '菜单1')

        item2 = QTreeWidgetItem(menu_tree_widget)
        item2.setText(0, '菜单2')

        # 创建一个 QWidget 作为右侧的窗口容器
        window_container = QWidget(self)

        # 创建一个 QSplitter 用于分隔左侧菜单和右侧窗口
        splitter = QSplitter(self)
        splitter.addWidget(menu_tree_widget)
        splitter.addWidget(window_container)

        # 设置主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)

        # 设置窗口的布局
        self.setLayout(main_layout)
        self.setWindowTitle('可调整尺寸的树状菜单和窗口')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
