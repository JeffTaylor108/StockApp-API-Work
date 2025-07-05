import time
import xml.etree.ElementTree as ET

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QGroupBox, QListWidget, \
    QListWidgetItem, QHBoxLayout, QTableWidget, QTabWidget, QTableWidgetItem
from PyQt6.QtGui import QColor, QBrush
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue

from gui import styling
from ibapi_connections.market_data import get_scanner_mkt_data, stop_mkt_data_stream
from ibapi_connections.market_scanner import req_scanner_subscription, req_saved_scanner_subscription, \
    cancel_subscription
from mongodb_connection.IBKR_market_scanners import mongo_fetch_scanners, mongo_remove_market_scanner, \
    mongo_fetch_scanner_name, mongo_fetch_scanner_tags, mongo_fetch_matching_scanner


class MarketScannerWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.filter_tags = []
        self.scan_code_dict = {}
        self.tag_category_dict = {}
        self.tag_code_to_display_name = {}
        self.symbol_to_row_maps = {} # stores row table mappings of symbol to row
        self.scanner_tables = {} # display name references QTableWidget
        self.current_table_req_id = None # keeps track of which table is selected for resource management

        # widgets added to layout
        widget_label = QLabel("Market Scanners")

        # current active scanners
        scanner_table_label = QLabel("Current Active Scanners")
        scanner_note = QLabel("Note: max 10 scanners active. Closing a tab deletes it.")
        self.scanner_tabs = QTabWidget()
        self.scanner_tabs.setTabsClosable(True)
        self.scanner_tabs.tabCloseRequested.connect(self.close_tab)
        self.scanner_tabs.currentChanged.connect(self.handle_tab_switch)

        # selects scanner code category
        scan_code_label = QLabel("1. Select Scanner Category")
        self.scan_code_selector = QComboBox()
        self.scan_code_selector.currentTextChanged.connect(self.change_preview_category)

        # selects filtering tag category
        tag_category_label = QLabel("2. Select Filter Tag")
        self.tag_category_selector = QComboBox()

        # selects filtering tag value
        tag_value_label = QLabel("3. Filter Tag Value")
        self.tag_value_input = QLineEdit()

        # adds tag to scanner object
        add_tag_button = QPushButton("Add Tag to Scanner")
        add_tag_button.pressed.connect(self.add_tag)

        # scanner details preview box
        self.scanner_preview = QGroupBox("Scanner Preview")
        scanner_preview_layout = QVBoxLayout()

        preview_code_category_label = QLabel("Scanner Category:")
        self.preview_code_category = QLabel("")
        scanner_preview_layout.addWidget(preview_code_category_label)
        scanner_preview_layout.addWidget(self.preview_code_category)

        preview_tags_label = QLabel("Current Filter Tags:")
        self.preview_tags_list = QListWidget()
        scanner_preview_layout.addWidget(preview_tags_label)
        scanner_preview_layout.addWidget(self.preview_tags_list)

        self.delete_tag_button = QPushButton("Clear Tags")
        self.delete_tag_button.pressed.connect(self.clear_tags)
        scanner_preview_layout.addWidget(self.delete_tag_button)

        self.scanner_preview.setLayout(scanner_preview_layout)

        create_scanner_button = QPushButton("Create Market Scanner")
        create_scanner_button.pressed.connect(self.create_scanner)
        self.app.active_scanners_updated.connect(self.update_scanner_table)
        self.app.scanner_price_updated.connect(self.update_scanner_table_prices)
        self.app.scanner_volume_updated.connect(self.update_scanner_table_volume)
        self.app.scanner_price_change_updated.connect(self.update_scanner_table_price_change)

        # layout
        layout = QVBoxLayout()
        create_scanner_layout = QVBoxLayout()
        horizontal_layout = QHBoxLayout()
        layout.addWidget(scanner_table_label)
        layout.addWidget(scanner_note)
        layout.addWidget(self.scanner_tabs)
        create_scanner_layout.addWidget(widget_label)
        create_scanner_layout.addWidget(scan_code_label)
        create_scanner_layout.addWidget(self.scan_code_selector)
        create_scanner_layout.addWidget(tag_category_label)
        create_scanner_layout.addWidget(self.tag_category_selector)
        create_scanner_layout.addWidget(tag_value_label)
        create_scanner_layout.addWidget(self.tag_value_input)
        create_scanner_layout.addWidget(add_tag_button)
        create_scanner_layout.addWidget(create_scanner_button)
        horizontal_layout.addLayout(create_scanner_layout)
        horizontal_layout.addWidget(self.scanner_preview)
        layout.addLayout(horizontal_layout)

        self.setLayout(layout)

        # fonts/styling
        widget_label.setFont(styling.heading_font)
        preview_code_category_label.setFont(styling.heading_font)
        preview_tags_label.setFont(styling.heading_font)
        scanner_note.setStyleSheet("color: gray;")

        self.find_valid_scan_codes()
        self.find_valid_tag_categories()

        self.initialize_saved_scanners()
        self.pause_tabs_not_in_focus()

    # gets scanner parameters and sends subscription request to TWS
    def create_scanner(self):

        display_name = self.scan_code_selector.currentText()
        code = self.scan_code_dict[display_name]

        scanner = ScannerSubscription()
        scanner.instrument = "STK"
        scanner.locationCode = "STK.US.MAJOR"
        scanner.scanCode = code

        print(f'Scanner code: {scanner.scanCode}')
        print(f'Filter Tags: {self.filter_tags}')

        req_scanner_subscription(self.app, scanner, self.filter_tags, display_name)

        # clears inputs/previews
        self.tag_value_input.clear()
        self.preview_tags_list.clear()

    # updates scanner tables with new scanner rankings
    def update_scanner_table(self, scan_data_obj, req_id):
        rank = scan_data_obj.rank
        symbol = scan_data_obj.contract.symbol
        get_scanner_mkt_data(self.app, scan_data_obj.contract, req_id)

        # creates reference to table and inserts into tab
        if req_id not in self.scanner_tables:
            scanner_table = QTableWidget()
            scanner_table.setColumnCount(4)
            scanner_table.setHorizontalHeaderLabels(["Symbol", "Last Price", "Volume", "Change"])
            scanner_table.setRowCount(50)

            self.symbol_to_row_maps[req_id] = {}
            self.scanner_tables[req_id] = scanner_table

            scanner_name = mongo_fetch_scanner_name(self.app.client, req_id)
            scanner_tags = mongo_fetch_scanner_tags(self.app.client, req_id)

            # scanner info box
            scanner_info_box = QGroupBox("Scanner Info")
            tags_label = QLabel("Active Filters:")
            tags_list = QListWidget()
            for tag in scanner_tags:
                tag_name = self.tag_code_to_display_name[tag["tag"]]
                tag_value = tag["value"]
                tags_list.addItem(QListWidgetItem(f"{tag_name}: {tag_value}"))

            scanner_info_layout = QVBoxLayout()
            scanner_info_layout.addWidget(tags_label)
            scanner_info_layout.addWidget(tags_list)

            scanner_info_box.setLayout(scanner_info_layout)

            # scanner table + info container
            tab_container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(scanner_table, stretch=3)
            layout.addWidget(scanner_info_box, stretch=1)
            tab_container.setLayout(layout)

            index = self.scanner_tabs.addTab(tab_container, f"{scanner_name}")
            self.scanner_tabs.tabBar().setTabData(index, req_id)

        table = self.scanner_tables.get(req_id)
        symbol_to_row = self.symbol_to_row_maps.get(req_id)

        symbol_to_row[symbol] = int(rank)
        table.setItem(int(rank), 0, QTableWidgetItem(symbol))
        table.setItem(int(rank), 1, QTableWidgetItem('--'))
        table.setItem(int(rank), 2, QTableWidgetItem('--'))
        table.setItem(int(rank), 3, QTableWidgetItem('--'))
        print(f'Rank: {rank}, Symbol: {symbol}')

    # updates prices in scanner table
    def update_scanner_table_prices(self, symbol, price, scanner_req_id):
        table = self.scanner_tables.get(scanner_req_id)
        symbol_to_row = self.symbol_to_row_maps.get(scanner_req_id)

        if symbol in symbol_to_row:
            row = symbol_to_row[symbol]
            table.setItem(row, 1, QTableWidgetItem(f"{price:.2f}"))

    # updates volume in scanner table
    def update_scanner_table_volume(self, symbol, volume, scanner_req_id):
        table = self.scanner_tables.get(scanner_req_id)
        symbol_to_row = self.symbol_to_row_maps.get(scanner_req_id)

        if symbol in symbol_to_row:
            row = symbol_to_row[symbol]
            table.setItem(row, 2, QTableWidgetItem(f"{volume}"))

    # updates price change in scanner table
    def update_scanner_table_price_change(self, symbol, price_change_dict, scanner_req_id):
        table = self.scanner_tables.get(scanner_req_id)
        symbol_to_row = self.symbol_to_row_maps.get(scanner_req_id)

        if symbol in symbol_to_row:
            row = symbol_to_row[symbol]
            last_price = price_change_dict["last_price"]
            open_price = price_change_dict["open_price"]
            price_change = last_price - open_price

            table_item = QTableWidgetItem(f"{price_change:.2f}")
            if price_change > 0:
                table_item.setBackground(QBrush(QColor("lightgreen")))
            else:
                table_item.setBackground(QBrush(QColor("#f88")))

            table.setItem(row, 3, table_item)


    # adds new tag to scanner
    def add_tag(self):
        display_name = self.tag_category_selector.currentText()
        new_tag = TagValue(self.tag_category_dict[display_name], self.tag_value_input.text())
        self.add_tag_to_preview()
        self.filter_tags.append(new_tag)

        print(f'Added tag to filters: {new_tag}')

    # fills scan_code_selector with valid codes and adds them to a dictionary matching display names to code names
    def find_valid_scan_codes(self):
        tree = ET.parse('ibapi_connections/scanner.xml')
        root = tree.getroot()

        valid_scan_codes = [
            "TOP_PERC_GAIN", "TOP_PERC_LOSE", "MOST_ACTIVE", "NOT_YET_TRADED_TODAY",
            "HALTED", "LIMIT_UP_DOWN", "HOT_BY_PRICE", "HOT_BY_VOLUME",  "HOT_BY_PRICE_RANGE", "TOP_VOLUME_RATE",
            "HIGH_OPEN_GAP", "LOW_OPEN_GAP", "TOP_AFTER_HOURS_PERC_GAIN",
            "TOP_AFTER_HOURS_PERC_LOSE", "HIGH_LAST_VS_EMA20", "LOW_LAST_VS_EMA20",
            "HIGH_LAST_VS_EMA50", "LOW_LAST_VS_EMA50", "HIGH_LAST_VS_EMA100", "LOW_LAST_VS_EMA100",
            "HIGH_LAST_VS_EMA200","LOW_LAST_VS_EMA200"
        ]

        for scan_type in root.findall(".//ScanTypeList/ScanType"):
            code = scan_type.find("scanCode")
            display_name = scan_type.find("displayName")
            if code is not None and code.text.strip() in valid_scan_codes:
                self.scan_code_dict[display_name.text.strip()] = code.text.strip()
                self.scan_code_selector.addItem(display_name.text.strip())
        print(f"Scan Codes: {self.scan_code_dict}")

    # fills tag_category_selector with valid tags and adds them to dictionary matching display names to code names
    def find_valid_tag_categories(self):
        tree = ET.parse('ibapi_connections/scanner.xml')
        root = tree.getroot()

        # filters that can be used with STK instruments
        valid_filters = [
            "AFTERHRSCHANGE", "AFTERHRSCHANGEPERC", "AVGVOLUME",
            "EMA_20", "EMA_50","EMA_100", "EMA_200", "PRICE_VS_EMA_20", "PRICE_VS_EMA_50", "PRICE_VS_EMA_100",
            "PRICE_VS_EMA_200", "GROWTHRATE", "HALTED", "MACD",
            "PRICE", "SHORTSALERESTRICTED", "STVOLUME_3MIN", "STVOLUME_5MIN",
            "STVOLUME_10MIN", "VOLUME", "VOLUMERATE"
        ]

        # adds tag codes and display names to dictionaries for reference
        for scan_type in root.findall(".//FilterList/RangeFilter"):
            filter_id = scan_type.find("id").text.strip()
            if filter_id is not None and filter_id in valid_filters:
                code = scan_type.find("AbstractField/code")
                display_name = scan_type.find("AbstractField/displayName")
                if code is not None and code.text and display_name is not None and display_name.text:
                    self.tag_category_dict[display_name.text.strip()] = code.text.strip()
                    self.tag_code_to_display_name[code.text.strip()] = display_name.text.strip()
                    self.tag_category_selector.addItem(display_name.text.strip())
        print(self.tag_category_dict)

    # handles preview category change
    def change_preview_category(self):
        self.preview_code_category.setText(self.scan_code_selector.currentText())

    # handles adding tag to preview
    def add_tag_to_preview(self):
        tag = QListWidgetItem(f"{self.tag_category_selector.currentText()}: {self.tag_value_input.text()}")
        self.preview_tags_list.addItem(tag)

    # clears all tags
    def clear_tags(self):
        self.preview_tags_list.clear()
        self.filter_tags.clear()

    # initializes scanners in TWS API from mongo database
    def initialize_saved_scanners(self):
        saved_scanners = mongo_fetch_scanners(self.app.client)
        for scanner in saved_scanners:

            scanner_details_obj = ScannerSubscription()
            scanner_details_obj.instrument = scanner["scanner_details"]["instrument"]
            scanner_details_obj.locationCode = scanner["scanner_details"]["locationCode"]
            scanner_details_obj.scanCode = scanner["scanner_details"]["scanCode"]

            req_id = scanner["req_id"]

            tag_values = []
            for tag in scanner["tags"]:
                tag_name = tag["tag"]
                value = tag["value"]
                tag_values.append(TagValue(tag_name, value))

            req_saved_scanner_subscription(self.app, scanner_details_obj, tag_values, req_id)

    # handles scanner tab close event, deleting from QTab widget, mongodb, and cancelling scanner subscription
    def close_tab(self, index):
        req_id = self.scanner_tabs.tabBar().tabData(index)
        self.scanner_tabs.removeTab(index)
        cancel_subscription(self.app, req_id)
        mongo_remove_market_scanner(self.app.client, req_id)
        print(f"Closing tab and connection for Mkt Scanner with id {req_id}")

    # handles closing subscriptions for tabs not in focus to manage data limitations
    def pause_tabs_not_in_focus(self):
        if self.scanner_tabs.count() > 1:
            index = 1
            while index < self.scanner_tabs.count():
                req_id = self.scanner_tabs.tabBar().tabData(index)
                cancel_subscription(self.app, req_id)
                index += 1
                print(f"Canceled scanner id {req_id} subscription on open")

    # handles switching between which tab is open and opening/closing scanner subscriptions accordingly
    def handle_tab_switch(self, index):

        # req_id for the new tab
        new_tab_req_id = self.scanner_tabs.tabBar().tabData(index)
        if new_tab_req_id == self.current_table_req_id:
            return

        # closes subscription for previous tab
        if self.current_table_req_id is not None:
            cancel_subscription(self.app, self.current_table_req_id)
            stop_mkt_data_stream(self.app, self.current_table_req_id)
            print(f"Closed subscription for scanner {self.current_table_req_id}")

        self.current_table_req_id = new_tab_req_id

        # reopen subscription for new tab
        scanner_data = mongo_fetch_matching_scanner(self.app.client, new_tab_req_id)

        # reconstructs scanner obj
        scanner_details_obj = ScannerSubscription()
        scanner_details_obj.instrument = scanner_data["scanner_details"]["instrument"]
        scanner_details_obj.locationCode = scanner_data["scanner_details"]["locationCode"]
        scanner_details_obj.scanCode = scanner_data["scanner_details"]["scanCode"]

        tag_values = []
        for tag in scanner_data["tags"]:
            tag_name = tag["tag"]
            value = tag["value"]
            tag_values.append(TagValue(tag_name, value))

        # reopen scanner subscription
        req_saved_scanner_subscription(self.app, scanner_details_obj, tag_values, new_tab_req_id)
        print(f"Reopened subscription for scanner {new_tab_req_id}")

        print(f"Switched to tab {index} with req_id {new_tab_req_id}")
