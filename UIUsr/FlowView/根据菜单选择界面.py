import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, \
    QPushButton, QLabel, QStackedWidget, QHBoxLayout


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 创建一个 QTreeWidget 作为左侧的菜单
        menu_tree_widget = QTreeWidget(self)
        menu_tree_widget.setHeaderLabels(['菜单'])

        # 添加菜单项
        item1 = QTreeWidgetItem(menu_tree_widget)
        item1.setText(0, '菜单1')

        item2 = QTreeWidgetItem(menu_tree_widget)
        item2.setText(0, '菜单2')

        # 设置单击菜单时，显示相应的窗口
        menu_tree_widget.itemClicked.connect(self.on_menu_item_clicked)

        # 创建一个 QWidget 作为右侧的窗口容器
        window_container = QWidget(self)

        # 创建一个 QStackedWidget 用于管理窗口的不同页面
        stacked_widget = QStackedWidget(window_container)

        # 添加窗口页面
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)
        layout1.addWidget(QPushButton('按钮1'))
        layout1.addWidget(QLabel('标签1'))
        stacked_widget.addWidget(page1)

        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        layout2.addWidget(QPushButton('按钮2'))
        layout2.addWidget(QLabel('标签2'))
        stacked_widget.addWidget(page2)

        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(menu_tree_widget)
        main_layout.addWidget(stacked_widget)

        # 设置窗口容器的布局
        window_container.setLayout(main_layout)

        # 设置主窗口的中心部分为窗口容器
        self.setCentralWidget(window_container)

        self.setWindowTitle('菜单和窗口')

    def on_menu_item_clicked(self, item, column):
        # 获取菜单项的文本
        menu_text = item.text(0)

        # 根据菜单的选择，切换显示相应的窗口页面
        if menu_text == '菜单1':
            self.centralWidget().layout().itemAt(1).widget().setCurrentIndex(0)
        elif menu_text == '菜单2':
            self.centralWidget().layout().itemAt(1).widget().setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
