from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class FileExplorer(QTreeWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setHeaderHidden(True)
        self._build_tree()

    def _build_tree(self) -> None:
        root = QTreeWidgetItem(["examples"])
        hello = QTreeWidgetItem(["hello_world.stn"])
        root.addChild(hello)

        src = QTreeWidgetItem(["src"])
        src.addChild(QTreeWidgetItem(["main.stn"]))
        src.addChild(QTreeWidgetItem(["utils.stn"]))

        self.addTopLevelItem(root)
        self.addTopLevelItem(src)
        self.expandAll()
