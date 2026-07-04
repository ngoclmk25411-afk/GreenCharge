import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt

# Local utilities
from .vehicle_utils import (
    get_vehicles_by_user,
    add_vehicle,
    update_vehicle,
    delete_vehicle,
)

class VehicleManagementWidget(QWidget):
    """Customer‑facing widget to CRUD their own vehicles.
    
    Expected to be added as a tab for role "KhachHang".
    """
    def __init__(self, user_info: dict):
        super().__init__()
        self.user = user_info
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Title
        title = QLabel("🛻 Quản lý xe của tôi")
        title.setStyleSheet("font-size: 18px; font-weight: 700; margin-bottom: 12px;")
        layout.addWidget(title)
        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Biển số", "Chuẩn sạc"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        # Form for add / edit
        form_layout = QHBoxLayout()
        self.input_bien = QLineEdit()
        self.input_bien.setPlaceholderText("Biển số")
        self.input_chuan = QLineEdit()
        self.input_chuan.setPlaceholderText("Chuẩn sạc (e.g., CCS, CHAdeMO)")
        form_layout.addWidget(self.input_bien)
        form_layout.addWidget(self.input_chuan)
        layout.addLayout(form_layout)
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Thêm xe")
        self.btn_edit = QPushButton("✏️ Sửa xe")
        self.btn_delete = QPushButton("🗑️ Xóa xe")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        # Connect signals
        self.btn_add.clicked.connect(self._add_vehicle)
        self.btn_edit.clicked.connect(self._edit_vehicle)
        self.btn_delete.clicked.connect(self._delete_vehicle)
        self.table.itemSelectionChanged.connect(self._populate_form_from_selection)

    def _load_data(self):
        """Load vehicles from DB and populate table."""
        self.table.setRowCount(0)
        rows = get_vehicles_by_user(self.user["MaNguoiDung"])
        for row in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col, item)
        self.table.resizeColumnsToContents()

    def _populate_form_from_selection(self):
        selected = self.table.selectedItems()
        if selected:
            # items are ordered row-wise; first column is ID
            self.input_bien.setText(selected[1].text())
            self.input_chuan.setText(selected[2].text())
        else:
            self.input_bien.clear()
            self.input_chuan.clear()

    def _add_vehicle(self):
        bien = self.input_bien.text().strip()
        chuan = self.input_chuan.text().strip()
        if not bien or not chuan:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ biển số và chuẩn sạc.")
            return
        try:
            add_vehicle(self.user["MaNguoiDung"], bien, chuan)
            QMessageBox.information(self, "Thành công", "Thêm xe thành công.")
            self.input_bien.clear()
            self.input_chuan.clear()
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm xe: {e}")

    def _edit_vehicle(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một xe để sửa.")
            return
        vehicle_id = int(selected[0].text())
        bien = self.input_bien.text().strip()
        chuan = self.input_chuan.text().strip()
        if not bien or not chuan:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ biển số và chuẩn sạc.")
            return
        try:
            update_vehicle(vehicle_id, bien, chuan)
            QMessageBox.information(self, "Thành công", "Cập nhật xe thành công.")
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa xe: {e}")

    def _delete_vehicle(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một xe để xóa.")
            return
        vehicle_id = int(selected[0].text())
        confirm = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc muốn xóa xe ID {vehicle_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_vehicle(vehicle_id)
            QMessageBox.information(self, "Thành công", "Xóa xe thành công.")
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa xe: {e}")
