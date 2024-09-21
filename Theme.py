
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
            font-size: 10pt;
        }
        QMenu {
            background-color: #303030;
            font-size: 10pt;
        }
        QMenu::item:disabled {
            color: gray
        }
        QMenu:selected {
            background-color: #242424;
        }
        QListView {
            background-color: #303030;
        }
    """
