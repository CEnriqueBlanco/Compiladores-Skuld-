from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class FileExplorer(QTreeWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setHeaderHidden(True)
        self._build_tree()

    def _build_tree(self) -> None:
        icon_file = QIcon("../resources/icons/file.png")
        icon_folder = QIcon("../resources/icons/icon.png")

        root = QTreeWidgetItem(["examples"])
        root.setIcon(0, icon_folder)
        hello = QTreeWidgetItem(["hello_world.stn"])
        hello.setIcon(0, icon_file)
        root.addChild(hello)

        src = QTreeWidgetItem(["src"])
        src.setIcon(0, icon_folder)
        main_stn = QTreeWidgetItem(["main.stn"])
        main_stn.setIcon(0, icon_file)
        utils_stn = QTreeWidgetItem(["utils.stn"])
        utils_stn.setIcon(0, icon_file)
        src.addChild(main_stn)
        src.addChild(utils_stn)

        self.addTopLevelItem(root)
        self.addTopLevelItem(src)
        self.expandAll()
