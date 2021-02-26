from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("kiwoom 클래스 입니다.")

        ###### eventloop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        ###########################

        ####### 스크린번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        #########################

        ###### 변수 모음
        self.account_num = None
        ###########################

        ###### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ###########################

        ###### 변수 모음
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        ###########################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()

        # 계좌번호 가져오기
        self.get_account_info()
        # 예수금 가져오기
        self.detail_account_info()
        # 계좌평가잔고내역요청
        self.detail_account_mystock()
        # 미체결 요청하기
        self.not_concluded_account()
        # 종목 분석용, 임시용으로 실행
        self.calculator_fnc()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        # 예수금 가져오기 EVENT
        self.OnReceiveTrData.connect(self.trdata_slot)

    def login_slot(self, errCode):
        print(errCode)
        print(errors(errCode))

        self.login_event_loop.exit()

    #계좌번호 가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCLIST")
        #계좌번호 232424; 세미콜론 같이 나옴
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호  %s" % self.account_num)


    # 수동 로그인설정인 경우 로그인창을 출력해서 로그인을 시도하거나 자동로그인 설정인 경우 로그인창 출력없이 로그인을 시도합니다.
    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    def detail_account_info(self):
        print("예수금을 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)","계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        # 회원번호 스크린번호
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청" ,  "opw00001"	,  "0"	,  self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가잔고내역요청 연속조회  %s" % sPrevNext)
        self.dynamicCall("SetInputValue(String, String)","계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")

        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext = "0"):
        self.dynamicCall("SetInputValue(String, String)","계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "체결구부", "1")
        self.dynamicCall("SetInputValue(String, String)", "매매구분", "0")
        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        TR요청을 받는 구역이다. 슬롯이다.
        :param sScrNo:  스크린 번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode:    요청ID, TR코드
        :param sRecordName: 사용안함
        :param PrevNext: 다음페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode,sRQName, 0, "예수금" )
            print("예수금 %s" % type(deposit))
            print("예수금 형변환 %s" % int(deposit))

            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode,sRQName, 0, "출금가능금액" )
            print("출금가능금액 %s" % type(ok_deposit))
            print("출금가능금액 형변환 %s" % int(deposit))

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode,sRQName, 0, "총매입금액" )
            total_buy_money_result = int(total_buy_money)
            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode,sRQName, 0, "총수익률(%)" )
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%%) %s" % total_profit_loss_rate_result)

            # 20개까지 조회 가능
            rows = self.dynamicCall("GetRepeatCnt(QString, QString", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                # 종목코드 A003322
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})
                    # self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity   = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명 " : code_nm})
                self.account_stock_dict[code].update({"보유수량 ": stock_quantity})
                self.account_stock_dict[code].update({"매입가 ": buy_price})
                self.account_stock_dict[code].update({"수익률(%) " : learn_rate})
                self.account_stock_dict[code].update({"현재가 ": current_price})
                self.account_stock_dict[code].update({"매입금액 ": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량 ": possible_quantity})

                cnt += 1

            print("계좌가 가지고 있는 종목 %s" % self.account_stock_dict)
            print("계좌에 보유종목 카운트 %s" % cnt)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            print("실시간미체결요청 ");
            rows = self.dynamicCall("GetRepeatCnt(QString, QString", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")
                # 접수 -> 확인 -> 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")
                # 매도 매수
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")


                code = code.strip()
                code_nm =   code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity =int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-') # "-매도" "+매수" 지우기
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                nasd = self.not_account_stock_dict[order_no]
                nasd.upate({"종목코드":code})
                self.not_account_stock_dict[order_no].upate({"종목명": code_nm})
                self.not_account_stock_dict[order_no].upate({"주문번호": order_no})
                self.not_account_stock_dict[order_no].upate({"주문상태": order_status})
                self.not_account_stock_dict[order_no].upate({"주문수량": order_quantity})
                self.not_account_stock_dict[order_no].upate({"주문가격": order_price})
                self.not_account_stock_dict[order_no].upate({"주문구분": order_gubun})
                self.not_account_stock_dict[order_no].upate({"미체결수량": not_quantity})
                self.not_account_stock_dict[order_no].upate({"체결량": ok_quantity})

                print("미체결 종목 : %s" % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            print("%s 일봉데이터 요청" % code)


    def get_code_list_by_market(self, market_code):
        '''
        종목코드 반환
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        # 마지막 빈자리 자르기 [:-1]
        code_list = code_list.split(";")[:-1]

        return code_list

    def calculator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:ss
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥 갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
            print("%s / %s : KOSDAQ Stock Code : %s is updating... " % (idx+1, len(code_list), code))

            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(String, String, int, String)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
2