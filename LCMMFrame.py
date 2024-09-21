import sys
import PyQt5
from PyQt5.QtWidgets import QWidget, QListWidget, QMainWindow, QApplication, QGridLayout, QLabel, QSpacerItem
from PyQt5.QtWidgets import QSizePolicy, QMenu, QListWidgetItem, QDesktopWidget, QMessageBox, QPushButton, QMenuBar
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config
from Theme import Theme
from pathlib import Path
import platform
import subprocess
import os.path
import traceback
import webbrowser

class DragDropWindow(QMainWindow):

    config = Config()
    ver_str = "v2.0.0 - Beta"
    modhandler = ModHandler(config.config)
    bepinUpdater = BepinexUpdater(config.config)
    styleSheets = Theme()
    cache_selection = None

    def __init__(self):

        super().__init__()
        # Set up the main widget and layout
        self.central_widget = QWidget()
        style = self.styleSheets.force_dark_mode
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        #Lable
        self.display_mod_icon = self.make_label("display_mod_icon", Qt.AlignTop, 0)
        #self.display_mod_icon.setFixedWidth(300)
        self.display_mod_icon.setFixedHeight(325)
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
        self.listwidget.setSelectionMode(3)
        self.listwidget.setMouseTracking(True)
        self.listwidget.setIconSize(QSize(50, 50))
        self.listwidget.setMaximumWidth(500)
        self.listwidget.setMinimumWidth(300)
        self.listwidget.setMinimumHeight(550)
        self.listwidget.setStyleSheet(style)
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
        self.install_menubar_action.triggered.connect(self.install_from_file)
        self.uninstall_menubar_action.triggered.connect(self.uninstall_mod)
        self.uninstall_menubar_action.setEnabled(False)
        self.toggle_menubar_action.triggered.connect(self.toggle_mod_status)
        self.toggle_menubar_action.setEnabled(False)
        self.refresh_menubar_action.triggered.connect(self.full_refresh)

        self.options_menu = self.menu_bar.addMenu("Options")
        self.update_menubar_action = QAction("Update BepInEx", self)
        self.opendir_menubar_action = QAction("Open Game Directroy", self)
        self.setdir_menubar_action = QAction("Set Game Directory", self)
        self.darkmode_menubar_action = QAction("Toggle Darkmode", self)
        self.options_menu.addAction(self.update_menubar_action)
        self.options_menu.addAction(self.opendir_menubar_action)
        self.options_menu.addAction(self.setdir_menubar_action)
        self.update_menubar_action.triggered.connect(self.update_bepinex)
        self.update_menubar_action.setEnabled(False)
        self.opendir_menubar_action.triggered.connect(self.open_game_folder)
        self.opendir_menubar_action.setEnabled(False)
        self.setdir_menubar_action.triggered.connect(self.set_game_directory)
        self.darkmode_menubar_action.triggered.connect(self.toggle_darkmode)
        if platform.system() == "Windows":
            self.options_menu.addAction(self.darkmode_menubar_action)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.downloadmods_menubar_action = QAction("Download Mods", self)
        self.troubleshoot_menubar_action = QAction("Troubleshooting", self)
        self.about_menubar_action = QAction("About", self)
        self.help_menu.addAction(self.downloadmods_menubar_action)
        self.help_menu.addAction(self.troubleshoot_menubar_action)
        self.help_menu.addAction(self.about_menubar_action)
        self.downloadmods_menubar_action.triggered.connect(self.openBrowser)
        self.troubleshoot_menubar_action.triggered.connect(self.showHelp)
        self.about_menubar_action.triggered.connect(self.showAbout)

        #display window
        self.setupWindow()
        self.setTheme()

        # Post window set up
        self.verify_files()
        self.refresh_list()

    def install_from_file(self):
        fileName, dump = QFileDialog.getOpenFileNames(self, "Install Thunderstore Package", os.path.join(Path.home(), 'Downloads') , "Thunderstore Package (*.zip);; All Files (*)")
        if fileName:
            print(fileName)
            self.install_mod(fileName)

    def setTheme(self):
        if platform.system() == "Windows":
            if self.config.config["darkmode"] == "False":
                print("[INFO] Darkmode is off")
                self.setStyleSheet(self.styleSheets.simple_style_sheet)
                self.menu_bar.setStyleSheet(self.styleSheets.simple_style_sheet)
                self.context_menu.setStyleSheet(self.styleSheets.simple_style_sheet)
                self.listwidget.setStyleSheet(self.styleSheets.simple_style_sheet)
            else:
                print("[INFO] Darkmode is on")
                self.setStyleSheet(self.styleSheets.force_dark_mode)
                self.listwidget.setStyleSheet(self.styleSheets.force_dark_mode_list)
                self.context_menu.setStyleSheet(self.styleSheets.force_dark_mode_list)
                self.menu_bar.setStyleSheet(self.styleSheets.force_dark_mode_list)
        else:
            # Other platforms will provide theme
            self.setStyleSheet(self.styleSheets.simple_style_sheet)
            self.listwidget.setStyleSheet(self.styleSheets.simple_style_sheet)

    def toggle_darkmode(self):
        if self.config.config["darkmode"] == "True":
            print("[INFO] Darkmode is off")
            self.setStyleSheet(self.styleSheets.simple_style_sheet)
            self.menu_bar.setStyleSheet(self.styleSheets.simple_style_sheet)
            self.context_menu.setStyleSheet(self.styleSheets.simple_style_sheet)
            self.listwidget.setStyleSheet(self.styleSheets.simple_style_sheet)
            self.config.config["darkmode"] = "False"
        else:
            print("[INFO] Darkmode is on")
            self.setStyleSheet(self.styleSheets.force_dark_mode)
            self.listwidget.setStyleSheet(self.styleSheets.force_dark_mode_list)
            self.context_menu.setStyleSheet(self.styleSheets.force_dark_mode_list)
            self.menu_bar.setStyleSheet(self.styleSheets.force_dark_mode_list)
            self.config.config["darkmode"] = "True"
        self.config.save_config()
        self.update()

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

    def showAbout(self):
        msg = self.make_popup_window(None, "About Lethal Manager",
        f"Lethal Manager {self.ver_str}\nYourBoyRory\nhttps://github.com/YourBoyRory/Lethal-Manager",
        f"BepInEx Version: {self.bepinUpdater.bepinex_version}\nMods Installed: {len(self.modhandler.mod_list)}\n\n\nSpecial Thanks!\nHemoglobin - Windows Beta Tester\nAntonio - Windows Beta Tester\nDRBatt - Linux Beta Tester")
        msg.exec()

    def showHelp(self):
        msg = self.make_popup_window(None, "Troubleshooting",
        "If your mods are not loading make sure the program is pointing that the game's install directory.\n\nIf you have confirmed the games install directory make sure BepInEx is up to date by installing in through \n[Options] > [Update BepInEx] \n\nIf you are on a unix based platform (Mac or Linux)\nyou will need to add the following line to your games launch options:",
        "WINEDLLOVERRIDES=\"winhttp.dll=n,b\" %command%")
        msg.exec()

    def openBrowser(self):
        webbrowser.open('https://thunderstore.io/c/lethal-company/')

    def setupWindow(self):
        self.setWindowTitle(f"Lethal Manager")
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
        self.install_mod(file_paths)

    def list_clicked(self, qmodelindex):
        if self.listwidget.currentItem().text() is not None:
            print(f"[Info] Showing {self.listwidget.currentItem().text()} mod data")
            self.refresh_mod_data()

    def set_game_directory(self):
        selected_folder = QFileDialog.getExistingDirectory(self, 'Select Game Folder', self.config.config["game_directory"], QFileDialog.ShowDirsOnly)
        if selected_folder:
            self.config.set_game_directory(selected_folder)
            print(selected_folder)
            self.config.save_config()
            self.full_refresh()

    def open_game_folder(self):
        path = self.config.config["game_directory"]
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

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

    def full_refresh(self):
        self.cache_selection=None
        self.verify_files()
        self.refresh_list()
        self.refresh_mod_data()

    def toggle_mod_status(self):
        if self.selected_mod_enabled:
            self.disable_mod()
        else:
            self.enable_mod()

    def refresh_list(self):
        self.listwidget.clear()
        if self.filesVerified:
            for mod in self.modhandler.mod_list:
                icon = QIcon(os.path.join(self.config.config["lmdata_directory"], mod, "icon.png"))
                self.listwidget.addItem(QListWidgetItem(icon, mod))
                if not self.modhandler.is_enabled(mod):
                    self.listwidget.findItems(mod, Qt.MatchExactly)[0].setForeground(Qt.darkGray)

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
                    if dependency_count == 4:
                        dependency_list += (dependency)
                    elif dependency_count == 5:
                        dependency_count=len(self.modhandler.mod_list[modname]["dependencies"])-(dependency_count+1)
                        self.show_all_dependencies.setText(f"Show {dependency_count} more...\n")
                        self.show_all_dependencies.setVisible(True)
                        break
                    else:
                        dependency_list += (dependency + "\n")
            if dependency_count == 4:
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

    def install_mod(self, file_paths):
        installed = [0]
        updates_occured = False
        updated = ""
        fails_occured = False
        failed = ""
        for package in file_paths:
            modname, old_version = self.modhandler.install(package)
            if modname == None:
                failed += f"\n        {os.path.basename(package)}"
                fails_occured = True
            elif old_version:
                    if old_version == self.modhandler.mod_list[modname]["version_number"]:
                        updated += f"        {modname}: {self.modhandler.mod_list[modname]["version_number"]} Reinstalled\n"
                    else:
                        updated += f"        {modname}: {old_version} -> {self.modhandler.mod_list[modname]["version_number"]}\n"
                    updates_occured = True
            else:
                temp = [modname]
                installed += temp
        if fails_occured:
                msg = self.make_popup_window(QMessageBox.Critical, f"Failed to install mods", f"The following packages failed to install!{failed}", "The package manifest may be missing or malformed.")
                msg.exec()
        if updates_occured:
                msg = self.make_popup_window(QMessageBox.Information, "Mods Updated", f"The following mods have been updated or reinstalled:", f"{updated}")
                msg.exec()
        for package in installed:
            print(installed)
            if package != 0:
                self.check_for_dependencies(package)

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
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies missing for {modname}", f"The following mods need installed for {modname}:{display_missing}",f"The following mods need enabled:{display_disabled}")
            msg.exec()
        elif missing_list:
            print(f"[INFO] Dependencies Needed for {modname}.")
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies missing for {modname}", f"The following mods need installed for {modname}:{display_missing}","")
            msg.exec()
        elif disabled_list:
            msg = self.make_popup_window(QMessageBox.Warning, f"Dependencies disabled for {modname}", f"The following mods need enabled for{modname}:{display_disabled}", "")
            msg.exec()
        else:
            print(f"[INFO] No dependencies needed for {modname}.")
        #self.refresh_list() # why is this needed?

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

    def verify_files(self):
        self.filesVerified = True
        game_found, loader_found = self.config.verify_files()
        self.update_menubar_action.setEnabled(True)
        self.opendir_menubar_action.setEnabled(True)
        if not game_found:
            self.filesVerified = False
            self.opendir_menubar_action.setEnabled(False)
            self.update_menubar_action.setEnabled(False)
            msg = self.make_popup_window(QMessageBox.Warning, "Lethal Company Not Found", "We where unabled to locate the games directory automatically. Please provide the path to your lethal company folder", "")
            msg.addButton(QPushButton('Set Directory'), QMessageBox.YesRole)
            msg.addButton(QPushButton('Later'), QMessageBox.NoRole)
            selection = msg.exec()
            if selection == 0:
                self.set_game_directory()
        elif not loader_found:
            self.filesVerified = False
            self.update_menubar_action.setText("Install BepInEx")
            msg = self.make_popup_window(QMessageBox.Warning, "BepInEx Not Found", "BepInEx does not appear to be installed. This is the mod loader for Lethal compant and will need to be installed to run mods", "Install BepInEx now?")
            msg.addButton(QPushButton('Install'), QMessageBox.YesRole)
            msg.addButton(QPushButton('Later'), QMessageBox.NoRole)
            selection = msg.exec()
            if selection == 0:
                self.update_bepinex()

    def update_bepinex(self):
        if not self.config.config["gameFound"]:
            msg = self.make_popup_window(QMessageBox.Warning, "Lethal Company Not Found", "We where unabled to locate the games directory automatically.", "Are you sure you want to attempt to install BepInEx here?")
            msg.addButton(QPushButton('Yes'), QMessageBox.YesRole)
            msg.addButton(QPushButton('No'), QMessageBox.NoRole)
            selection = msg.exec()
            if selection is not QMessageBox.YesRole:
                return
        self.bepinUpdater.preformUpdate(self)
        self.verify_files()
        if self.bepinUpdater.bepinex_version != "Not Installed":
            self.update_menubar_action.setText("Update BepInEx")

    def uninstall_mod(self):
        if self.dependency_issue():
            return
        for item in self.listwidget.selectedItems():
            self.modhandler.uninstall(item.text())
        self.refresh_list()
        self.refresh_mod_data()

    def disable_mod(self):
        if self.dependency_issue():
            return
        for item in self.listwidget.selectedItems():
            self.cache_selection=self.listwidget.currentRow()
            self.modhandler.disable(item.text())
        self.partial_refresh()

    def enable_mod(self):
        enabled = [0]
        for item in self.listwidget.selectedItems():
            self.cache_selection=self.listwidget.currentRow()
            self.modhandler.enable(item.text())
            temp = [item.text()]
            enabled += temp
        self.partial_refresh()
        for package in enabled:
            print(enabled)
            if package != 0:
                self.check_for_dependencies(package)

    def dependency_issue(self):
        dependency_issue = False
        dependency_issue_list = ""
        for item in self.listwidget.selectedItems():
            for mod in self.listwidget.findItems('*', Qt.MatchWildcard):
                if self.modhandler.is_enabled(mod.text()) and mod not in self.listwidget.selectedItems() and self.modhandler.check_if_dependent(item.text(), mod.text()):
                    dependency_issue = True
                    dependency_issue_list += f"\n        {mod.text()} depends on {item.text()}"
        if dependency_issue:
            print(f"[INFO] Disbaling selected mods breaks these mods:{dependency_issue_list}")
            msg = self.make_popup_window(QMessageBox.Warning, f"Confirm Dependency Issue", f"The the operation will break dependency for the following mods:{dependency_issue_list}","Would you like to ignore these issues?")
            msg.addButton(QPushButton('Ignore'), QMessageBox.YesRole)
            msg.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
            selection = msg.exec()
            if selection != 0:
                return True
        return False
                

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
