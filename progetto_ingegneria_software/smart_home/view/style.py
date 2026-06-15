STILE_GLOBALE = """
QMainWindow {
    background-color: #f5f5f5;
}

QTabWidget::pane {
    background-color: #f5f5f5;
    border: none;
}

QTabBar::tab {
    color: #666666;
    padding: 8px 16px;
    font-size: 13px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:hover {
    color: #333333;
}

QTabBar::tab:selected {
    color: #2563eb;
    border-bottom: 2px solid #2563eb;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #fafafa;
    border: 1px solid #e0e0e0;
    gridline-color: #f0f0f0;
    selection-background-color: #e8f0fe;
    selection-color: #333333;
    color: #333333;
    outline: none;
}

QTableWidget::item {
    padding: 6px 10px;
    color: #333333;
}

QHeaderView::section {
    background-color: #fafafa;
    color: #555555;
    font-weight: 600;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #e0e0e0;
    font-size: 12px;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 7px 16px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton#btn_elimina {
    background-color: #dc2626;
}

QPushButton#btn_elimina:hover {
    background-color: #b91c1c;
}

QPushButton#btn_annulla {
    background-color: #ffffff;
    color: #555555;
    border: 1px solid #d0d0d0;
}

QPushButton#btn_annulla:hover {
    background-color: #fafafa;
}

QPushButton#btn_esci {
    background-color: #ffffff;
    color: #666666;
    border: 1px solid #d0d0d0;
    padding: 5px 12px;
    font-size: 12px;
}

QPushButton#btn_esci:hover {
    background-color: #f5f5f5;
    color: #dc2626;
    border-color: #dc2626;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    color: #333333;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTimeEdit:focus {
    border-color: #2563eb;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    color: #333333;
}

QComboBox:focus {
    border-color: #2563eb;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    selection-background-color: #e8f0fe;
    selection-color: #333333;
}

QGroupBox {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    margin-top: 12px;
    padding: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 12px;
    font-size: 13px;
    color: #333333;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    color: #333333;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    color: #333333;
}

QListWidget::item:hover {
    background-color: #fafafa;
}

QListWidget::item:selected {
    background-color: #e8f0fe;
    color: #333333;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 8px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #aaaaaa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background-color: #cccccc;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #aaaaaa;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QLabel {
    color: #444444;
    background-color: transparent;
}

QCheckBox {
    spacing: 6px;
    font-size: 13px;
    color: #444444;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #cccccc;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

QDialog {
    background-color: #ffffff;
}
"""
