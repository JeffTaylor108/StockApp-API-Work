import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QGroupBox, QListWidget, \
    QListWidgetItem, QHBoxLayout, QTableWidget, QTabWidget, QTableWidgetItem
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue

from gui import styling
from ibapi_connections.market_scanner import req_scanner_subscription


class MarketScannerWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.filter_tags = []
        self.scan_code_dict = {}
        self.tag_category_dict = {}

        # widgets added to layout
        widget_label = QLabel("Market Scanners")

        # current active scanners
        scanner_table_label = QLabel("Current Active Scanners")
        scanner_note = QLabel("Note: max 10 scanners active")
        self.scanner_tabs = QTabWidget()
        self.scanner_table = QTableWidget()
        self.scanner_table.setColumnCount(2)
        self.scanner_table.setHorizontalHeaderLabels(["Symbol", "Last Price"])
        self.scanner_table.setRowCount(50)
        self.scanner_tabs.addTab(self.scanner_table, "Scanner 1")

        self.scanner_table2 = QTableWidget()
        self.scanner_tabs.addTab(self.scanner_table2, "Scanner 2")

        # selects scanner code category
        scan_code_label = QLabel("Select Scanner Category")
        self.scan_code_selector = QComboBox()
        self.scan_code_selector.currentTextChanged.connect(self.change_preview_category)

        # selects filtering tag category
        tag_category_label = QLabel("Select Filter Tag")
        self.tag_category_selector = QComboBox()

        # selects filtering tag value
        tag_value_label = QLabel("Filter Tag Value")
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
        self.app.active_scanners_updated.connect(self.update_scanner_tables)

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

        req_scanner_subscription(self.app, scanner, self.filter_tags)

    # creates new scanner table and adds it to tabs
    def update_scanner_tables(self, scan_data_obj):
        rank = scan_data_obj.rank
        symbol = scan_data_obj.contract.symbol
        print(f'Rank: {rank}, Symbol: {symbol}')

        self.scanner_table.setItem(int(rank), 0, QTableWidgetItem(symbol))

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

        # filters that can be used with STK instruments
        valid_filters = [
            "ABSCHANGEPERC", "AFTERHRSCHANGE", "AFTERHRSCHANGEPERC", "AVGOPTVOLUME", "AVGPRICETARGET", "AVGRATING",
            "AVGTARGET2PRICERATIO", "AVGVOLUME", "AVGVOLUME_USD", "CHANGEOPENPERC", "CHANGEPERC", "EMA_20", "EMA_50",
            "EMA_100", "EMA_200", "PRICE_VS_EMA_20", "PRICE_VS_EMA_50", "PRICE_VS_EMA_100", "PRICE_VS_EMA_200",
            "DIVIB", "DIVYIELDIB", "FEERATE", "FIRSTTRADEDATE", "GROWTHRATE", "HALTED", "HASOPTIONS", "HISTDIVIB",
            "HISTDIVYIELDIB", "IMBALANCE", "IMBALANCEADVRATIOPERC", "IMPVOLAT", "IMPVOLATCHANGEPERC",
            "IMPVOLATOVERHIST",
            "INSIDEROFFLOATPERC", "INSTITUTIONALOFFLOATPERC", "MACD", "MACD_SIGNAL", "MACD_HISTOGRAM", "MKTCAP",
            "MKTCAP_USD", "NEXTDIVAMOUNT", "NEXTDIVDATE", "NUMPRICETARGETS", "NUMRATINGS", "NUMSHARESINSIDER",
            "NUMSHARESINSTITUTIONAL", "OPENGAPPERC", "OPTOI", "OPTVOLUME", "OPTVOLUMEPCRATIO", "PEAELIGIBLE", "PERATIO",
            "PPO", "PPO_SIGNAL", "PPO_HISTOGRAM", "PRICE", "PRICE2BK", "PRICE2TANBK", "PRICERANGE", "PRICE_USD",
            "QUICKRATIO", "REGIMBALANCE", "REGIMBALANCEADVRATIOPERC", "RETEQUITY", "SHORTABLESHARES",
            "SHORTSALERESTRICTED", "SIC", "ISSUER_COUNTRY_CODE", "STKTYPE", "STVOLUME_3MIN", "STVOLUME_5MIN",
            "STVOLUME_10MIN", "TRADECOUNT", "TRADERATE", "UNSHORTABLE", "VOLUME", "VOLUMERATE", "VOLUME_USD",
            "RCGLTCLASS", "RCGLTENDDATE", "RCGLTIVALUE", "RCGLTTRADE", "RCGITCLASS", "RCGITENDDATE", "RCGITIVALUE",
            "RCGITTRADE", "RCGSTCLASS", "RCGSTENDDATE", "RCGSTIVALUE", "RCGSTTRADE", "ESG_SCORE", "ESG_COMBINED_SCORE",
            "ESG_CONTROVERSIES_SCORE", "ESG_RESOURCE_USE_SCORE", "ESG_EMISSIONS_SCORE", "ESG_ENV_INNOVATION_SCORE",
            "ESG_WORKFORCE_SCORE", "ESG_HUMAN_RIGHTS_SCORE", "ESG_COMMUNITY_SCORE", "ESG_PRODUCT_RESPONSIBILITY_SCORE",
            "ESG_MANAGEMENT_SCORE", "ESG_SHAREHOLDERS_SCORE", "ESG_CSR_STRATEGY_SCORE", "ESG_ENV_PILLAR_SCORE",
            "ESG_SOCIAL_PILLAR_SCORE", "ESG_CORP_GOV_PILLAR_SCORE", "IV_RANK13", "IV_RANK26", "IV_RANK52",
            "IV_PERCENTILE13", "IV_PERCENTILE26", "IV_PERCENTILE52", "HV_RANK13", "HV_RANK26", "HV_RANK52",
            "HV_PERCENTILE13", "HV_PERCENTILE26", "HV_PERCENTILE52", "PRICE_2_SALES", "EQUITY_PER_SHARE", "UTILIZATION",
            "SSCORE", "SCHANGE", "SVSCORE", "SVCHANGE", "EPS_CHANGE_TTM", "REV_CHANGE", "REV_GROWTH_RATE_5Y",
            "PAYOUT_RATIO_TTM", "PRICE_2_CASH_TTM", "OPERATING_MARGIN_TTM", "NET_PROFIT_MARGIN_TTM",
            "RETURN_ON_INVESTMENT_TTM"
        ]

        # filters out tags that aren't valid with STK instruments
        for scan_type in root.findall(".//FilterList/RangeFilter"):
            filter_id = scan_type.find("id").text.strip()
            if filter_id is not None and filter_id in valid_filters:
                code = scan_type.find("AbstractField/code")
                display_name = scan_type.find("AbstractField/displayName")
                if code is not None and code.text and display_name is not None and display_name.text:
                    self.tag_category_dict[display_name.text.strip()] = code.text.strip()
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