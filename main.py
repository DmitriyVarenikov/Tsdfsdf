import sys
import os
from enum import Enum, auto
from itertools import chain

from PySide6.QtWidgets import QWidget, QApplication, QTreeWidgetItem
from PySide6.QtGui import QIcon

from untitled import Ui_Form
from base_obj import BaseFile
from configuration import Config


# todo плохо листает вперед назад

class VisibleObj(Enum):
    FILE = auto()
    HIDE_FILE = auto()
    DIR = auto()
    HIDE_DIR = auto()


class CurrentDir:
    """Отвечает за определение текущей директории"""

    def __init__(self, max_buffer: int = 100):
        self._buffer = []
        self._max_buffer = max_buffer
        self._current_path = os.path.expanduser("~")
        self._buffer.append(self._current_path)
        self._current_index = 0

    def _check_buffer(self):
        if len(self._buffer) >= self._max_buffer:
            if self._current_index < self._max_buffer - 1:
                # self._buffer.pop(0)
                # self._buffer.pop(len(self._))
                pass
            elif self._current_index < self._max_buffer - 1:
                pass

    def get_dir(self) -> str:
        return self._current_path

    def set_dir(self, value):
        self._current_path = value
        self._buffer.append(value)
        self._current_index += 1
        self._check_buffer()

    def back_dir(self) -> str:
        print("start back: ", self._current_index, self._buffer)
        if self._current_index - 1 >= 0:
            self._current_index -= 1
            self._current_path = self._buffer[self._current_index]
        print("end back: ", self._current_index, self._buffer)
        return self._current_path

    def next_dir(self) -> str:
        print("start next: ", self._current_index, self._buffer)
        if self._current_index < len(self._buffer) - 1:
            self._current_index += 1
            self._current_path = self._buffer[self._current_index]
        print("end next: ", self._current_index, self._buffer)
        return self._current_path


class FileManager:
    def __init__(self):
        self._current_path = CurrentDir()
        self._struct_file = {VisibleObj.HIDE_DIR: [],
                             VisibleObj.DIR: [],
                             VisibleObj.HIDE_FILE: [],
                             VisibleObj.FILE: []
                             }
        self._test = {VisibleObj.HIDE_DIR: [],
                      VisibleObj.DIR: [],
                      VisibleObj.HIDE_FILE: [],
                      VisibleObj.FILE: []
                      }
        self.update_folder(self._current_path.get_dir())

    def next_dir(self) -> str:
        current_dir = self._current_path.next_dir()
        if current_dir is not None:
            self.update_folder(current_dir)
            return current_dir

    def back_dir(self) -> str:
        current_dir = self._current_path.back_dir()
        if current_dir is not None:
            self.update_folder(current_dir)
            return current_dir

    def clear_data(self):
        for lst in self._struct_file.values():
            lst.clear()

    def update_folder(self, current_path: str):
        self.clear_data()
        for name in os.listdir(current_path):
            path = current_path + os.sep + name
            obj = BaseFile(path, name)
            last_modified_time = os.path.getmtime(path)
            obj.set_last_edit(last_modified_time)
            if os.path.isdir(path):
                if '.' == name[0]:
                    self._struct_file.get(VisibleObj.HIDE_DIR).append(obj)
                else:
                    self._struct_file.get(VisibleObj.DIR).append(obj)
            elif os.path.isfile(path):
                obj.is_dir = False
                if '.' == name[0]:
                    self._struct_file.get(VisibleObj.HIDE_FILE).append(obj)
                else:
                    self._struct_file.get(VisibleObj.FILE).append(obj)

    def get_current_folder(self) -> str:
        return self._current_path.get_dir()

    def set_current_folder(self, value: str):
        self._current_path.set_dir(value)
        self.update_folder(self._current_path.get_dir())

    def get_all(self) -> list:
        return list(self._d.values())

    def get_hide_dir(self) -> list[str]:
        return self._struct_file.get(VisibleObj.HIDE_DIR)

    def get_dir(self) -> list[str]:
        return self._struct_file.get(VisibleObj.DIR)

    def get_hide_file(self) -> list[str]:
        return self._struct_file.get(VisibleObj.HIDE_FILE)

    def get_file(self) -> list[str]:
        return self._struct_file.get(VisibleObj.FILE)


class FolderManager(QWidget):
    def __init__(self):
        super().__init__()
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._icon_folder = QIcon(Config.DEFAULT_ICON_FOLDER)
        self._file_manager = FileManager()
        self._show_all()
        self._ui.btn_update.clicked.connect(self._update_folder)
        self._ui.btn_create_folder.clicked.connect(self._show_file)
        self._ui.treeWidget.itemDoubleClicked.connect(self._test)
        self._ui.btn_back.clicked.connect(self._back_dir)
        self._ui.btn_next.clicked.connect(self._next_dir)

    def _next_dir(self) -> None:
        """Следующая директория"""
        if self._file_manager.next_dir():
            self._show_all()

    def _back_dir(self) -> None:
        """Предыдущая директория"""
        if self._file_manager.back_dir():
            self._show_all()

    def _update_folder(self):
        self._file_manager.set_current_folder(self._file_manager.get_current_folder())
        self._show_all()

    def _test(self, obj: QTreeWidgetItem):
        name_obj = obj.text(0)
        new_current_folder = self._file_manager.get_current_folder() + os.sep + name_obj
        if os.path.isdir(new_current_folder):
            self._file_manager.set_current_folder(new_current_folder)
            self._show_all()

    def _show_file(self):
        for obj in chain(self._file_manager.get_hide_file(), self._file_manager.get_file()):
            item = QTreeWidgetItem(self._ui.treeWidget)
            item.setText(0, obj.name)
            item.setText(1, obj.last_edit)
            item.setText(2, obj.get_type_name())

    def _show_folder(self, flag=True):
        if flag:
            chain_folder = chain(self._file_manager.get_hide_dir(), self._file_manager.get_dir())
        else:
            chain_folder = self._file_manager.get_dir()
        for obj in chain_folder:
            item = QTreeWidgetItem(self._ui.treeWidget)
            item.setText(0, obj.name)
            item.setIcon(0, self._icon_folder)
            item.setText(1, obj.last_edit)
            item.setText(2, obj.get_type_name())

    def _show_all(self):
        self._ui.lineEdit.setText(self._file_manager.get_current_folder())
        self._ui.treeWidget.clear()
        self._show_folder()
        self._show_file()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderManager()
    window.show()
    sys.exit(app.exec())
