from kiwoom.kiwoom import *
import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("Ui_class 입니다. ")

        # UI 를 실행하기 위한 필요한 함수나 변수를 사용 용도
        self.app = QApplication(sys.argv)

        self.kiwoom = Kiwoom()

        self.app.exec_()
