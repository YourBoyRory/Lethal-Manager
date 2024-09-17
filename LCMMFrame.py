import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config

class DragDropWindow(QMainWindow):
    
    config = Config()
    BepinexUpdater(config.config)
    modhandler = ModHandler(config.config)
    
    def __init__(self):
        super().__init__()
        
        self.setAcceptDrops(True)
        self.setWindowTitle("Lethal Manager v2 Alpha")
        self.setGeometry(300, 300, 400, 300)

        # Set up the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Set up the label
        self.label = QLabel("Drag and drop files here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAcceptDrops(True)  # Enable drag and drop
        self.layout.addWidget(self.label)

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
        
    def install_mod(self, package):
        modname = self.modhandler.install(package)
        x,y = self.modhandler.get_needed_dependencies(modname)
        if x:
            print(f"[INFO] Dependencies Needed for {modname}.")
        if y:
            print(f"[INFO] Dependencies for {modname} are Disbaled.")
    
    def uninstall_mod(self, modname):
        self.modhandler.uninstall(modname)
        
    def disable_mod(self, modname):
        self.modhandler.disable(modname)
    
    def enable_mod(self, modname):
        self.modhandler.enable(modname)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
