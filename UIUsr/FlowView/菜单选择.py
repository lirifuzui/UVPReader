import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QFont

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 创建一个 QTreeWidget 作为主窗口的中心部分
        tree_widget = QTreeWidget(self)
        tree_widget.setHeaderLabels(['菜单'])

        # 添加一级菜单项
        item1 = QTreeWidgetItem(tree_widget)
        item1.setText(0, '一级菜单1')
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # 设置字体大小
        item1.setFont(0, font)

        item2 = QTreeWidgetItem(tree_widget)
        item2.setText(0, '一级菜单2')
        item2.setFont(0, font)

        # 添加二级菜单项
        subitem1_1 = QTreeWidgetItem(item1)
        subitem1_1.setText(0, '二级菜单1-1')

        subitem1_2 = QTreeWidgetItem(item1)
        subitem1_2.setText(0, '二级菜单1-2')

        subitem2_1 = QTreeWidgetItem(item2)
        subitem2_1.setText(0, '二级菜单2-1')

        # 设置单击一级菜单时，显示相应的二级菜单
        tree_widget.itemClicked.connect(self.on_tree_item_clicked)

        self.setCentralWidget(tree_widget)
        self.setWindowTitle('树状菜单')

    def on_tree_item_clicked(self, item, column):
        # 获取一级菜单项的文本
        first_level_text = item.text(0)

        # 在这里可以根据一级菜单的选择，进行相应的操作
        print(f'选择了一级菜单：{first_level_text}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
