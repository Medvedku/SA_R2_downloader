from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QHBoxLayout
)

from app.config import save_config, load_config
from app.sync import test_connection
from app import theme


class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("R2 Configuration")
        self.setMinimumWidth(450)
        self.setStyleSheet(theme.get_stylesheet())

        layout = QVBoxLayout()
        form = QFormLayout()

        self.endpoint = QLineEdit()
        self.access_key = QLineEdit()
        self.secret_key = QLineEdit()
        self.secret_key.setEchoMode(QLineEdit.Password)
        self.bucket = QLineEdit()
        self.local_path = QLineEdit()

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_folder)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.local_path)
        path_layout.addWidget(browse_btn)

        form.addRow("R2 Endpoint:", self.endpoint)
        form.addRow("Access Key:", self.access_key)
        form.addRow("Secret Key:", self.secret_key)
        form.addRow("Bucket:", self.bucket)
        form.addRow("Local Folder:", path_layout)

        # Prefill with existing config so user can change only the destination folder
        cfg = load_config()
        if cfg:
            self.endpoint.setText(cfg.get("endpoint", ""))
            self.access_key.setText(cfg.get("access_key", ""))
            self.secret_key.setText(cfg.get("secret_key", ""))
            self.bucket.setText(cfg.get("bucket", ""))
            self.local_path.setText(cfg.get("local_path", ""))

        layout.addLayout(form)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_and_test)

        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select destination folder")
        if folder:
            self.local_path.setText(folder)

    def save_and_test(self):
        config = {
            "endpoint": self.endpoint.text().strip(),
            "access_key": self.access_key.text().strip(),
            "secret_key": self.secret_key.text().strip(),
            "bucket": self.bucket.text().strip(),
            "local_path": self.local_path.text().strip(),
        }

        if not all(config.values()):
            QMessageBox.warning(self, "Missing data",
                                "Please fill all fields.")
            return

        try:
            test_connection(config)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection failed",
                f"Unable to connect to R2:\n\n{e}"
            )
            return

        save_config(config)
        QMessageBox.information(
            self, "Success", "Configuration saved successfully.")
        self.accept()