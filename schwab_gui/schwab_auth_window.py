import time

from PyQt6.QtCore import Qt, QTime, QTimer
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout

from gui import styling
from schwab_connections.schwab_acccount_data import check_if_authorized
from schwab_connections.schwab_auth import authorize, get_auth_url, get_refresh_expire_time
from schwab_gui.schwab_window import MainSchwabWindow


class SchwabAuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Authorization for API Trading GUI")

        # widgets to be added to layout

        # auth link to click
        note_label = QLabel("<i>Note: auth is only needed if 1st time log on, or refresh token is expired</i>")
        auth_label = QLabel("Authorize account before proceeding by clicking this link:")
        auth_url = get_auth_url()
        print(auth_url)
        auth_link = QLabel(f'<a href="{auth_url}">Click here to authorize</a>')
        auth_link.setOpenExternalLinks(True)
        auth_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        # input for broken url
        returned_link_label = QLabel("Enter the URL of where Schwab redirects you after authorizing (it will show a broken page)")
        self.returned_link_input = QLineEdit()
        submit_link = QPushButton("Complete Authorization")
        submit_link.clicked.connect(self.submit_authorize)

        # continue without auth button + button grouping
        continue_button = QPushButton("Continue Without Auth")
        continue_button.clicked.connect(self.continue_without_auth)
        button_grouping = QHBoxLayout()
        button_grouping.addWidget(submit_link)
        button_grouping.addWidget(continue_button)

        # refresh token countdown
        refresh_token_label = QLabel("<b>Time until refresh token expires: </b>")
        self.token_expire_countdown = QLabel("")

        # layout
        layout = QVBoxLayout()
        layout.addWidget(note_label)
        layout.addWidget(auth_label)
        layout.addWidget(auth_link)
        layout.addSpacing(30)
        layout.addWidget(returned_link_label)
        layout.addWidget(self.returned_link_input)
        layout.addLayout(button_grouping)
        layout.addWidget(refresh_token_label)
        layout.addWidget(self.token_expire_countdown)

        container = QWidget()
        container.setLayout(layout)

        # sets window to display container
        self.setCentralWidget(container)

        # styling
        auth_label.setFont(styling.heading_font)
        returned_link_label.setFont(styling.heading_font)

        # countdown timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_token_countdown)
        self.timer.start(1000)

    def submit_authorize(self):
        link = self.returned_link_input.text()
        authorized = authorize(link) # returns true if authorized

        if authorized:
            self.main_window = MainSchwabWindow()
            self.main_window.show()
            self.close()
        else:
            print("User not authorized")

    def continue_without_auth(self):
        authorized = check_if_authorized()
        if authorized:
            self.main_window = MainSchwabWindow()
            self.main_window.show()
            self.close()
        else:
            print("User not authorized")

    def refresh_token_countdown(self):
        expire_time = get_refresh_expire_time() # contains "No Token Found" if tokens.json is empty

        if expire_time == "No Token Found":
            self.token_expire_countdown.setText(expire_time)

        else:
            countdown_in_epoch = float(expire_time) - time.time()

            if countdown_in_epoch > 0:
                days = countdown_in_epoch // 86400
                seconds_left = countdown_in_epoch % 86400

                hours = seconds_left // 3600
                seconds_left = seconds_left % 3600

                minutes = seconds_left // 60
                seconds = seconds_left % 60

                countdown = f"{int(days)} days, {int(hours)} hours, {int(minutes)} min, {int(seconds)} sec"
                self.token_expire_countdown.setText(countdown)
            else:
                self.token_expire_countdown.setText("Token Expired")
