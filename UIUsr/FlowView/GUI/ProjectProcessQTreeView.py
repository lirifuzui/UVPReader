import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import QApplication, QTreeView

Font_size = 14


class Project_process_QTV(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setHeaderHidden(True)  # 隐藏列表标题
        self.setMinimumWidth(200)  # 设置最小宽为200
        self.setStyleSheet(
            'QTreeView { background-color: rgba(255, 255, 255, 1); border: 3px solid transparent; }'
        )  # 设置背景样式
        self.item_font = QFont("Times New Roman", Font_size)  # 预设字体字号

        # =======================================================================
        # 添加 geomtry 项
        self.item_geom = QStandardItem("Geomtry")
        icon_geom = QIcon("Icon_Tree_ProjectProcess/icon_geom.jpg")
        self.item_geom.setIcon(icon_geom)
        self.item_geom.setCheckable(False)
        self.item_geom.setEditable(False)
        self.model.appendRow(self.item_geom)
        self.item_geom.setFont(self.item_font)
        self.item_geom.setCheckState(Qt.Unchecked)
        self.expand(self.model.indexFromItem(self.item_geom))  # 默认展开
        # 添加 geomtry 项中的子项 cylinder container 项
        self.item_cylinder = QStandardItem("Container(cylinder)")
        icon_cylinder = QIcon("Icon_Tree_ProjectProcess/icon_cylinder.jpg")
        self.item_cylinder.setIcon(icon_cylinder)
        self.item_cylinder.setCheckable(True)
        self.item_cylinder.setEditable(False)
        self.item_geom.appendRow(self.item_cylinder)
        self.item_cylinder.setFont(self.item_font)
        self.item_cylinder.setCheckState(Qt.Unchecked)
        # 添加 geomtry 项中的子项 pipeline 项
        self.item_pipeline = QStandardItem("Pipeline")
        icon_pipeline = QIcon("Icon_Tree_ProjectProcess/icon_pipeline.jpg")
        self.item_pipeline.setIcon(icon_pipeline)
        self.item_pipeline.setCheckable(True)
        self.item_pipeline.setEditable(False)
        self.item_geom.appendRow(self.item_pipeline)
        self.item_pipeline.setFont(self.item_font)
        self.item_pipeline.setCheckState(Qt.Unchecked)
        # 添加 geomtry 项中的子项 custom 项
        self.item_custom = QStandardItem("Custom")
        icon_custom = QIcon("Icon_Tree_ProjectProcess/icon_custom.jpg")
        self.item_custom.setIcon(icon_pipeline)
        self.item_custom.setCheckable(True)
        self.item_custom.setEditable(False)
        self.item_geom.appendRow(self.item_custom)
        self.item_custom.setFont(self.item_font)
        self.item_custom.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 data 项
        self.item_data = QStandardItem("Data")
        icon_data = QIcon("Icon_Tree_ProjectProcess/icon_data.jpg")
        self.item_data.setIcon(icon_data)
        self.item_data.setCheckable(False)
        self.item_data.setEditable(False)
        self.model.appendRow(self.item_data)
        self.item_data.setFont(self.item_font)
        self.item_data.setCheckState(Qt.Unchecked)
        self.expand(self.model.indexFromItem(self.item_data))  # 默认展开
        # 添加 data 项中的子项 Load
        self.item_load_data = QStandardItem("Load")
        icon_load_data = QIcon("Icon_Tree_ProjectProcess/icon_load_data.jpg")
        self.item_load_data.setIcon(icon_load_data)
        self.item_load_data.setCheckable(True)
        self.item_load_data.setEditable(False)
        self.item_data.appendRow(self.item_load_data)
        self.item_load_data.setFont(self.item_font)
        self.item_load_data.setCheckState(Qt.Unchecked)
        # 添加 data 项中的子项 Measurement
        self.item_measure = QStandardItem("Measure")
        icon_measure = QIcon("Icon_Tree_ProjectProcess/icon_measure.jpg")
        self.item_measure.setIcon(icon_measure)
        self.item_measure.setCheckable(True)
        self.item_measure.setEditable(False)
        self.item_data.appendRow(self.item_measure)
        self.item_measure.setFont(self.item_font)
        self.item_measure.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 analysis 项
        self.item_analysis = QStandardItem("Analysis")
        icon_analysis = QIcon("Icon_Tree_ProjectProcess/icon_analysis.jpg")
        self.item_analysis.setIcon(icon_analysis)
        self.item_analysis.setCheckable(True)
        self.item_analysis.setEditable(False)
        self.model.appendRow(self.item_analysis)
        self.item_analysis.setFont(self.item_font)
        self.item_analysis.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 fields 项
        self.item_fields = QStandardItem("Fields")
        icon_fields = QIcon("Icon_Tree_ProjectProcess/icon_fields.jpg")
        self.item_fields.setIcon(icon_fields)
        self.item_fields.setCheckable(True)
        self.item_fields.setEditable(False)
        self.model.appendRow(self.item_fields)
        self.item_fields.setFont(self.item_font)
        self.item_fields.setCheckState(Qt.Unchecked)

        # ------------------------------------------------------
        # 添加 results 项
        self.item_results = QStandardItem("Results")
        icon_results = QIcon("Icon_Tree_ProjectProcess/icon_results.jpg")
        self.item_results.setIcon(icon_results)
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
        if item in (self.item_load_data, self.item_measure):
            if all(item.checkState() == Qt.Unchecked for item in (self.item_load_data, self.item_measure)):
                self.item_data.setCheckState(Qt.Unchecked)
                self.item_load_data.setFlags(Qt.ItemFlags(int("110001", 2)))
                # 位数从右到左，（1）、可编辑（2）、可拖拽（4）、可放入（8）、可勾选（16）、可交互（32）
                self.item_measure.setFlags(Qt.ItemFlags(int("110001", 2)))
            elif self.item_load_data.checkState() == Qt.Checked:
                self.item_data.setCheckState(Qt.Checked)
                self.item_measure.setFlags(Qt.ItemFlags(int("000000", 2)))
            elif self.item_measure.checkState() == Qt.Checked:
                self.item_data.setCheckState(Qt.Checked)
                self.item_load_data.setFlags(Qt.ItemFlags(int("000000", 2)))

        elif item in (self.item_cylinder, self.item_pipeline, self.item_custom):
            if all(item.checkState() == Qt.Unchecked for item in (self.item_cylinder, self.item_pipeline, self.item_custom)):
                self.item_geom.setCheckState(Qt.Unchecked)
                self.item_geom.setCheckState(Qt.Unchecked)
                self.item_cylinder.setFlags(Qt.ItemFlags(int("110001", 2)))
                self.item_pipeline.setFlags(Qt.ItemFlags(int("110001", 2)))
                self.item_custom.setFlags(Qt.ItemFlags(int("110001", 2)))
            elif self.item_cylinder.checkState() == Qt.Checked:
                self.item_geom.setCheckState(Qt.Checked)
                self.item_pipeline.setFlags(Qt.ItemFlags(int("000000", 2)))
                self.item_custom.setFlags(Qt.ItemFlags(int("000000", 2)))
            elif self.item_pipeline.checkState() == Qt.Checked:
                self.item_geom.setCheckState(Qt.Checked)
                self.item_cylinder.setFlags(Qt.ItemFlags(int("000000", 2)))
                self.item_custom.setFlags(Qt.ItemFlags(int("000000", 2)))
            elif self.item_custom.checkState() == Qt.Checked:
                self.item_geom.setCheckState(Qt.Checked)
                self.item_cylinder.setFlags(Qt.ItemFlags(int("000000", 2)))
                self.item_pipeline.setFlags(Qt.ItemFlags(int("000000", 2)))

    # =======================================================================


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Project_process_QTV()
    window.show()
    sys.exit(app.exec())
