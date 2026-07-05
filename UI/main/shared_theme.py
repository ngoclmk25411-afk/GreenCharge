# ─────────────────────────────────────────────────────────────
#  shared_theme.py  —  Light Green Theme cho toàn bộ widget con
# ─────────────────────────────────────────────────────────────

G1  = "#059669"
G2  = "#10b981"
G3  = "#34d399"
G_L = "#e2e8e5"
G_M = "#d1fae5"
G_B = "#a7f3d0"

GROUP_STYLE = f"""
QGroupBox {{
    font-weight: 700;
    color: {G1};
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: {G1};
    font-size: 13px;
}}
"""

TABLE_STYLE = f"""
QTableWidget {{
    background-color: #ffffff;
    color: #1f2937;
    gridline-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: {G_M};
    selection-color: {G1};
    alternate-background-color: #f8fafc;
}}
QHeaderView::section {{
    background-color: #f8fafc;
    color: #475569;
    font-weight: 700;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #f1f5f9;
    font-size: 12px;
    text-align: center;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
}}
QTableWidget::item:selected {{
    background-color: {G_M};
    color: {G1};
}}
QTableWidget::item:hover {{
    background-color: {G_L};
}}
"""

COMBO_STYLE = f"""
QComboBox {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}}
QComboBox:focus {{ border: 1.5px solid {G2}; background: #ffffff; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #1f2937;
    selection-background-color: {G_M};
    selection-color: {G1};
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}}
"""

INPUT_STYLE = f"""
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border: 1.5px solid {G2};
    background-color: #ffffff;
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background-color: #ffffff;
    color: #1f2937;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
}}
QLabel {{
    color: #374151;
    font-weight: 600;
    font-size: 12px;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
}}
QLineEdit, QComboBox, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
}}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {G2};
    background: #ffffff;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: #ffffff; color: #1f2937;
    selection-background-color: {G_M}; selection-color: {G1};
    border: 1px solid #e2e8f0;
}}
QDialogButtonBox QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {G1},stop:1 {G2});
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-width: 80px;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
}}
QDialogButtonBox QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {G2},stop:1 {G3});
}}
"""

TITLE_STYLE = f"color: {G1}; font-size: 16px; font-weight: 700;"
LBL_STYLE   = f"color: #374151; font-weight: 600; font-size: 12px;"


def btn_style(color=None):
    c = color or G1
    return (
        f"QPushButton {{ background-color: {c}; color: #fff; border: none;"
        f" border-radius: 8px; padding: 8px 18px; font-weight: 600; font-size: 13px;"
        f" font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif; }}"
        f" QPushButton:hover {{ background-color: {G2}; }}"
        f" QPushButton:pressed {{ background-color: #047857; }}"
    )


def status_color(val: str) -> str:
    """Trả màu tương ứng trạng thái (dùng cho QTableWidgetItem.setForeground)."""
    mapping = {
        "Hoạt động":  G1,
        "Trống":       G1,
        "Đã thanh toán": G1,
        "Hoàn thành":  G1,
        "Đang sạc":   "#2563eb",
        "Chờ duyệt":  "#d97706",
        "Chờ xử lý":  "#d97706",
        "Tạm ngừng":  "#d97706",
        "Bảo trì":    "#d97706",
        "Chưa thanh toán": "#d97706",
        "Đang hỏng":  "#dc2626",
        "Huỷ":        "#dc2626",
        "Từ chối":    "#dc2626",
    }
    return mapping.get(val, "#374151")