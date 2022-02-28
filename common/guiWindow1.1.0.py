import sys
import multiprocessing
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QMessageBox)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.first_event_loop = QEventLoop()
        self.second_event_loop = QEventLoop()
        self.third_event_loop = QEventLoop()
        self.serverLabel = QLabel('Server', self)
        self.cpuLabel = QLabel('Multi Process', self)
        self.yourIdLabel = QLabel('Your ID', self)
        self.cb = QComboBox(self)
        self.cb_cpu = QComboBox(self)
        self.cb_id = QComboBox(self)
        self.inputLabel = QLabel('Team Information', self)
        self.userIdList = QLineEdit(self)
        self.scoutBtn = QPushButton('Scout', self)
        self.canWinLabel = QLabel('Can Win : ', self)
        self.winRateLabel = QLabel('50 %', self)
        self.playerLabel = QLabel('Player', self)
        self.player1Label = QLabel('Player1', self)
        self.player2Label = QLabel('Player2', self)
        self.player3Label = QLabel('Player3', self)
        self.player4Label = QLabel('Player4', self)
        self.player5Label = QLabel('Player5', self)
        self.positionLabel = QLabel('Position', self)
        self.cb_p1 = QComboBox(self)
        self.cb_p2 = QComboBox(self)
        self.cb_p3 = QComboBox(self)
        self.cb_p4 = QComboBox(self)
        self.cb_p5 = QComboBox(self)
        self.position_list = ['탑', '정글', '미드', '원딜', '서폿']
        self.championLabel = QLabel('Champion', self)
        self.cb_champ1 = QComboBox(self)
        self.cb_champ2 = QComboBox(self)
        self.cb_champ3 = QComboBox(self)
        self.cb_champ4 = QComboBox(self)
        self.cb_champ5 = QComboBox(self)
        self.detailCheckBtn = QPushButton('Detail Check', self)
        self.canWinLabel2 = QLabel('Can Win : ', self)
        self.winRateLabel2 = QLabel('50 %', self)
        self.initBtn = QPushButton('초기화', self)
        self.init_ui()
        self.user_id_list = []

    def init_ui(self):
        self.cpuLabel.move(10, 10)
        self.cb_cpu.move(140, 5)
        process = multiprocessing.cpu_count()
        process_list = []
        for i in range(1, process + 1):
            process_list.append(str(i))
        self.cb_cpu.addItems(process_list)
        self.cb_cpu.setCurrentText(str(int(process/2)))

        self.serverLabel.move(10, 60)
        self.cb.move(140, 55)
        self.cb.addItems(['Korea', 'Japan', 'North America', 'Europe West', 'Europe Nordic & East', 'Oceania',
                          'Brazil', 'LAS', 'LAN', 'Russia', 'Turkey'])

        self.inputLabel.move(10, 110)

        # setGeometry(상위 윈도우 시작 위치x, y, 가로, 세로)
        self.userIdList.move(140, 110)

        self.yourIdLabel.move(300, 110)
        self.cb_id.move(350, 105)
        self.userIdList.textChanged.connect(self.select_id)

        self.scoutBtn.move(30, 150)
        self.canWinLabel.move(160, 155)
        self.winRateLabel.move(230, 155)
        self.scoutBtn.clicked.connect(self.scouting)

        self.playerLabel.move(60, 200)
        self.player1Label.move(10, 235)
        self.player2Label.move(10, 260)
        self.player3Label.move(10, 285)
        self.player4Label.move(10, 310)
        self.player5Label.move(10, 335)
        self.positionLabel.move(165, 200)
        self.cb_p1.move(160, 230)
        self.cb_p1.addItems(self.position_list)
        self.cb_p2.move(160, 255)
        self.cb_p2.addItems(self.position_list)
        self.cb_p2.setCurrentIndex(1)
        self.cb_p3.move(160, 280)
        self.cb_p3.addItems(self.position_list)
        self.cb_p3.setCurrentIndex(2)
        self.cb_p4.move(160, 305)
        self.cb_p4.addItems(self.position_list)
        self.cb_p4.setCurrentIndex(3)
        self.cb_p5.move(160, 330)
        self.cb_p5.addItems(self.position_list)
        self.cb_p5.setCurrentIndex(4)
        self.championLabel.move(270, 200)
        self.cb_champ1.move(260, 230)
        self.cb_champ2.move(260, 255)
        self.cb_champ3.move(260, 280)
        self.cb_champ4.move(260, 305)
        self.cb_champ5.move(260, 330)

        self.detailCheckBtn.move(30, 360)
        self.canWinLabel2.move(160, 365)
        self.winRateLabel2.move(230, 365)
        self.detailCheckBtn.clicked.connect(self.detail_check)

        self.initBtn.move(30, 400)
        self.initBtn.clicked.connect(self.init_data)

        self.setWindowTitle('LoL Scouter')
        self.setGeometry(200, 200, 700, 600)
        self.show()

    def select_id(self):
        # 로비 접속자 목록 가공
        first_user_id_list = self.userIdList.text().split('님이 로비에 참가하셨습니다.\n')
        first_user_id_list[-1] = first_user_id_list[-1].replace('님이 로비에 참가하셨습니다.', '')

        for i in range(0, 5):
            user_id = first_user_id_list[len(first_user_id_list)+i-5]
            self.user_id_list.append(user_id)

        self.cb_id.addItems(self.user_id_list)

    def scouting(self):
        self.first_event_loop.exit()

    def detail_check(self):
        self.second_event_loop.exit()

    def closeEvent(self, QCloseEvent):
        re = QMessageBox.question(self, "종료 확인", "종료 하시겠습니까?",
                                  QMessageBox.Yes | QMessageBox.No)

        if re == QMessageBox.Yes:
            QCloseEvent.accept()
            sys.exit(0)
        else:
            QCloseEvent.ignore()

    def init_data(self):
        self.third_event_loop.exit()
