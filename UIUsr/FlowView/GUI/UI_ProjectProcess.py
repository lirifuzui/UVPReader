import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QStandardItemModel, QStandardItem, QColor, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, \
    QPushButton, QLabel, QStackedWidget, QHBoxLayout, QSplitter, QFrame, QTreeView

Font_size = 14


class Project_process_QTreeV(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setHeaderHidden(True)  # 隐藏列表标题
        self.setMinimumWidth(200)  # 设置最小宽为180
        self.setMaximumWidth(340)  # 设置最大宽为260
        self.setStyleSheet(
            'QTreeView { background-color: rgba(255, 255, 255, 1); border: 3px solid transparent; }'
        )  # 设置背景样式
        self.item_font = QFont("Times New Roman", Font_size)  # 预设字体字号

        # =======================================================================
        # 添加 geomtry 项
        self.item_geom = QStandardItem("Geomtry")
        icon_geom = QIcon("Icon/icon_tree_geom.jpg")
        self.item_geom.setIcon(icon_geom)
        self.item_geom.setCheckable(False)
        self.item_geom.setEditable(False)
        self.model.appendRow(self.item_geom)
        self.item_geom.setFont(self.item_font)
        self.item_geom.setCheckState(Qt.Unchecked)
        self.expand(self.model.indexFromItem(self.item_geom))  # 默认展开
        # 添加 geomtry 项中的子项 cylinder container 项
        self.item_cylinder = QStandardItem("Container(cylinder)")
        self.item_cylinder.setCheckable(True)
        self.item_cylinder.setEditable(False)
        self.item_geom.appendRow(self.item_cylinder)
        self.item_cylinder.setFont(self.item_font)
        self.item_cylinder.setCheckState(Qt.Unchecked)
        # 添加 geomtry 项中的子项 pipeline 项
        self.item_pipeline = QStandardItem("Pipeline")
        self.item_pipeline.setCheckable(True)
        self.item_pipeline.setEditable(False)
        self.item_geom.appendRow(self.item_pipeline)
        self.item_pipeline.setFont(self.item_font)
        self.item_pipeline.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 data 项
        self.item_data = QStandardItem("Data")
        self.item_data.setCheckable(False)
        self.item_data.setEditable(False)
        self.model.appendRow(self.item_data)
        self.item_data.setFont(self.item_font)
        self.item_data.setCheckState(Qt.Unchecked)
        self.expand(self.model.indexFromItem(self.item_data))  # 默认展开
        # 添加 data 项中的子项 Load
        self.item_load_data = QStandardItem("Load")
        self.item_load_data.setCheckable(True)
        self.item_load_data.setEditable(False)
        self.item_data.appendRow(self.item_load_data)
        self.item_load_data.setFont(self.item_font)
        self.item_load_data.setCheckState(Qt.Unchecked)
        # 添加 data 项中的子项 Measurement
        self.item_measure = QStandardItem("Measure")
        self.item_measure.setCheckable(True)
        self.item_measure.setEditable(False)
        self.item_data.appendRow(self.item_measure)
        self.item_measure.setFont(self.item_font)
        self.item_measure.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 analysis 项
        self.item_analysis = QStandardItem("Analysis")
        self.item_analysis.setCheckable(True)
        self.item_analysis.setEditable(False)
        self.model.appendRow(self.item_analysis)
        self.item_analysis.setFont(self.item_font)
        self.item_analysis.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 fields 项
        self.item_fields = QStandardItem("Fields")
        self.item_fields.setCheckable(True)
        self.item_fields.setEditable(False)
        self.model.appendRow(self.item_fields)
        self.item_fields.setFont(self.item_font)
        self.item_fields.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 results 项
        self.item_results = QStandardItem("Results")
        self.item_results.setCheckable(True)
        self.item_results.setEditable(False)
        self.model.appendRow(self.item_results)
        self.item_results.setFont(self.item_font)
        self.item_results.setCheckState(Qt.Unchecked)

        # 创建逻辑，这里是连接槽函数
        self.model.itemChanged.connect(self.__onStateChanged)

    # =======================================================================
    # 制作逻辑，如果完成了一些项，另一些想将被锁定
    def __onStateChanged(self, item):
        # 制作逻辑，如果Load和Measurement中任意一个被选中，就会锁定另一个,同时 Data 会被选中
        if item == self.item_load_data or item == self.item_measure:
            if self.item_load_data.checkState() == Qt.Unchecked and self.item_measure.checkState() == Qt.Unchecked:
                self.item_data.setCheckState(Qt.Unchecked)
                self.item_load_data.setFlags(Qt.ItemFlags(int("110001", 2)))
                # 位数从右到左，（1）、可编辑（2）、可拖拽（4）、可放入（8）、可勾选（16）、可交互（32）
                self.item_measure.setFlags(Qt.ItemFlags(int("110001", 2)))
            elif self.item_load_data.checkState() == Qt.Checked:
                self.item_data.setCheckState(Qt.Checked)
                self.item_measure.setFlags(Qt.ItemIsUserCheckable)
            elif self.item_measure.checkState() == Qt.Checked:
                self.item_data.setCheckState(Qt.Checked)
                self.item_load_data.setFlags(Qt.ItemIsUserCheckable)

        if item == self.item_cylinder or item == self.item_pipeline:
            if self.item_cylinder.checkState() == Qt.Unchecked and self.item_pipeline.checkState() == Qt.Unchecked:
                self.item_geom.setCheckState(Qt.Unchecked)
                self.item_cylinder.setFlags(Qt.ItemFlags(int("110001", 2)))
                # 位数从右到左，（1）、可编辑（2）、可拖拽（4）、可放入（8）、可勾选（16）、可交互（32）
                self.item_pipeline.setFlags(Qt.ItemFlags(int("110001", 2)))
            elif self.item_cylinder.checkState() == Qt.Checked:
                self.item_geom.setCheckState(Qt.Checked)
                self.item_pipeline.setFlags(Qt.ItemIsUserCheckable)
            elif self.item_pipeline.checkState() == Qt.Checked:
                self.item_geom.setCheckState(Qt.Checked)
                self.item_cylinder.setFlags(Qt.ItemIsUserCheckable)

    # =======================================================================


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Project_process_QTreeV()
    window.show()
    sys.exit(app.exec_())
