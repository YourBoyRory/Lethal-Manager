import sys
import PyQt5
from PyQt5.QtWidgets import QWidget, QListWidget, QMainWindow, QApplication, QGridLayout, QLabel, QSpacerItem
from PyQt5.QtWidgets import QSizePolicy, QMenu, QListWidgetItem, QDesktopWidget, QMessageBox, QPushButton, QMenuBar
from PyQt5.QtWidgets import QMenuBar, QAction
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config
import os.path

class DragDropWindow(QMainWindow):

    config = Config()
    #BepinexUpdater(config.config)
    modhandler = ModHandler(config.config)
    cache_selection = None

    def __init__(self):

        super().__init__()

        # Set up the main widget and layout
        self.central_widget = QWidget()
        style = """
            QLabel {
                font: 14pt
            }
            QListWidget {
                font: 14pt
            }
            QPushButton {
                font-size: 14pt;
            }
            QPushButton:hover {
                color: darkgray;
            }
        """
        self.setStyleSheet(style)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        #Lable
        self.display_mod_icon = self.make_label("display_mod_icon", Qt.AlignTop, 0)
        #self.display_mod_icon.setFixedWidth(300)
        #self.display_mod_icon.setFixedHeight(350)
        self.layout.addWidget(self.display_mod_icon,1,1,5,1, Qt.AlignRight)
        self.display_mod_icon.setContentsMargins(25, 25, 25, 25)
        self.display_mod_name=self.make_label("display_mod_name", Qt.AlignLeft, 0)
        self.display_mod_name.setContentsMargins(0, 25, 0, 0)
        self.layout.addWidget(self.display_mod_name,1,2,1,3)
        self.display_mod_version=self.make_label("display_mod_version", Qt.AlignLeft, 0)
        self.layout.addWidget(self.display_mod_version,2,2,1,3)
        self.display_mod_website=self.make_label("display_mod_website", Qt.AlignLeft, 0)
        self.display_mod_website.setTextFormat(Qt.RichText);
        self.display_mod_website.setTextInteractionFlags(Qt.TextBrowserInteraction);
        self.display_mod_website.setOpenExternalLinks(True);
        self.layout.addWidget(self.display_mod_website,3,2,1,3)
        self.display_mod_status=self.make_button("display_mod_status", self.toggle_mod_status)
        self.layout.addWidget(self.display_mod_status,4,2, Qt.AlignLeft)
        self.display_mod_uninstall=self.make_button("Uninstall", self.uninstall_mod)
        self.layout.addWidget(self.display_mod_uninstall,4,3, Qt.AlignLeft)
        verticalSpacer = QSpacerItem(700, 0, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer,4,4,1,1)
        verticalSpacer = QSpacerItem(0, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer,5,2,1,3)
        self.display_mod_description=self.make_label("display_mod_description", Qt.AlignHCenter , 0)
        self.display_mod_description.setMinimumHeight(50)
        self.display_mod_description.setContentsMargins(25, 0, 25, 0)
        self.layout.addWidget(self.display_mod_description,6,1,1,4, Qt.AlignTop)
        verticalSpacer = QSpacerItem(700, 700, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer,7,1,1,4)
        self.dependencies_lable=self.make_label("Dependencies:", Qt.AlignLeft, 0)
        self.dependencies_lable.setContentsMargins(25, 50, 0, 0)
        self.layout.addWidget(self.dependencies_lable,8,1,1,4)
        self.display_mod_dependencies=self.make_label("display_mod_dependencies", Qt.AlignLeft, 0)
        self.display_mod_dependencies.setContentsMargins(25, 0, 0, 0)
        self.display_mod_dependencies.setStyleSheet("font: 12pt; color: gray")
        self.layout.addWidget(self.display_mod_dependencies,9,1,1,4)
        self.show_all_dependencies = self.make_button("show_all_dependencies", self.show_more_clicked)
        self.show_all_dependencies.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                padding-left: 25;
                font-size: 12pt;
            }
            QPushButton:hover {
                color: darkgray;
            }
        """)
        self.layout.addWidget(self.show_all_dependencies,10,1,1,2, Qt.AlignLeft)

        # Mod List
        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.list_clicked)
        self.listwidget.setMouseTracking(True)
        self.listwidget.setIconSize(QSize(50, 50))
        self.listwidget.setMaximumWidth(500)
        self.listwidget.setMinimumWidth(300)
        self.listwidget.setMinimumHeight(550)
        self.layout.addWidget(self.listwidget,1,0,11,1)

        # Context menu
        self.context_menu = QMenu(self)
        self.uninstall_menuaction = self.context_menu.addAction("Uninstall")
        self.uninstall_menuaction.setEnabled(False)
        self.toggle_menuaction = self.context_menu.addAction("Enable")
        self.toggle_menuaction.setEnabled(False)
        self.refresh_menuaction = self.context_menu.addAction("Refresh")
        self.uninstall_menuaction.triggered.connect(self.uninstall_mod)
        self.toggle_menuaction.triggered.connect(self.toggle_mod_status)
        self.refresh_menuaction.triggered.connect(self.partial_refresh)

        # Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("Edit")
        self.install_menubar_action = QAction("Install Mod", self)
        self.uninstall_menubar_action = QAction("Uninstall Mod", self)
        self.toggle_menubar_action = QAction("Enable Mod", self)
        self.refresh_menubar_action = QAction("Refresh List", self)
        self.file_menu.addAction(self.install_menubar_action)
        self.file_menu.addAction(self.uninstall_menubar_action)
        self.file_menu.addAction(self.toggle_menubar_action)
        self.file_menu.addAction(self.refresh_menubar_action)
        #self.install_menubar_action.triggered.connect(self.new_file)
        self.uninstall_menubar_action.triggered.connect(self.uninstall_mod)
        self.uninstall_menubar_action.setEnabled(False)
        self.toggle_menubar_action.triggered.connect(self.toggle_mod_status)
        self.toggle_menubar_action.setEnabled(False)
        self.refresh_menubar_action.triggered.connect(self.partial_refresh)

        self.options_menu = self.menu_bar.addMenu("Options")
        self.update_menubar_action = QAction("Update BepInEx", self)
        self.opendir_menubar_action = QAction("Open Game Directroy", self)
        self.setdir_menubar_action = QAction("Set Game Directory", self)
        self.options_menu.addAction(self.update_menubar_action)
        self.options_menu.addAction(self.opendir_menubar_action)
        self.options_menu.addAction(self.setdir_menubar_action)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.downloadmods_menubar_action = QAction("Download Mods", self)
        self.troubleshoot_menubar_action = QAction("Troubleshooting", self)
        self.about_menubar_action = QAction("About", self)
        self.help_menu.addAction(self.downloadmods_menubar_action)
        self.help_menu.addAction(self.troubleshoot_menubar_action)
        self.help_menu.addAction(self.about_menubar_action)

        #display window
        self.refresh_list()
        self.setupWindow()

    def make_button(self, title, action):
        button = QPushButton(title)
        button.setVisible(False)
        button.clicked.connect(action)
        button.setMinimumWidth(0)
        button.setMinimumHeight(0)
        return button

    def make_label(self, text, alignment, width):
        label = QLabel(text)
        label.setAlignment(alignment)
        #label.setContentsMargins(50, 50, 50, 50)
        label.setMinimumWidth(width)
        label.setWordWrap(True)
        label.setVisible(False)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return label

    def setupWindow(self):
        self.setWindowTitle("Lethal Manager v2 Alpha")
        self.setAcceptDrops(True)
        self.resize(1000, 700)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.show()

    def contextMenuEvent(self, event):
        if self.listwidget.underMouse():
            if self.listwidget.currentItem() is not None:
                self.refresh_mod_data()
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

    def list_clicked(self, qmodelindex):
        if self.listwidget.currentItem().text() is not None:
            self.refresh_mod_data()


    def show_more_clicked(self):
        dependency_list = ""
        if self.listwidget.currentItem().text() is not None:
            modname = self.listwidget.currentItem().text()
            for dependency in self.modhandler.mod_list[modname]["dependencies"]:
                curr_dependency = dependency[dependency.find('-')+1:dependency.rfind('-')]
                if curr_dependency != "BepInExPack":
                    dependency_list += (dependency + "\n")
            msg = self.make_popup_window(None, f"All Dependencies for {modname}", dependency_list, "")
            msg.setStyleSheet("""
                QLabel {
                    min-width:500 px;
                    font-size: 12pt;
                    color: gray;
                }
            """)
            msg.exec()

    def partial_refresh(self):
        self.cache_selection=self.listwidget.currentRow()
        self.refresh_list()
        self.refresh_mod_data()

    def toggle_mod_status(self):
        if self.selected_mod_enabled:
            self.disable_mod()
        else:
            self.enable_mod()

    def refresh_list(self):
        self.listwidget.clear()
        for mod in self.modhandler.mod_list:
            icon = QIcon(os.path.join(self.config.config["lmdata_directory"], mod, "icon.png"))
            self.listwidget.addItem(QListWidgetItem(icon, mod))

    def refresh_mod_data(self):

        if self.cache_selection is not None:
            self.listwidget.setCurrentRow(self.cache_selection)
            self.cache_selection = None

        if self.listwidget.currentItem() is not None:
            modname = self.listwidget.currentItem().text()

            dependency_list = ""
            dependency_count = 0
            self.uninstall_menuaction.setEnabled(True)
            self.toggle_menuaction.setEnabled(True)
            self.uninstall_menubar_action.setEnabled(True)
            self.toggle_menubar_action.setEnabled(True)


            self.display_mod_icon.setVisible(True)
            self.display_mod_name.setText(self.modhandler.mod_list[modname]["name"])
            self.display_mod_name.setVisible(True)
            self.display_mod_version.setText("v" + self.modhandler.mod_list[modname]["version_number"])
            self.display_mod_version.setVisible(True)
            if  self.modhandler.is_enabled(modname):
                self.display_mod_status.setText("Enabled")
                self.display_mod_status.setStyleSheet("color: green")
                self.selected_mod_enabled = True
                self.toggle_menuaction.setText("Disable")
                self.toggle_menubar_action.setText("Disable")
            else:
                self.display_mod_status.setText("Disabled")
                self.display_mod_status.setStyleSheet("color: red")
                self.selected_mod_enabled = False
                self.toggle_menuaction.setText("Enable")
                self.toggle_menubar_action.setText("Enable")
            self.display_mod_status.setVisible(True)
            self.display_mod_uninstall.setVisible(True)
            self.display_mod_website.setText(f"<a href=\"{self.modhandler.mod_list[modname]["website_url"]}\">{self.modhandler.mod_list[modname]["website_url"]}</a>")
            self.display_mod_website.setVisible(True)
            self.display_mod_description.setText(self.modhandler.mod_list[modname]["description"])
            self.display_mod_description.setVisible(True)
            self.dependencies_lable.setVisible(True)
            self.display_mod_dependencies.setVisible(True)
            self.show_all_dependencies.setVisible(False)
            for dependency in self.modhandler.mod_list[modname]["dependencies"]:
                curr_dependency = dependency[dependency.find('-')+1:dependency.rfind('-')]
                if curr_dependency != "BepInExPack":
                    dependency_count += 1
                    if dependency_count is 4:
                        dependency_list += (dependency)
                    elif dependency_count is 5:
                        dependency_count=len(self.modhandler.mod_list[modname]["dependencies"])-(dependency_count+1)
                        self.show_all_dependencies.setText(f"Show {dependency_count} more...\n")
                        self.show_all_dependencies.setVisible(True)
                        break
                    else:
                        dependency_list += (dependency + "\n")
            if dependency_count is 4:
                dependency_list += "\n"
            if dependency_list == "":
                dependency_list = "None\n"
            self.display_mod_dependencies.setText(dependency_list)

            icon = QPixmap(os.path.join(self.config.config["lmdata_directory"], modname, "icon.png"))
            icon.scaled(10, 10)
            self.display_mod_icon.setPixmap(icon)
            self.display_mod_icon.resize(icon.width(), icon.height())
            self.display_mod_icon.setVisible(True)
        else:
            self.uninstall_menuaction.setEnabled(False)
            self.toggle_menuaction.setEnabled(False)
            self.uninstall_menubar_action.setEnabled(False)
            self.toggle_menubar_action.setEnabled(False)

            self.display_mod_icon.setVisible(False)
            self.display_mod_name.setVisible(False)
            self.display_mod_version.setVisible(False)
            self.display_mod_status.setVisible(False)
            self.display_mod_uninstall.setVisible(False)
            self.display_mod_website.setVisible(False)
            self.display_mod_description.setVisible(False)
            self.dependencies_lable.setVisible(False)
            self.display_mod_dependencies.setVisible(False)
            self.show_all_dependencies.setVisible(False)
            self.display_mod_icon.setVisible(False)

    def install_mod(self, package):
        modname = self.modhandler.install(package)
        if modname == None:
            msg = self.make_popup_window(QMessageBox.Critical, f"Failed to install mod", "The provided package failed to install!","The mod manifest may be missing or malformed. Contact the mod creator and notify me on Github.\n\n https://github.com/YourBoyRory")
            msg.exec()
        else:
            self.check_for_dependencies(modname)

    def check_for_dependencies(self, modname):
        display_missing = ""
        display_disabled = ""
        missing_list,disabled_list = self.modhandler.get_needed_dependencies(modname)
        for name in missing_list:
            display_missing += "\n        " + name
        for name in disabled_list:
            display_disabled += "\n        " + name
        if missing_list and disabled_list:
            print(f"[INFO] Dependencies Needed for {modname}.")
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies missing for {modname}", f"The following mods need installed:{display_missing}",f"The following mods need enabled:{display_disabled}")
            msg.exec()
        elif missing_list:
            print(f"[INFO] Dependencies Needed for {modname}.")
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies missing for {modname}", f"The following mods need installed:{display_missing}","")
            msg.exec()
        elif disabled_list:
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies disabled for {modname}", f"The following mods need enabled:{display_disabled}", "")
            msg.exec()
        else:
            print(f"[INFO] No dependencies needed for {modname}.")
        self.refresh_list()

    def make_popup_window(self, mtype, title, top_text, bottom_text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        if mtype is not None:
            msg.setIcon(mtype)
        msg.setText(top_text)
        msg.setInformativeText(bottom_text)
        msg.setStyleSheet("""
            QLabel {
                min-width:500 px;
                font-size: 12pt;
            }
        """)
        return msg


    def uninstall_mod(self):
        if self.listwidget.currentItem() is not None:
            self.modhandler.uninstall(self.listwidget.currentItem().text())
            self.refresh_list()
            self.refresh_mod_data()

    def disable_mod(self):
        if self.listwidget.currentItem() is not None:
            self.cache_selection=self.listwidget.currentRow()
            self.modhandler.disable(self.listwidget.currentItem().text())
            self.partial_refresh()

    def enable_mod(self):
        if self.listwidget.currentItem() is not None:
            self.modhandler.enable(self.listwidget.currentItem().text())
            self.partial_refresh()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
