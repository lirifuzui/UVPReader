import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建一个按钮，点击时切换到子页面
        btn_open_child = QPushButton('打开子页面', self)
        btn_open_child.clicked.connect(self.show_child_page)
        layout.addWidget(btn_open_child)

        # 创建一个 QStackedWidget 用于管理页面
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)

        # 将主页面和子页面添加到 QStackedWidget 中
        main_page = QWidget()
        main_page_layout = QVBoxLayout()
        main_page_layout.addWidget(QLabel('这是主页面'))
        main_page.setLayout(main_page_layout)

        child_page = QWidget()
        child_page_layout = QVBoxLayout()
        child_page_layout.addWidget(QLabel('这是子页面'))
        child_page.setLayout(child_page_layout)

        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.addWidget(child_page)

        self.setLayout(layout)
        self.setWindowTitle('主页面')

    def show_child_page(self):
        # 切换到子页面
        self.stacked_widget.setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
