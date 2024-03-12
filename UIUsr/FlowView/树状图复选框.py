from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class TreeViewExample(QMainWindow):
    def __init__(self):
        super(TreeViewExample, self).__init__()

        self.setWindowTitle("Tree View Example")
        self.setGeometry(100, 100, 600, 400)

        # 创建树状视图和数据模型
        self.tree_view = QTreeView(self)
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        # 添加根节点
        root_item = QStandardItem("Root")
        root_item.setCheckable(True)  # 设置根节点的复选框
        self.model.appendRow(root_item)

        # 添加子节点
        child_item1 = QStandardItem("Child 1")
        child_item1.setCheckable(True)  # 设置子节点的复选框
        root_item.appendRow(child_item1)

        child_item2 = QStandardItem("Child 2")
        child_item2.setCheckable(True)  # 设置子节点的复选框
        root_item.appendRow(child_item2)

        # 设置树状视图的显示模式
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.expandAll()

        # 设置主窗口布局
        self.setCentralWidget(self.tree_view)

if __name__ == "__main__":
    app = QApplication([])
    window = TreeViewExample()
    window.show()
    app.exec_()
