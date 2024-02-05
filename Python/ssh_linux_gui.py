import sys
import ssh_linux
import os
import traceback
import json
import shutil
from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QRadioButton, QPushButton, QMessageBox, QFileDialog, QButtonGroup, QStyleFactory)
from jinja2 import Environment, FileSystemLoader

class LinuxServerInfoGUI(QWidget):
    def __init__(self):
        super().__init__()
        QApplication.setStyle(QStyleFactory.create('Fusion'))  # Set Fusion style
        self.setWindowTitle('Linux Server Info')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.host_label = QLabel('서버 주소:')
        self.host_input = QLineEdit(self)
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)

        self.port_label = QLabel('포트:')
        self.port_input = QLineEdit(self)
        self.port_input.setText("22")  # default SSH port
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        self.username_label = QLabel('사용자 이름:')
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.auth_label = QLabel('인증 방식 선택:')
        layout.addWidget(self.auth_label)

        self.password_button = QRadioButton('암호')
        self.keypair_button = QRadioButton('키페어')
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.password_button)
        self.button_group.addButton(self.keypair_button)
        layout.addWidget(self.password_button)
        layout.addWidget(self.keypair_button)
        self.keypair_button.toggled.connect(self.toggle_keypair_button)

        self.auth_info_label = QLabel('인증 방식:')
        self.auth_input = QLineEdit(self)
        layout.addWidget(self.auth_info_label)
        layout.addWidget(self.auth_input)

        self.select_key_button = QPushButton("키페어 선택", self)
        self.select_key_button.clicked.connect(self.select_key_file)
        layout.addWidget(self.select_key_button)

        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)

        self.download_tf_button = QPushButton('테라폼 템플릿 다운로드', self)
        self.download_tf_button.clicked.connect(self.download_terraform_template)
        layout.addWidget(self.download_tf_button)

        self.setLayout(layout)

    def toggle_keypair_button(self, checked):
        if checked:
            self.auth_input.clear()
            self.select_key_button.setEnabled(True)
        else:
            self.select_key_button.setEnabled(False)
            self.auth_input.clear()

    def select_key_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "키페어 선택", "", "All Files (*)", options=options)
        if file_name:
            self.auth_input.setText(file_name)

    def connect_to_server(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        key_path = None
        password = None
        
        if self.password_button.isChecked():
            password = self.auth_input.text()
        elif self.keypair_button.isChecked():
            key_path = self.auth_input.text()

        try:
            host_info = ssh_linux.get_server_info(host, port, username, password, key_path)
            
            # 추출한 정보를 S3에 저장하기
            s3_bucket_name = "mte-project"
            s3_key_path = f"json(terraform)/{host}_info.json"  # 예: json(terraform)/192.168.1.1_info.json
            ssh_linux.save_data_to_s3(host_info, s3_bucket_name, s3_key_path)

            # Jinja2 템플릿 적용
            env = Environment(loader=FileSystemLoader(ssh_linux.TEMPLATE_DIR))
            template = env.get_template('ec2_template.tf.j2')
            terraform_code = template.render(data=host_info)
            
            # 테라폼 코드를 일시적인 파일로 저장
            self.temp_tf_file = NamedTemporaryFile(delete=False, suffix=".tf", mode='wt')
            self.temp_tf_file.write(terraform_code)
            self.temp_tf_file.close()
            
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Server Info")
            msg_box.setText(json.dumps(host_info, indent=4))
            msg_box.exec_()

        except Exception as e:
            traceback.print_exc()
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText(f"An error occurred: {str(e)}")
            error_box.exec_()

    def download_terraform_template(self):
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "테라폼 템플릿 저장 위치 선택", "", "Terraform Files (*.tf);;All Files (*)", options=options)
        if save_path:
            shutil.copy(self.temp_tf_file.name, save_path)
            QMessageBox.information(self, "성공", "테라폼 템플릿이 성공적으로 저장되었습니다.")
            os.remove(self.temp_tf_file.name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LinuxServerInfoGUI()
    ex.show()
    sys.exit(app.exec_())