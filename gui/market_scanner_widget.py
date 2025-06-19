import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit, QPushButton
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue

from gui import styling
from ibapi_connections.market_scanner import req_scanner_params, req_scanner_subscription


class MarketScannerWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.filter_tags = []
        self.scan_code_dict = {}
        self.tag_category_dict = {}

        # widgets added to layout
        widget_label = QLabel("Market Scanner")

        self.scan_code_selector = QComboBox()
        self.tag_category_selector = QComboBox()

        self.tag_value_input = QLineEdit()
        add_tag_button = QPushButton("Add Tag to Scanner")
        add_tag_button.pressed.connect(self.add_tag)

        create_scanner_button = QPushButton("Create Market Scanner")
        create_scanner_button.pressed.connect(self.get_scanner_parameters)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(widget_label)
        layout.addWidget(self.scan_code_selector)
        layout.addWidget(self.tag_category_selector)
        layout.addWidget(self.tag_value_input)
        layout.addWidget(add_tag_button)
        layout.addWidget(create_scanner_button)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)

        self.find_valid_scan_codes()
        self.find_valid_tag_categories()

    # gets scanner parameters and sends subscription request to TWS
    def get_scanner_parameters(self):

        display_name = self.scan_code_selector.currentText()
        code = self.scan_code_dict[display_name]

        scanner = ScannerSubscription()
        scanner.instrument = "STK"
        scanner.locationCode = "STK.US.MAJOR"
        scanner.scanCode = code

        req_scanner_subscription(self.app, scanner, self.filter_tags)

    # adds new tag to scanner
    def add_tag(self):
        new_tag = TagValue(self.tag_category_selector.currentText(), self.tag_value_input.text())
        self.filter_tags.append(new_tag)

        print(f'Added tag to filters: {new_tag}')

    # fills scan_code_selector with valid codes and adds them to a dictionary matching display names to code names
    def find_valid_scan_codes(self):
        tree = ET.parse('ibapi_connections/scanner.xml')
        root = tree.getroot()

        for scan_type in root.findall(".//ScanTypeList/ScanType"):
            code = scan_type.find("scanCode")
            display_name = scan_type.find("displayName")
            if code is not None and code.text and display_name is not None and display_name.text:
                self.scan_code_dict[display_name.text.strip()] = code.text.strip()
                self.scan_code_selector.addItem(display_name.text.strip())
        print(self.scan_code_dict)

    # fills tag_category_selector with valid tags and adds them to dictionary matching display names to code names
    def find_valid_tag_categories(self):
        tree = ET.parse('ibapi_connections/scanner.xml')
        root = tree.getroot()

        for scan_type in root.findall(".//FilterList/RangeFilter/AbstractField"):
            code = scan_type.find("code")
            display_name = scan_type.find("displayName")
            if code is not None and code.text and display_name is not None and display_name.text:
                self.tag_category_dict[display_name.text.strip()] = code.text.strip()
                self.tag_category_selector.addItem(display_name.text.strip())
        print(self.tag_category_dict)