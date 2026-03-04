from pathlib import Path

from PyQt5.QtCore import QPoint, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QInputDialog, QMenu, QMessageBox, QTreeWidget, QTreeWidgetItem


class FileExplorer(QTreeWidget):
    file_open_requested = pyqtSignal(str)
    file_close_requested = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._root_paths: list[Path] = []
        self._open_files: list[Path] = []
        self._ignored_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            ".venv311",
            "venv",
            "venv312",
            "node_modules",
        }
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setExpandsOnDoubleClick(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_item_activated)
        self._build_tree()

    def _build_tree(self) -> None:
        self.clear()
        if not self._root_paths and not self._open_files:
            return

        icon_file = QIcon("../resources/icons/file.png")
        icon_folder = QIcon("../resources/icons/icon.png")

        for file_path in self._open_files:
            # No mostrar si ya está dentro de alguna carpeta abierta
            if any(file_path.is_relative_to(root) for root in self._root_paths):
                continue
            item = QTreeWidgetItem([file_path.name])
            item.setIcon(0, icon_file)
            item.setData(0, Qt.UserRole, "file")
            item.setData(0, Qt.UserRole + 1, str(file_path))
            item.setToolTip(0, str(file_path))
            self.addTopLevelItem(item)

        for root_path in self._root_paths:
            root_label = root_path.name if root_path.name else str(root_path)
            root_item = QTreeWidgetItem([root_label])
            root_item.setIcon(0, icon_folder)
            root_item.setData(0, Qt.UserRole, "folder")
            root_item.setData(0, Qt.UserRole + 1, str(root_path))
            root_item.setData(0, Qt.UserRole + 2, "root")
            root_item.setToolTip(0, str(root_path))

            for path in sorted(root_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                if self._should_skip(path):
                    continue
                item = self._create_item(path, icon_folder, icon_file)
                if item:
                    root_item.addChild(item)

            self.addTopLevelItem(root_item)

        self.expandAll()

    def refresh(self) -> None:
        self._build_tree()

    def set_root_path(self, folder_path: str) -> None:
        self._root_paths.clear()
        self.add_root_path(folder_path)

    def set_root_paths(self, folder_paths: list[str]) -> None:
        self._root_paths.clear()
        for folder_path in folder_paths:
            selected = Path(folder_path)
            if not selected.exists() or not selected.is_dir():
                continue
            resolved = selected.resolve()
            if resolved in self._root_paths:
                continue
            self._root_paths.append(resolved)
        self._build_tree()

    def add_root_path(self, folder_path: str) -> None:
        selected = Path(folder_path)
        if not selected.exists() or not selected.is_dir():
            return
        resolved = selected.resolve()
        if resolved in self._root_paths:
            return
        self._root_paths.append(resolved)
        self._build_tree()

    def clear_roots(self) -> None:
        self._root_paths.clear()
        self._build_tree()

    def add_open_file(self, file_path: str) -> None:
        path = Path(file_path).resolve()
        if path not in self._open_files:
            self._open_files.append(path)
        self._build_tree()

    def remove_open_file(self, file_path: str) -> None:
        path = Path(file_path).resolve()
        self._open_files = [f for f in self._open_files if f != path]
        self._build_tree()

    def get_root_paths(self) -> list[str]:
        return [str(path) for path in self._root_paths]

    def _should_skip(self, path: Path) -> bool:
        if path.is_dir():
            if path.name in self._ignored_dirs:
                return True
            if path.name.startswith(".") and path.name not in {".vscode"}:
                return True
            return False
        # Para archivos, solo mostrar .stn y .txt
        if path.suffix.lower() not in {".stn", ".txt"}:
            return True
        return False

    def _create_item(self, path: Path, icon_folder: QIcon, icon_file: QIcon) -> QTreeWidgetItem | None:
        if self._should_skip(path):
            return None

        item_type = "folder" if path.is_dir() else "file"
        item = QTreeWidgetItem([path.name])
        item.setIcon(0, icon_folder if item_type == "folder" else icon_file)
        item.setData(0, Qt.UserRole, item_type)
        item.setData(0, Qt.UserRole + 1, str(path))

        if path.is_dir():
            for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                child_item = self._create_item(child, icon_folder, icon_file)
                if child_item:
                    item.addChild(child_item)
            # No mostrar carpetas vacias (sin archivos .stn/.txt)
            if item.childCount() == 0:
                return None

        return item

    def _show_context_menu(self, position: QPoint) -> None:
        item = self.itemAt(position)
        if not item:
            return

        item_type = item.data(0, Qt.UserRole)
        if item_type not in {"folder", "file"}:
            return

        menu = QMenu(self)
        action_open_file = None
        action_close_file = None
        action_remove_root = None
        action_new_file = menu.addAction("Nuevo archivo")
        if item_type == "folder":
            action_open_target = menu.addAction("Abrir en el explorador")
            if item.data(0, Qt.UserRole + 2) == "root":
                action_remove_root = menu.addAction("Quitar carpeta del explorador")
        else:
            action_open_file = menu.addAction("Abrir archivo")
            action_close_file = menu.addAction("Cerrar")
            action_open_target = menu.addAction("Abrir carpeta contenedora")

        selected_action = menu.exec_(self.viewport().mapToGlobal(position))
        if selected_action == action_new_file:
            self._create_new_file_for_item(item)
            return

        if action_open_file and selected_action == action_open_file:
            item_path_raw = item.data(0, Qt.UserRole + 1)
            if item_path_raw:
                self.file_open_requested.emit(str(item_path_raw))
            return

        if action_close_file and selected_action == action_close_file:
            item_path_raw = item.data(0, Qt.UserRole + 1)
            if item_path_raw:
                self.file_close_requested.emit(str(item_path_raw))
            return

        if selected_action == action_open_target:
            self._open_folder_for_item(item)
            return

        if action_remove_root and selected_action == action_remove_root:
            item_path_raw = item.data(0, Qt.UserRole + 1)
            if item_path_raw:
                self._remove_root_path(str(item_path_raw))

    def _remove_root_path(self, folder_path: str) -> None:
        selected = Path(folder_path)
        if not selected.exists():
            self._root_paths = [path for path in self._root_paths if str(path) != folder_path]
            self._build_tree()
            return

        resolved = selected.resolve()
        self._root_paths = [path for path in self._root_paths if path != resolved]
        self._build_tree()

    def _open_folder_for_item(self, item: QTreeWidgetItem) -> None:
        item_path_raw = item.data(0, Qt.UserRole + 1)
        item_type = item.data(0, Qt.UserRole)
        if not item_path_raw:
            return

        item_path = Path(str(item_path_raw))
        folder_path = item_path if item_type == "folder" else item_path.parent
        if not folder_path.exists() or not folder_path.is_dir():
            QMessageBox.warning(
                self,
                "Carpeta no disponible",
                f"La carpeta no existe en el proyecto:\n{folder_path}",
            )
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def _create_new_file_for_item(self, item: QTreeWidgetItem) -> None:
        item_path_raw = item.data(0, Qt.UserRole + 1)
        item_type = item.data(0, Qt.UserRole)
        if not item_path_raw:
            return

        selected_path = Path(str(item_path_raw))
        target_dir = selected_path if item_type == "folder" else selected_path.parent
        if not target_dir.exists() or not target_dir.is_dir():
            QMessageBox.warning(
                self,
                "Carpeta no disponible",
                f"La carpeta no existe en el proyecto:\n{target_dir}",
            )
            return

        file_name, ok = QInputDialog.getText(self, "Nuevo archivo", "Nombre del archivo:")
        if not ok:
            return

        clean_name = file_name.strip()
        if not clean_name:
            QMessageBox.information(self, "Nuevo archivo", "Debes ingresar un nombre de archivo.")
            return

        if not Path(clean_name).suffix:
            clean_name = f"{clean_name}.stn"

        new_file_path = target_dir / clean_name
        if new_file_path.exists():
            QMessageBox.warning(
                self,
                "Nuevo archivo",
                f"Ya existe un archivo con ese nombre:\n{new_file_path.name}",
            )
            return

        try:
            new_file_path.write_text("", encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(
                self,
                "No se pudo crear",
                f"No fue posible crear el archivo:\n{new_file_path}\n\n{exc}",
            )
            return

        self.refresh()
        self.file_open_requested.emit(str(new_file_path))

    def _on_item_activated(self, item: QTreeWidgetItem, _column: int) -> None:
        item_type = item.data(0, Qt.UserRole)
        item_path_raw = item.data(0, Qt.UserRole + 1)
        if item_type == "file" and item_path_raw:
            self.file_open_requested.emit(str(item_path_raw))

