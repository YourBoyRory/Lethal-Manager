import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config

class DragDropWindow(QMainWindow):
    
    config = Config()
    #BepinexUpdater(config.config)
    modhandler = ModHandler(config.config)
    selected_item = None
    
    def __init__(self):
        super().__init__()

        # Set up the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Drag and Drop
        self.label = QLabel("Drag and drop files here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAcceptDrops(True)  # Enable drag and drop
        self.layout.addWidget(self.label)
        self.setAcceptDrops(True)
        
        # 
        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.clicked)
        self.layout.addWidget(self.listwidget)
        
        
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

    def setupWindow(self):
        self.setWindowTitle("Lethal Manager v2 Alpha")
        #self.resize(325, 400)
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
        
        # Display file paths in the label
        self.label.setText("\n".join(file_paths))
        for package in file_paths:
            self.install_mod(package)
        
    def clicked(self, qmodelindex):
        item = self.listwidget.currentItem()
        self.selected_item = item.text()
            
    def refresh_list(self):
        self.listwidget.clear()
        for mod in self.modhandler.mod_list:
            self.listwidget.addItem(mod)
        
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
        
    def disable_mod(self):
        if self.selected_item is not None:
            self.modhandler.disable(self.selected_item)
            self.refresh_list()
    
    def enable_mod(self):
        if self.selected_item is not None:
            self.modhandler.enable(self.selected_item)
            self.refresh_list()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
