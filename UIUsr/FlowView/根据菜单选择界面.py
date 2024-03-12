import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, \
    QPushButton, QLabel, QStackedWidget, QHBoxLayout, QSplitter, QFrame

project_name = 'New project'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('NewVUP - \'' + project_name + '\'')
        self.menu_widget = QTreeWidget(self)
        self.detail_widget = QStackedWidget(self)
        self.MainWidget()
        self.SetMenuTree()
        self.SetDetailWidget()

    def on_menu_item_clicked(self, item, column):
        menu_text = item.text(0)
        if menu_text == 'Data':
            self.detail_widget.setCurrentIndex(0)
        elif menu_text == 'Flow field':
            self.detail_widget.setCurrentIndex(1)

    def SetMenuTree(self):
        Menu_font_1 = QFont("Times New Roman", 11)
        data = QTreeWidgetItem(self.menu_widget)
        data.setText(0, 'Data')
        data.setFont(0, Menu_font_1)

        flow_field = QTreeWidgetItem(self.menu_widget)
        flow_field.setText(0, 'Flow field')
        flow_field.setFont(0, Menu_font_1)

    def SetDetailWidget(self):
        data_page = QWidget()
        layout1 = QVBoxLayout(data_page)
        layout1.addWidget(QPushButton('按钮1'))
        layout1.addWidget(QLabel('标签1'))
        self.detail_widget.addWidget(data_page)

        flow_field_page = QWidget()
        layout2 = QVBoxLayout(flow_field_page)
        layout2.addWidget(QPushButton('按钮2'))
        layout2.addWidget(QLabel('标签2'))
        self.detail_widget.addWidget(flow_field_page)

    def MainWidget(self):
        self.menu_widget = QTreeWidget(self)
        self.menu_widget.setHeaderHidden(True)
        self.menu_widget.setMaximumWidth(300)
        self.menu_widget.setMinimumWidth(180)
        self.menu_widget.setStyleSheet(
            'QTreeWidget { background-color: rgba(255, 255, 255, 0.7); border: 3px solid transparent; }')
        self.detail_widget.setMinimumSize(900, 600)
        self.menu_widget.itemClicked.connect(self.on_menu_item_clicked)

        splitter = QSplitter(Qt.Horizontal)  # Change orientation to horizontal
        splitter.addWidget(self.menu_widget)
        splitter.addWidget(self.detail_widget)
        splitter_line = QFrame(self)
        splitter_line.setFrameShape(QFrame.VLine)
        splitter_line.setFrameShadow(QFrame.Sunken)
        splitter.insertWidget(1, splitter_line)
        self.setCentralWidget(splitter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
