from PyQt5.QtWidgets import *
from kiwoom.kiwoom import *
import sys


class Ui_class():
    def __init__(self):
        print("화면 클래스 입니다. ")

        # UI 를 실행하기 위한 필요한 함수나 변수를 사용 용도
        self.app = QApplication(sys.argv)               # PyQt5로 실행할 파일명을 자동 설정
        self.kiwoom = Kiwoom()                          # 키움 클래스 객체화
        self.app.exec_()                                # 이벤트 루프 실행

