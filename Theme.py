
class Theme:
    simple_style_sheet="""
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

    force_dark_mode="""
        background-color: #393939;
        color: white;
        font: 14pt;
        font-size: 14pt;
        
        QLabel {
            font: 14pt;
        }
        QPushButton {
            font-size: 14pt;
        }
        QPushButton:hover {
            color: darkgray;
        }
    """
    force_dark_mode_list="""
        QMenuBar { 
            background-color: #303030;
            font-size: 12pt;
        }
        QMenu {
            background-color: #303030;
            font-size: 12pt;
        }
        QMenu:pressed {
            background-color: #000000;
            font-size: 12pt;
        }
        QListView {
            background-color: #303030;
        }
    """
