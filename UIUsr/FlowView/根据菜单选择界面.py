import sys

from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, \
    QPushButton, QLabel, QStackedWidget, QHBoxLayout, QSplitter, QSplitterHandle

project_name = 'New project'

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 创建一个 QTreeWidget 作为左侧的菜单
        menu_tree_widget = QTreeWidget(self)
        menu_tree_widget.setHeaderLabels(['\'' + project_name + '\''])

        menu_tree_widget.setFixedWidth(180)
        menu_tree_widget.setMaximumWidth(600)
        menu_tree_widget.setMinimumWidth(20)


        # 添加菜单项
        data = QTreeWidgetItem(menu_tree_widget)
        data.setText(0, 'Data')

        flow_field = QTreeWidgetItem(menu_tree_widget)
        flow_field.setText(0, 'Flow field')

        item2 = QTreeWidgetItem(menu_tree_widget)
        item2.setText(0, '菜单2')


        # 创建菜单的字体
        header_font = QFont()
        header_font.setPointSize(10)  # 设置字体大小
        menu_tree_widget.headerItem().setFont(0, header_font)

        font1 = QFont()
        font1.setPointSize(11)  # 设置字体大小
        data.setFont(0, font1)
        flow_field.setFont(0, font1)


        # 使用CSS样式表来设置背景透明度和边框透明
        menu_tree_widget.setStyleSheet(
            'QTreeWidget { background-color: rgba(255, 255, 255, 0.5); border: 0px solid transparent; }'
            'QHeaderView::section { background-color: rgba(255, 255, 255, 0.5); border: 0px solid transparent: }'
        )

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



        # 创建一个 QSplitter 用于分隔左侧菜单和右侧窗口
        splitter = QSplitter(self)
        splitter.addWidget(menu_tree_widget)
        splitter.addWidget(window_container)

        self.setCentralWidget(splitter)

        # 设置窗口标题
        self.setWindowTitle('NewVUP - \'' + project_name + '\'')

        # 设置窗口初始大小为全屏
        self.showMaximized()

        splitter.setSizes([180, 1])

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
