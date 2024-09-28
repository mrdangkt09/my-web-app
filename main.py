import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QMessageBox, QTabWidget, QLabel, 
                             QComboBox, QSpinBox, QLineEdit)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('store.db')
cursor = conn.cursor()

# Tạo bảng sản phẩm, khách hàng, hóa đơn và mục hóa đơn nếu chưa có
cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, quantity INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS customers
                  (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, address TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS invoices
                  (id INTEGER PRIMARY KEY, customer_name TEXT, total_price REAL, date TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS invoice_items
                  (id INTEGER PRIMARY KEY, invoice_id INTEGER, product_name TEXT, quantity INTEGER, price REAL)''')

class StoreApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hệ thống quản lý bán hàng Kiot Việt')
        self.setGeometry(100, 100, 1000, 600)

        # Thiết lập font
        font = QFont("Arial", 10)
        self.setFont(font)

        # Tạo QTabWidget để chứa các tab khác nhau
        self.tabs = QTabWidget()

        # Tab Quản lý sản phẩm
        self.product_tab = QWidget()
        self.product_layout = QVBoxLayout()
        self.product_table = QTableWidget()
        self.load_products()
        
        # Khung tìm kiếm sản phẩm
        self.search_product_input = QLineEdit(self)
        self.search_product_input.setPlaceholderText('Tìm kiếm sản phẩm...')
        self.search_product_input.textChanged.connect(self.search_product)
        self.product_layout.addWidget(self.search_product_input)

        # Khung thêm sản phẩm
        self.product_form = QHBoxLayout()
        self.product_name_input = QLineEdit(self)
        self.product_name_input.setPlaceholderText('Tên sản phẩm')
        self.product_form.addWidget(self.product_name_input)
        
        self.product_category_input = QLineEdit(self)
        self.product_category_input.setPlaceholderText('Danh mục')
        self.product_form.addWidget(self.product_category_input)

        self.product_price_input = QLineEdit(self)
        self.product_price_input.setPlaceholderText('Giá')
        self.product_form.addWidget(self.product_price_input)

        self.product_quantity_input = QLineEdit(self)
        self.product_quantity_input.setPlaceholderText('Số lượng')
        self.product_form.addWidget(self.product_quantity_input)

        self.add_product_button = QPushButton('Thêm sản phẩm', self)
        self.add_product_button.clicked.connect(self.add_product)
        self.product_form.addWidget(self.add_product_button)

        self.update_product_button = QPushButton('Cập nhật sản phẩm', self)
        self.update_product_button.clicked.connect(self.update_product)
        self.product_form.addWidget(self.update_product_button)

        self.delete_product_button = QPushButton('Xóa sản phẩm', self)
        self.delete_product_button.clicked.connect(self.delete_product)
        self.product_form.addWidget(self.delete_product_button)

        self.product_layout.addLayout(self.product_form)
        self.product_layout.addWidget(self.product_table)
        self.product_tab.setLayout(self.product_layout)
        self.tabs.addTab(self.product_tab, "Quản lý sản phẩm")

        # Tab Quản lý khách hàng
        self.customer_tab = QWidget()
        self.customer_layout = QVBoxLayout()
        self.customer_table = QTableWidget()
        self.load_customers()
        
        # Khung tìm kiếm khách hàng
        self.search_customer_input = QLineEdit(self)
        self.search_customer_input.setPlaceholderText('Tìm kiếm khách hàng...')
        self.search_customer_input.textChanged.connect(self.search_customer)
        self.customer_layout.addWidget(self.search_customer_input)

        # Khung thêm khách hàng
        self.customer_form = QHBoxLayout()
        self.customer_name_input = QLineEdit(self)
        self.customer_name_input.setPlaceholderText('Tên khách hàng')
        self.customer_form.addWidget(self.customer_name_input)

        self.customer_phone_input = QLineEdit(self)
        self.customer_phone_input.setPlaceholderText('Số điện thoại')
        self.customer_form.addWidget(self.customer_phone_input)

        self.customer_address_input = QLineEdit(self)
        self.customer_address_input.setPlaceholderText('Địa chỉ')
        self.customer_form.addWidget(self.customer_address_input)

        self.add_customer_button = QPushButton('Thêm khách hàng', self)
        self.add_customer_button.clicked.connect(self.add_customer)
        self.customer_form.addWidget(self.add_customer_button)

        self.update_customer_button = QPushButton('Cập nhật khách hàng', self)
        self.update_customer_button.clicked.connect(self.update_customer)
        self.customer_form.addWidget(self.update_customer_button)

        self.delete_customer_button = QPushButton('Xóa khách hàng', self)
        self.delete_customer_button.clicked.connect(self.delete_customer)
        self.customer_form.addWidget(self.delete_customer_button)

        self.customer_layout.addLayout(self.customer_form)
        self.customer_layout.addWidget(self.customer_table)
        self.customer_tab.setLayout(self.customer_layout)
        self.tabs.addTab(self.customer_tab, "Quản lý khách hàng")

        # Tab Quản lý hóa đơn
        self.invoice_tab = QWidget()
        self.invoice_layout = QVBoxLayout()
        self.invoice_table = QTableWidget()
        self.load_invoices()
        
        # Khung tạo hóa đơn
        self.invoice_form = QHBoxLayout()
        self.customer_combo = QComboBox(self)
        self.load_customers_for_invoice()
        self.invoice_form.addWidget(QLabel("Khách hàng:"))
        self.invoice_form.addWidget(self.customer_combo)

        self.product_combo = QComboBox(self)
        self.load_products_for_invoice()
        self.invoice_form.addWidget(QLabel("Sản phẩm:"))
        self.invoice_form.addWidget(self.product_combo)

        self.invoice_quantity_input = QSpinBox(self)
        self.invoice_quantity_input.setRange(1, 100)
        self.invoice_form.addWidget(QLabel("Số lượng:"))
        self.invoice_form.addWidget(self.invoice_quantity_input)

        self.create_invoice_button = QPushButton('Tạo hóa đơn', self)
        self.create_invoice_button.clicked.connect(self.create_invoice)
        self.invoice_form.addWidget(self.create_invoice_button)

        self.invoice_layout.addLayout(self.invoice_form)
        self.invoice_layout.addWidget(self.invoice_table)
        self.invoice_tab.setLayout(self.invoice_layout)
        self.tabs.addTab(self.invoice_tab, "Quản lý hóa đơn")

        # Tab Báo cáo
        self.report_tab = QWidget()
        self.report_layout = QVBoxLayout()
        self.report_label = QLineEdit('Báo cáo doanh thu, tồn kho, khách hàng, sản phẩm bán chạy')
        self.report_layout.addWidget(self.report_label)
        self.report_tab.setLayout(self.report_layout)
        self.tabs.addTab(self.report_tab, "Báo cáo")

        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Nút thoát
        self.exit_button = QPushButton('Thoát', self)
        self.exit_button.clicked.connect(self.close)
        main_layout.addWidget(self.exit_button)

        self.setLayout(main_layout)

    # Hàm tải danh sách sản phẩm
    def load_products(self):
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        self.product_table.setRowCount(len(products))
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(['ID', 'Tên sản phẩm', 'Danh mục', 'Giá', 'Số lượng'])
        for row_idx, product in enumerate(products):
            for col_idx, data in enumerate(product):
                self.product_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    # Hàm tìm kiếm sản phẩm
    def search_product(self):
        search_text = self.search_product_input.text().lower()
        for row in range(self.product_table.rowCount()):
            item = self.product_table.item(row, 1)  # Tìm kiếm theo tên sản phẩm
            self.product_table.setRowHidden(row, not (search_text in item.text().lower() if item else True))

    # Hàm thêm sản phẩm
    def add_product(self):
        name = self.product_name_input.text()
        category = self.product_category_input.text()
        price = self.product_price_input.text()
        quantity = self.product_quantity_input.text()
        if name and category and price and quantity:
            cursor.execute("INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)", 
                           (name, category, float(price), int(quantity)))
            conn.commit()
            self.load_products()
            QMessageBox.information(self, 'Thông báo', 'Thêm sản phẩm thành công!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập đầy đủ thông tin!')

    # Hàm cập nhật sản phẩm
    def update_product(self):
        row = self.product_table.currentRow()
        if row >= 0:
            id = self.product_table.item(row, 0).text()
            name = self.product_name_input.text()
            category = self.product_category_input.text()
            price = self.product_price_input.text()
            quantity = self.product_quantity_input.text()
            if name and category and price and quantity:
                cursor.execute("UPDATE products SET name=?, category=?, price=?, quantity=? WHERE id=?", 
                               (name, category, float(price), int(quantity), id))
                conn.commit()
                self.load_products()
                QMessageBox.information(self, 'Thông báo', 'Cập nhật sản phẩm thành công!')
            else:
                QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập đầy đủ thông tin!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn sản phẩm để cập nhật!')

    # Hàm xóa sản phẩm
    def delete_product(self):
        row = self.product_table.currentRow()
        if row >= 0:
            id = self.product_table.item(row, 0).text()
            cursor.execute("DELETE FROM products WHERE id=?", (id,))
            conn.commit()
            self.load_products()
            QMessageBox.information(self, 'Thông báo', 'Xóa sản phẩm thành công!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn sản phẩm để xóa!')

    # Hàm tải danh sách khách hàng
    def load_customers(self):
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        self.customer_table.setRowCount(len(customers))
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['ID', 'Tên khách hàng', 'Số điện thoại', 'Địa chỉ'])
        for row_idx, customer in enumerate(customers):
            for col_idx, data in enumerate(customer):
                self.customer_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    # Hàm tìm kiếm khách hàng
    def search_customer(self):
        search_text = self.search_customer_input.text().lower()
        for row in range(self.customer_table.rowCount()):
            item = self.customer_table.item(row, 1)  # Tìm kiếm theo tên khách hàng
            self.customer_table.setRowHidden(row, not (search_text in item.text().lower() if item else True))

    # Hàm thêm khách hàng
    def add_customer(self):
        name = self.customer_name_input.text()
        phone = self.customer_phone_input.text()
        address = self.customer_address_input.text()
        if name and phone and address:
            cursor.execute("INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)", 
                           (name, phone, address))
            conn.commit()
            self.load_customers()
            QMessageBox.information(self, 'Thông báo', 'Thêm khách hàng thành công!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập đầy đủ thông tin!')

    # Hàm cập nhật khách hàng
    def update_customer(self):
        row = self.customer_table.currentRow()
        if row >= 0:
            id = self.customer_table.item(row, 0).text()
            name = self.customer_name_input.text()
            phone = self.customer_phone_input.text()
            address = self.customer_address_input.text()
            if name and phone and address:
                cursor.execute("UPDATE customers SET name=?, phone=?, address=? WHERE id=?", 
                               (name, phone, address, id))
                conn.commit()
                self.load_customers()
                QMessageBox.information(self, 'Thông báo', 'Cập nhật khách hàng thành công!')
            else:
                QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng nhập đầy đủ thông tin!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn khách hàng để cập nhật!')

    # Hàm xóa khách hàng
    def delete_customer(self):
        row = self.customer_table.currentRow()
        if row >= 0:
            id = self.customer_table.item(row, 0).text()
            cursor.execute("DELETE FROM customers WHERE id=?", (id,))
            conn.commit()
            self.load_customers()
            QMessageBox.information(self, 'Thông báo', 'Xóa khách hàng thành công!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng chọn khách hàng để xóa!')

    # Hàm tải danh sách khách hàng cho hóa đơn
    def load_customers_for_invoice(self):
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        for customer in customers:
            self.customer_combo.addItem(customer[1], customer[0])  # Thêm tên khách hàng vào ComboBox

    # Hàm tải danh sách sản phẩm cho hóa đơn
    def load_products_for_invoice(self):
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        for product in products:
            self.product_combo.addItem(product[1], product[0])  # Thêm tên sản phẩm vào ComboBox

    # Hàm tạo hóa đơn
    def create_invoice(self):
        customer_id = self.customer_combo.currentData()  # Lấy ID khách hàng từ ComboBox
        product_id = self.product_combo.currentData()  # Lấy ID sản phẩm từ ComboBox
        quantity = self.invoice_quantity_input.value()  # Lấy số lượng từ SpinBox

        # Lấy thông tin sản phẩm từ cơ sở dữ liệu
        cursor.execute("SELECT name, price FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        if product:
            product_name = product[0]
            product_price = product[1]
            total_price = product_price * quantity
            
            # Thêm hóa đơn vào cơ sở dữ liệu
            cursor.execute("INSERT INTO invoices (customer_name, total_price, date) VALUES (?, ?, date('now'))", 
                           (self.customer_combo.currentText(), total_price))
            invoice_id = cursor.lastrowid  # Lấy ID của hóa đơn vừa tạo

            # Thêm mục hóa đơn vào cơ sở dữ liệu
            cursor.execute("INSERT INTO invoice_items (invoice_id, product_name, quantity, price) VALUES (?, ?, ?, ?)", 
                           (invoice_id, product_name, quantity, product_price))
            conn.commit()

            self.load_invoices()
            QMessageBox.information(self, 'Thông báo', 'Tạo hóa đơn thành công!')
        else:
            QMessageBox.warning(self, 'Cảnh báo', 'Sản phẩm không tồn tại!')

    # Hàm tải danh sách hóa đơn
    def load_invoices(self):
        cursor.execute("SELECT * FROM invoices")
        invoices = cursor.fetchall()
        self.invoice_table.setRowCount(len(invoices))
        self.invoice_table.setColumnCount(4)
        self.invoice_table.setHorizontalHeaderLabels(['ID', 'Khách hàng', 'Tổng tiền', 'Ngày'])
        for row_idx, invoice in enumerate(invoices):
            for col_idx, data in enumerate(invoice):
                self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

# Khởi động ứng dụng
if __name__ == '__main__':
    app = QApplication(sys.argv)
    store = StoreApp()
    store.show()
    sys.exit(app.exec_())
