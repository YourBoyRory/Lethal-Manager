import sys
import PyQt5
from PyQt5.QtWidgets import QWidget, QListWidget, QMainWindow, QApplication, QGridLayout, QLabel, QSpacerItem, QSizePolicy, QMenu, QListWidgetItem, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config
import os.path

class DragDropWindow(QMainWindow):

    config = Config()
    #BepinexUpdater(config.config)
    modhandler = ModHandler(config.config)
    selected_item = None

    def __init__(self):

        super().__init__()

        # Set up the main widget and layout
        self.central_widget = QWidget()
        style ="""
            QLabel {
                font: 14pt
            }
            QListWidget {
                font: 14pt
            }
        """
        self.setStyleSheet(style)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        #Lable
        self.display_mod_icon = self.make_label("display_mod_icon", Qt.AlignLeft, 0)
        self.layout.addWidget(self.display_mod_icon,1,1,4,1, Qt.AlignRight)
        self.display_mod_icon.setContentsMargins(0, 0, 25, 25)
        self.display_mod_name=self.make_label("display_mod_name", Qt.AlignLeft, 0)
        self.layout.addWidget(self.display_mod_name,1,2)
        self.display_mod_version=self.make_label("display_mod_version", Qt.AlignLeft, 0)
        self.layout.addWidget(self.display_mod_version,2,2)
        self.display_mod_status=self.make_label("display_mod_status", Qt.AlignLeft, 0)
        self.layout.addWidget(self.display_mod_status,3,2)
        self.display_mod_website=self.make_label("display_mod_website", Qt.AlignLeft, 0)
        self.display_mod_website.setStyleSheet("color: lightblue")
        self.layout.addWidget(self.display_mod_website,4,2)
        self.display_mod_description=self.make_label("display_mod_description", Qt.AlignCenter, 600)
        self.layout.addWidget(self.display_mod_description,5,1,1,2)
        self.dependencies_lable=self.make_label("Dependencies:", Qt.AlignLeft, 0)
        self.dependencies_lable.setContentsMargins(0, 50, 0, 0)
        self.layout.addWidget(self.dependencies_lable,6,1,1,2)
        self.display_mod_dependencies=self.make_label("display_mod_dependencies", Qt.AlignLeft, 0)
        self.display_mod_dependencies.setStyleSheet("font: 12pt; color: gray")
        self.layout.addWidget(self.display_mod_dependencies,7,1,1,2)

        verticalSpacer = QSpacerItem(100, 100,  QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer, 8,1,1,2)

        # Mod List
        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.clicked)
        self.listwidget.setMaximumWidth(500)
        self.listwidget.setMinimumWidth(200)
        self.listwidget.setMinimumHeight(400)
        self.layout.addWidget(self.listwidget,1,0,9,1)


       # Context menu
        self.context_menu = QMenu(self)
        uninstall_menuaction = self.context_menu.addAction("Uninstall")
        enable_menuaction = self.context_menu.addAction("Enable")
        disable_menuaction = self.context_menu.addAction("Disable")
        uninstall_menuaction.triggered.connect(self.uninstall_mod)
        enable_menuaction.triggered.connect(self.enable_mod)
        disable_menuaction.triggered.connect(self.disable_mod)

        #display window
        self.refresh_list()
        self.setupWindow()

    def make_label(self, text, alignment, width):
        label = QLabel(text)
        label.setAlignment(alignment)
        #label.setContentsMargins(50, 50, 50, 50)
        label.setMinimumWidth(width)
        label.setWordWrap(True)
        label.setVisible(False)
        return label

    def setupWindow(self):
        self.setWindowTitle("Lethal Manager v2 Alpha")
        self.setAcceptDrops(True)
        self.resize(900, 600)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.show()

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Accept the drag if it contains files
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Get the dropped files
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls]
        for package in file_paths:
            self.install_mod(package)

    def clicked(self, qmodelindex):
        item = self.listwidget.currentItem()
        self.selected_item = item.text()
        if self.selected_item is not None:
            self.refresh_mod_data()

    def refresh_list(self):
        self.listwidget.clear()
        for mod in self.modhandler.mod_list:
            icon = QIcon(os.path.join(self.config.config["lmdata_directory"], mod, "icon.png"))
            self.listwidget.addItem(QListWidgetItem(icon, mod))

    def refresh_mod_data(self):
        if self.selected_item is not None:
            modname = self.selected_item
            dependency_list = ""
            self.display_mod_icon.setVisible(True)
            self.display_mod_name.setText(self.modhandler.mod_list[modname]["name"])
            self.display_mod_name.setVisible(True)
            self.display_mod_version.setText("v" + self.modhandler.mod_list[modname]["version_number"])
            self.display_mod_version.setVisible(True)
            if  self.modhandler.is_enabled(modname):
                self.display_mod_status.setText("Enabled")
                self.display_mod_status.setStyleSheet("color: green")
            else:
                self.display_mod_status.setText("Disabled")
                self.display_mod_status.setStyleSheet("color: red")
            self.display_mod_status.setVisible(True)
            self.display_mod_website.setText(self.modhandler.mod_list[modname]["website_url"])
            self.display_mod_website.setVisible(True)
            self.display_mod_description.setText(self.modhandler.mod_list[modname]["description"])
            self.display_mod_description.setVisible(True)
            self.dependencies_lable.setVisible(True)
            self.display_mod_dependencies.setVisible(True)
            for dependency in self.modhandler.mod_list[modname]["dependencies"]:
                dependency_list += (dependency + "\n")
            self.display_mod_dependencies.setText(dependency_list)

            icon = QPixmap(os.path.join(self.config.config["lmdata_directory"], modname, "icon.png"))
            icon.scaled(10, 10)
            self.display_mod_icon.setPixmap(icon)
            self.display_mod_icon.resize(icon.width(), icon.height())
            self.display_mod_icon.setVisible(True)
        else:
            self.display_mod_icon.setVisible(False)
            self.display_mod_name.setVisible(False)
            self.display_mod_version.setVisible(False)
            self.display_mod_status.setVisible(False)
            self.display_mod_website.setVisible(False)
            self.display_mod_description.setVisible(False)
            self.dependencies_lable.setVisible(False)
            self.display_mod_dependencies.setVisible(False)
            self.display_mod_icon.setVisible(False)

    def install_mod(self, package):
        modname = self.modhandler.install(package)
        x,y = self.modhandler.get_needed_dependencies(modname)
        if x:
            print(f"[INFO] Dependencies Needed for {modname}.")
        if y:
            print(f"[INFO] Dependencies for {modname} are Disbaled.")
        self.refresh_list()

    def uninstall_mod(self):
        if self.selected_item is not None:
            self.modhandler.uninstall(self.selected_item)
            self.refresh_list()
            self.selected_item = None
            self.refresh_mod_data()

    def disable_mod(self):
        if self.selected_item is not None:
            self.modhandler.disable(self.selected_item)
            self.refresh_list()
            self.refresh_mod_data()

    def enable_mod(self):
        if self.selected_item is not None:
            self.modhandler.enable(self.selected_item)
            self.refresh_list()
            self.refresh_mod_data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
