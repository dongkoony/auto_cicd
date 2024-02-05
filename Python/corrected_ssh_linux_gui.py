from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox
from jinja2 import Environment, FileSystemLoader
import os
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'SSH Linux GUI'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        layout = QVBoxLayout()
        
        self.loadTemplateBtn = QPushButton('Load Template', self)
        self.loadTemplateBtn.clicked.connect(self.loadTemplate)
        layout.addWidget(self.loadTemplateBtn)
        
        self.setLayout(layout)
    
    def loadTemplate(self):
        try:
            # Correct the path to the template directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(base_dir, 'Template')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('ec2_instance.tf.j2')
            QMessageBox.information(self, 'Success', 'Template loaded successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load template: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
