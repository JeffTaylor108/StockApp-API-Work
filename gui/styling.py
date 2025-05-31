from PyQt6.QtGui import QFont

heading_font = QFont()
heading_font.setPointSize(10)
heading_font.setBold(True)

transparent_button_style = """
    QPushButton {
        background-color: transparent;
        border: none;
        padding: 0;
    }
    QPushButton:hover {
        background-color: transparent;
    }
    QPushButton:pressed {
        background-color: transparent;
    }
"""