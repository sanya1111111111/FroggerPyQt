from PyQt5 import QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QPixmap, QTransform, QPalette
from PyQt5.QtCore import Qt, QTimer, QUrl
import sys

from PyQt5.uic.properties import QtCore


class Wind1(QMainWindow):
    def __init__(self):
        super(Wind1, self).__init__()
        self.setWindowTitle("Frogger")
        self.setGeometry(0,0,700,800)
        self.setFixedSize(700,800)
        self.setStyleSheet("background-color: black; color:white; font-size: 25px")

        self.playScene = QGraphicsScene(0, 0, 700, 700)
        self.playFieldActive = True

        self.grass = QtWidgets.QGraphicsRectItem(0,0,700,700)
        self.grass.setBrush(QBrush(Qt.darkGreen))
        self.grass.setPos(0,0)
        self.grass.setZValue(100)
        self.playScene.addItem(self.grass)

        self.road = QtWidgets.QGraphicsRectItem(0, 0, 700, 300)
        self.road.setBrush(QBrush(Qt.black))
        self.road.setPos(0, 350)
        self.road.setZValue(101)
        self.playScene.addItem(self.road)

        self.slab = QPixmap("slab.png")
        self.fillLine(self.slab, 650, 101)
        self.fillLine(self.slab, 300, 101)

        self.river = QtWidgets.QGraphicsRectItem(0, 0, 699, 248)
        self.river.setBrush(QBrush(Qt.darkBlue))
        self.river.setPos(0, 51)
        self.river.setZValue(101)

        self.techGrass = QtWidgets.QGraphicsRectItem(0,0,700,50)
        self.grass.setBrush(QBrush(Qt.darkGreen))
        self.techGrass.setPos(0,0)
        self.playScene.addItem(self.techGrass)

        self.playScene.addItem(self.river)

        '''
        self.railRoad = QPixmap("railroad.png")
        self.fillLine(self.railRoad, 300, 102)
        self.fillLine(self.railRoad, 350, 102)
        '''

        self.frogPix = QPixmap("FrogAnim/tile000.png").scaledToHeight(50)
        self.deathPix = QPixmap("death.png").scaledToHeight(50)
        self.frog = self.playScene.addPixmap(self.frogPix)
        self.frog.setPos(0, 650)
        self.frog.setZValue(210)

        self.LivesCt = 5
        self.LiveLabel = QtWidgets.QLabel(self)
        self.LiveLabel.setText("Жизни:" + str(self.LivesCt))
        self.LiveLabel.adjustSize()
        self.LiveLabel.move(50,700)
        self.LiveLabel.hide()

        self.gameOverLabel = QtWidgets.QLabel(self)
        self.gameOverLabel.setText("ИГРА ОКОНЧЕНА")
        self.gameOverLabel.adjustSize()
        self.gameOverLabel.move(250,350)
        self.gameOverLabel.hide()

        self.timeoutMessage = QtWidgets.QLabel(self)
        self.timeoutMessage.setText("Время вышло")
        self.timeoutMessage.adjustSize()
        self.timeoutMessage.move(300, 450)
        self.timeoutMessage.hide()

        self.gameOverButtonMenu = QtWidgets.QPushButton(self)
        self.gameOverButtonMenu.setText("В меню")
        self.gameOverButtonMenu.adjustSize()
        self.gameOverButtonMenu.move(300, 400)
        self.gameOverButtonMenu.clicked.connect(self.gameOverHide)
        self.gameOverButtonMenu.hide()

        self.timerMessage = QtWidgets.QLabel(self)
        self.timerMessage.setText('Времени осталось:'+'300')
        self.timerMessage.adjustSize()
        self.timerMessage.move(400, 700)
        self.timerMessage.hide()

        self.gameOverTime = 300
        self.gameOverTimer = QTimer()
        self.gameOverTimer.timeout.connect(self.mainTimerTick)

        class Level:
            def __init__(self):
                self.timer = QTimer()
                self.timer.timeout.connect(self.update)
                self.objects = []

            def start(self):
                for obj in self.objects:
                    obj.show()
                self.timer.start(1)

            def pause(self):
                self.timer.stop()

            def resume(self):
                self.timer.start()

            def stop(self):
                self.timer.stop()
                for obj in self.objects:
                    obj.hide()

            def add_object(self, obj):
                self.objects.append(obj)

            def update(self):
                for obj in self.objects:
                    obj.move()

        class Platform:
            def __init__(self, playScene, row, fPos, speed, side, frog, isBorder):
                self.plat = playScene.addPixmap(QPixmap("platform.png").scaledToWidth(50).scaledToHeight(50))
                self.plat.setZValue(0)
                self.frog = frog
                self.isBorder = isBorder
                self.y = 50 + 50 * row
                self.fPos = fPos
                self.plat.setPos(-100, -100)
                self.x = fPos
                self.side = side
                self.speed = 10 - speed
                self.time_since_last_update = 0
                #game.add_object(self)

            def show(self):
                self.plat.setPos(self.fPos, self.y)
                self.plat.setZValue(209)

            def hide(self):
                self.plat.setPos(-100, -100)
                self.plat.setZValue(0)

            def move(self):
                self.time_since_last_update += 1
                if self.time_since_last_update >= self.speed:
                    self.time_since_last_update = 0
                    if self.x > 701:
                        self.x = -51
                    elif self.x < -51:
                        self.x = 701
                    self.x += self.side
                    self.plat.setPos(self.x, self.y)
                    if (not(self.frog.x() <= 0 and self.side < 0) and not(self.frog.x() >= 650 and self.side > 0)) and (self.plat in self.frog.collidingItems()):
                        self.frog.moveBy(self.side * self.isBorder, 0)

        class Car:
            def __init__(self, gameOver, playScene, frog, sprite, row, startPos, returnPos, endPos, speed):
                self.Car = playScene.addPixmap(QPixmap(sprite).scaledToHeight(50))
                self.y = 300 + 50 * row
                self.startPos = startPos
                self.Car.setPos(-100, -100)
                self.gO = gameOver
                self.frog = frog
                self.returnPos = returnPos
                self.endPos = endPos
                self.x = startPos
                self.speed = 10 - speed
                self.Car.setZValue(0)
                if startPos < endPos:
                    self.side = 1
                elif startPos == endPos:
                    self.side = 0
                else:self.side = -1
                self.time_since_last_update = 0
                #game.add_object(self)

            def show(self):
                self.Car.setPos(self.startPos, self.y)
                self.Car.setZValue(211)

            def hide(self):
                self.Car.setPos(-100, -100)
                self.Car.setZValue(0)

            def move(self):
                self.time_since_last_update += 1
                if self.time_since_last_update >= self.speed:
                    self.time_since_last_update = 0
                    if (self.side == 1 and self.x > self.endPos) or (self.side == -1 and self.x < self.endPos):
                        self.x = self.returnPos
                    else:
                        self.x += self.side
                    self.Car.setPos(self.x, self.y)
                    if self.Car in self.frog.collidingItems():
                        self.gO()

        self.LevelList = [Level(),Level(),Level(),Level()]

        self.fullObjList =[[
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, -150, -100, 700, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 100, -100, 700, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 350, -100, 700, 3),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, -160, -100, 700, 5),

            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 600, 700, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 100, 700, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 350, 700, -100, 3),

            Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 1, -160, -100, 700, 9),

            Platform(self.playScene, 4, 100, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 150, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 200, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 300, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 350, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 400, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 500, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 550, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 600, 4, -1, self.frog, 1),

            Platform(self.playScene, 3, 150, 2, 1, self.frog, 1),
            Platform(self.playScene, 3, 200, 2, 1, self.frog, 0),
            Platform(self.playScene, 3, 250, 2, 1, self.frog, 1),

            Platform(self.playScene, 3, 500, 2, 1, self.frog, 1),
            Platform(self.playScene, 3, 550, 2, 1, self.frog, 0),
            Platform(self.playScene, 3, 600, 2, 1, self.frog, 1),

            Platform(self.playScene, 2, 0, 0, 0, self.frog, 1),
            Platform(self.playScene, 2, 400, 0, 0, self.frog, 1),
            Platform(self.playScene, 2, 450, 0, 0, self.frog, 0),
            Platform(self.playScene, 2, 500, 0, 0, self.frog, 0),
            Platform(self.playScene, 2, 550, 0, 0, self.frog, 0),
            Platform(self.playScene, 2, 600, 0, 0, self.frog, 1),

            Platform(self.playScene, 1, 500, 5, -1, self.frog, 1),
            Platform(self.playScene, 1, 550, 5, -1, self.frog, 0),
            Platform(self.playScene, 1, 600, 5, -1, self.frog, 1),
            Platform(self.playScene, 1, 650, 5, -1, self.frog, 0),

            Platform(self.playScene, 0, 500, 2, -1, self.frog, 1),
            Platform(self.playScene, 0, 550, 2, -1, self.frog, 0),
            Platform(self.playScene, 0, 600, 2, -1, self.frog, 1),
        ],
            [
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 350, -100, 700, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 0, -100, 700, 3),

            Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 5, -160, -100, 700, 9),

            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 4, 350, 700, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 4, 0, 700, -100, 5),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 3, 160, 700, -100, 7),

            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 2, 350, -100, 700, 4),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 2, 0, -100, 700, 4),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 1, 160, -100, 700, 8),

            Platform(self.playScene, 4, 100, 4, 1, self.frog, 1),

            Platform(self.playScene, 3, 150, 4, -1, self.frog, 1),

            Platform(self.playScene, 2, 200, -10, 0, self.frog, 1),

            Platform(self.playScene, 1, 100, 1, 1, self.frog, 1),
            Platform(self.playScene, 1, 150, 1, 1, self.frog, 0),
            Platform(self.playScene, 1, 200, 1, 1, self.frog, 1),

            Platform(self.playScene, 0, 100, 6, -1, self.frog, 1),
            Platform(self.playScene, 0, 150, 6, -1, self.frog, 0),
            Platform(self.playScene, 0, 200, 6, -1, self.frog, 1),

        ],
            [
            Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 6, 350, -100, 350, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 450, -100, 450, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6,550, -100, 550, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 6, 650, -100, 650, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 150, -100, 150, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 6, 50, -100, 50, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 6, -50, -100, -50, 3),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 5, 200, -100, 200, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 5, 400, -100, 400, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 5, 500, -100, 500, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 5, 600, -100, 600, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 5, 100, -100, 100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 5, 0, -100, 0, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 5, -100, -100, -100, 3),

            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 4, 250, -100, 250, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 450, -100, 450, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 4, 550, -100, 550, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 4, 650, -100, 650, 3),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 150, -100, 150, 3),
            Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 4, 50, -100, 50, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 4, -50, -100, -50, 3),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 3, 500, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 3, 600, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 700, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 3, 250, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 3, 150, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 50, 750, -100, 3),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 3, -50, 750, -100, 3),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 2, 250, 750, -100, 8),
            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 2, 550, 750, -100, 8),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 1, 150, 750, -100, 9),

            Platform(self.playScene, 4, 300, 4, 0, self.frog, 1),
            Platform(self.playScene, 4, 350, 4, 0, self.frog, 1),

            Platform(self.playScene, 3, 300, 4, 0, self.frog, 1),
            Platform(self.playScene, 3, 350, 4, 0, self.frog, 1),

            Platform(self.playScene, 2, 300, 3, 1, self.frog, 1),
            Platform(self.playScene, 2, 350, 3, 1, self.frog, 1),

            Platform(self.playScene, 1, 300, 4, 0, self.frog, 1),
            Platform(self.playScene, 1, 350, 4, 0, self.frog, 1),

            Platform(self.playScene, 0, 300, 4, 0, self.frog, 1),
            Platform(self.playScene, 0, 350, 4, 0, self.frog, 1),

        ],
            [
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 6, 250, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 6, 350, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 6, 450, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 6, 650, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 6, 550, 750, -100, 5),

            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 5, 250, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 5, 350, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 5, 450, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 5, 550, 750, -100, 5),
            Car(self.gameOver, self.playScene, self.frog, "carLeft.png", 5, 650, 750, -100, 5),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 250, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 350, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 450, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 650, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, 550, -100, 750, 5),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, 250, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, 350, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, 450, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, 550, -100, 750, 5),
            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, 650, -100, 750, 5),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 2, 0, 750, -100, 8),
            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 2, 425, 750, -100, 8),

            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 1, 0, 750, -100, 8),
            Car(self.gameOver, self.playScene, self.frog, "carFastLeft.png", 1, 425, 750, -100, 8),

            Platform(self.playScene, 4, 100, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 150, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 200, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 300, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 350, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 400, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 500, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 550, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 600, 4, -1, self.frog, 1),

            Platform(self.playScene, 3, 150, 2, 1, self.frog, 1),
            Platform(self.playScene, 3, 200, 2, 1, self.frog, 0),
            Platform(self.playScene, 3, 250, 2, 1, self.frog, 1),

            Platform(self.playScene, 3, 500, 2, 1, self.frog, 1),
            Platform(self.playScene, 3, 550, 2, 1, self.frog, 0),
            Platform(self.playScene, 3, 600, 2, 1, self.frog, 1),

            Platform(self.playScene, 2, 0, 6, -1, self.frog, 1),


            Platform(self.playScene, 1, 500, 5, -1, self.frog, 1),
            Platform(self.playScene, 1, 550, 5, -1, self.frog, 0),
            Platform(self.playScene, 1, 600, 5, -1, self.frog, 1),
            Platform(self.playScene, 1, 650, 5, -1, self.frog, 0),

            Platform(self.playScene, 0, 500, 2, 1, self.frog, 1),
            Platform(self.playScene, 0, 550, 2, 1, self.frog, 0),
            Platform(self.playScene, 0, 600, 2, 1, self.frog, 1),
        ]
        ]
        for i in range(len(self.fullObjList)):
            for j in range(len(self.fullObjList[i])):
                self.LevelList[i].add_object(self.fullObjList[i][j])

        self.LevelList[0].start()

        self.levelNum = 0

        #self.displayMenu()
        self.frogAnTime = 100
        self.frogAnTimer = QTimer()
        self.frogAnTimer.timeout.connect(self.frogMove)
        self.frogIsX = True
        self.frogPlusOrMinus = 1

        self.frogDAnTime = 2
        self.frogDAnTimer = QTimer()
        self.frogDAnTimer.timeout.connect(self.deathAnimTimerTick)
        #self.frogDAnTimer.timeout.connect(self.frogDeAn)

        self.Timer = QTimer()
        self.Timer.timeout.connect(self.gameOverChk)
        self.Timer.start(100)

        self.viewPS = QGraphicsView(self.playScene,self)
        self.viewPS.setGeometry(0, 0, 700, 700)
        self.viewPS.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewPS.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewPS.setFocusPolicy(Qt.NoFocus)
        self.viewPS.hide()

        self.frogJumpPix = QPixmap("FrogAnim/tile004.png").scaledToHeight(50)
        self.facingSide = 0

        #здесь начинается стаф связанный с меню
        self.startButton = QtWidgets.QPushButton(self)
        self.startButton.setText("Начать")
        self.startButton.adjustSize()
        self.startButton.move(300, 300)
        self.startButton.clicked.connect(self.start)

        self.settingsButton = QtWidgets.QPushButton(self)
        self.settingsButton.setText("Настройки")
        self.settingsButton.adjustSize()
        self.settingsButton.move(290, 350)
        self.settingsButton.clicked.connect(self.settingshow)

        self.leaderBoardButton = QtWidgets.QPushButton(self)
        self.leaderBoardButton.setText("Таблица рекордов")
        self.leaderBoardButton.adjustSize()
        self.leaderBoardButton.move(255, 400)
        self.leaderBoardButton.clicked.connect(self.leaderBoardShow)

        self.guideButton = QtWidgets.QPushButton(self)
        self.guideButton.setText("Как играть")
        self.guideButton.adjustSize()
        self.guideButton.clicked.connect(self.howtoShow)
        self.guideButton.move(300, 450)

        self.exitButton = QtWidgets.QPushButton(self)
        self.exitButton.setText("Выход")
        self.exitButton.adjustSize()
        self.exitButton.move(300, 500)
        self.exitButton.clicked.connect(sys.exit)

        self.volumeslider = QSlider(self)
        self.volumeslider.setOrientation(Qt.Horizontal)
        self.volumeslider.setFocusPolicy(Qt.NoFocus)
        self.volumeslider.setValue(100)
        self.volumeslider.adjustSize()
        self.volumeslider.move(430,462)
        self.volumeslider.hide()

        self.volumeLabel = QLabel(self)
        self.volumeLabel.setText("Громкость музыки")
        self.volumeLabel.adjustSize()
        self.volumeLabel.move(200, 450)
        self.volumeLabel.hide()

        self.svolumslider = QSlider(self)
        self.svolumslider.setOrientation(Qt.Horizontal)
        self.svolumslider.setFocusPolicy(Qt.NoFocus)
        self.svolumslider.adjustSize()
        self.svolumslider.move(430, 562)
        self.svolumslider.hide()

        self.svolumeLabel = QLabel(self)
        self.svolumeLabel.setText("Громкость звука")
        self.svolumeLabel.adjustSize()
        self.svolumeLabel.move(200, 550)
        self.svolumeLabel.hide()

        try:
            with open("settings.txt") as settings:
                self.volumeslider.setValue(int(settings.readline()))
                self.svolumslider.setValue(int(settings.readline()))
        except IOError:
            print("IOError")


        self.BackToMenu = QPushButton(self)
        self.BackToMenu.setText("В меню")
        self.BackToMenu.adjustSize()
        self.BackToMenu.move(300, 300)
        self.BackToMenu.clicked.connect(self.settingsHide)
        self.BackToMenu.hide()

        text_edit = QPlainTextEdit()
        ...
        text = open('settings.txt').read()
        text_edit.setPlainText(text)

        #как играть
        self.howtoLabel = QLabel(self)
        self.howtoLabel.setText("Вы управляете лягушкой,\n перемещение осуществляется на клавиши WASD.\nВаша цель перейти дорогу и попасть на болото,\n избегая машин. При прыжке в воду вы тонете,\n но кувшинки защитят вас от этого.\n Ваше время и жизни ограничены.\n Удачи!")
        self.howtoLabel.adjustSize()
        self.howtoLabel.move(0, 400)
        self.howtoLabel.hide()

        #music starts here
        self.menuMusic = QMediaContent(QUrl.fromLocalFile("Sounds/menu.wav"))
        self.levelMusic = QMediaContent(QUrl.fromLocalFile("Sounds/level.wav"))

        self.musicPlayer = QMediaPlayer()
        self.volumeslider.valueChanged[int].connect(self.change_volume)
        self.musicPlayer.setMedia(self.menuMusic)
        self.musicPlayer.setVolume(self.volumeslider.value())
        self.unnecessaryTimer = QTimer()
        self.unnecessaryTimer.timeout.connect(self.iDontKnowHowToCorrectlyUseAudio)
        self.unnecessaryTimer.start(1000)

        #sound starts here
        carDSound = QMediaContent(QUrl.fromLocalFile("Sounds/carD.wav"))
        jumpSound = QMediaContent(QUrl.fromLocalFile("Sounds/jump.wav"))
        startSound = QMediaContent(QUrl.fromLocalFile("Sounds/start.wav"))
        timeSound = QMediaContent(QUrl.fromLocalFile("Sounds/time.wav"))

        self.carDsoundPlayer = QMediaPlayer()
        self.jumpsoundPlayer = QMediaPlayer()
        self.startsoundPlayer = QMediaPlayer()
        self.timeDsoundPlayer = QMediaPlayer()

        self.carDsoundPlayer.setVolume(self.svolumslider.value())
        self.jumpsoundPlayer.setVolume(self.svolumslider.value())
        self.startsoundPlayer.setVolume(self.svolumslider.value())
        self.timeDsoundPlayer.setVolume(self.svolumslider.value())

        self.carDsoundPlayer.setMedia(carDSound)
        self.jumpsoundPlayer.setMedia(jumpSound)
        self.startsoundPlayer.setMedia(startSound)
        self.timeDsoundPlayer.setMedia(timeSound)

        self.volumeslider.valueChanged[int].connect(self.change_volume)

        self.iDontKnowHowToCorrectlyUseAudio()

        #winScreen
        self.score = 0

        self.WinMessage = QLabel(self)
        self.WinMessage.setText("Поздравляю вы прошли игру!")
        self.WinMessage.adjustSize()
        self.WinMessage.move(250, 200)
        self.WinMessage.hide()

        self.scoreMessage = QLabel(self)
        self.scoreMessage.setText("Счёт:")
        self.scoreMessage.adjustSize()
        self.scoreMessage.move(100, 400)
        self.scoreMessage.hide()

        self.finalButton = QPushButton(self)
        self.finalButton.setText("В меню")
        self.finalButton.adjustSize()
        self.finalButton.move(100, 100)
        self.finalButton.hide()
        self.finalButton.clicked.connect(self.finalHide)

        self.leaderBoardTable = QTableWidget(self)
        self.leaderBoardTable.move(50,50)
        self.leaderBoardTable.setFixedSize(500,650)
        self.leaderBoardTable.hide()

        self.BackToMenu1 = QPushButton(self)
        self.BackToMenu1.move(0,0)
        self.BackToMenu1.setFixedSize(200,50)
        self.BackToMenu1.hide()
        self.BackToMenu1.setText("Назад в меню")
        self.BackToMenu1.clicked.connect(self.settingsHide)

        self.techStop = False
        self.viewPS.show()


    def leaderBoardShow(self):
        self.BackToMenu1.show()
        self.menuhide()
        self.viewPS.hide()
        try:
            with open("Scores.txt", "r") as base:
                scores = list(base.readlines())

            self.leaderBoardTable.setRowCount(len(scores))
            self.leaderBoardTable.setColumnCount(1)
            self.leaderBoardTable.setColumnWidth(0,350)

            for i, row in enumerate(scores):
                for j, col in enumerate(row):
                    self.leaderBoardTable.setItem(i, j, QTableWidgetItem(row))

            self.leaderBoardTable.setStyleSheet("background-color: black; color:white; font-size: 25px")
            self.leaderBoardTable.horizontalHeader().hide()
            self.leaderBoardTable.verticalHeader().setStyleSheet('color: black')
            self.leaderBoardTable.show()
        except IOError:
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Critical)
            mb.setText("Ошибка: IOError")
            mb.setWindowTitle("IOError")
            mb.exec_()

    def settingshow(self):
        self.viewPS.hide()
        self.menuhide()
        self.volumeLabel.showNormal()
        self.svolumeLabel.showNormal()
        self.volumeslider.showNormal()
        self.svolumslider.showNormal()
        self.BackToMenu.showNormal()

    def settingsHide(self):
        self.BackToMenu1.hide()
        self.howtoLabel.hide()
        self.menuhide()
        self.volumeLabel.hide()
        self.svolumeLabel.hide()
        self.volumeslider.hide()
        self.svolumslider.hide()
        self.BackToMenu.hide()
        self.leaderBoardTable.hide()
        self.viewPS.show()
        self.menushow()

    def schange_volume(self, value):
        self.timeDsoundPlayer.setVolume(value)
        self.startsoundPlayer.setVolume(value)
        self.carDsoundPlayer.setVolume(value)
        self.jumpsoundPlayer.setVolume(value)

    def change_volume(self, value):
        self.musicPlayer.setVolume(value)

    def deathAnimTimerTick(self):
        if self.frogDAnTime == 1: self.frog.setPixmap(QPixmap())
        if self.frogDAnTime == 0:
            self.frog.setPos(0, 650)
            self.frogDAnTime = 2
            self.frog.setPixmap(self.frogPix)
            self.frogDAnTimer.stop()
            self.playFieldActive = False
            return
        self.frogDAnTime-=1

    def timerReset(self):
        self.gameOverTimer.stop()
        self.gameOverTime = 300
        self.gameOverTimer.start(1000)


    def final(self):
        self.Timer.stop()
        self.viewPS.hide()
        self.score+=self.LivesCt*100
        self.WinMessage.show()
        self.scoreMessage.setText("Счёт:"+str(self.score))
        self.addRec()
        self.LiveLabel.hide()
        self.timerMessage.hide()
        self.scoreMessage.adjustSize()
        self.scoreMessage.show()
        self.finalButton.show()
        self.gameOverTimer.stop()

    def finalHide(self):
        self.LivesCt = 5
        self.playFieldActive = True
        self.LevelList[0].start()
        self.frog.setPos(0,650)
        self.scoreMessage.hide()
        self.WinMessage.hide()
        self.finalButton.hide()
        self.menushow()
        self.gameOverTimer.stop()

    def menuhide(self):
        self.startButton.hide()
        self.leaderBoardButton.hide()
        self.settingsButton.hide()
        self.exitButton.hide()
        self.guideButton.hide()

    def howtoShow(self):
        self.viewPS.hide()
        self.BackToMenu.show()
        self.howtoLabel.show()
        self.menuhide()

    def gameOverHide(self):
        self.gameOverLabel.hide()
        self.gameOverButtonMenu.hide()
        self.timeoutMessage.hide()
        self.menushow()

    def menushow(self):
        self.viewPS.show()
        self.startButton.show()
        self.leaderBoardButton.show()
        self.settingsButton.show()
        self.exitButton.show()
        self.guideButton.show()

    def start(self):
        self.Timer.start()
        self.musicPlayer.setMedia(self.levelMusic)
        self.menuhide()
        self.timerReset()
        self.LiveLabel.show()
        self.timerMessage.show()
        self.playFieldActive = False
        self.levelSwitch()

    def updateLives(self):
        self.LiveLabel.setText("Жизни:" + str(self.LivesCt))
        self.LiveLabel.adjustSize()

    def iDontKnowHowToCorrectlyUseAudio(self):
        if self.musicPlayer.state() ==0: self.musicPlayer.play()

    def mainTimerTick(self):
        if self.gameOverTime == 30:
            self.timeDsoundPlayer.play()
        if self.gameOverTime <= 0:
            self.gameOverTimer.stop()
            self.fullGameOver(True)
        else:
            self.gameOverTime -=1
            self.timerMessage.setText('Времени осталось:' + str(self.gameOverTime))

    def gameOverChk(self): #Функция проверяющая смерть от воды и победу
        if self.grass in self.frog.collidingItems() and self.techGrass in self.frog.collidingItems():
            self.score += self.gameOverTime*10
            self.techStop = True
            self.LevelList[self.levelNum].stop()
            self.levelNum+=1
            self.LivesCt+=2
            if self.levelNum < len(self.LevelList):
                self.levelSwitch()
            else:self.final()
            return
        if (len(self.frog.collidingItems()) < 3) and (self.river in self.frog.collidingItems()) and not(self.techGrass in self.frog.collidingItems()):
            self.gameOver()


    def levelSwitch(self, isGameOver = False):
        if self.levelNum == len(self.LevelList): self.levelNum=0
        self.LevelList[self.levelNum].start()
        self.updateLives()
        self.timerReset()
        if not isGameOver:self.startsoundPlayer.play()
        self.frog.setPos(0, 650)

    def gameOver(self): #trigger if player die
        if not (self.playFieldActive):
            self.carDsoundPlayer.play()
            self.LivesCt-=1
            self.updateLives()
            self.frogAnTimer.stop()
            self.playFieldActive = True
            self.frog.setPixmap(self.deathPix)
            self.frogDAnTimer.start(500)
            if self.LivesCt <= 0:
                self.fullGameOver()

    def gameReset(self):
        self.timerReset()
        self.LivesCt = 5
        self.LevelList[self.levelNum].stop()
        self.levelNum = 0
        self.levelSwitch(True)

    def fullGameOver(self, isTimeout=False): #trigger if lives=0
        self.gameOverTimer.stop()
        self.timerMessage.hide()
        self.LiveLabel.hide()
        self.viewPS.hide()
        self.gameReset()
        self.frogDAnTimer.stop()
        self.frogDAnTime = 2
        self.frog.setPixmap(self.frogPix)
        self.gameOverButtonMenu.show()
        self.gameOverLabel.show()
        self.playFieldActive = True
        if isTimeout:
            self.timeoutMessage.show()

    def keyPressEvent(self, e):
        if self.playFieldActive or self.frogAnTimer.isActive():
            return
        if e.key() == Qt.Key_D or e.key() == 1042:
            self.facingSide = 270
            self.frogPlusOrMinus = 1
            self.frogIsX = True
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
        if e.key() == Qt.Key_A or e.key() == 1060:
            self.facingSide = 90
            self.frogPlusOrMinus = -1
            self.frogIsX = True
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
        if e.key() == Qt.Key_W or e.key() == 1062:
            self.facingSide = 180
            self.frogPlusOrMinus = -1
            self.frogIsX = False
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
        if e.key() == Qt.Key_S or e.key() == 1067:
            self.facingSide = 0
            self.frogPlusOrMinus = 1
            self.frogIsX = False
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)

    def frogMove(self):
        if self.techStop or self.frogAnTime <= 0 or ((self.frog.x() + self.frogPlusOrMinus * 50 >= 700 or self.frog.x() + self.frogPlusOrMinus * 50 <= -50) and self.frogIsX) or ((self.frog.y() + self.frogPlusOrMinus * 50 >= 700) and not(self.frogIsX)):
            self.frog.setPixmap(self.frogPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTime = 100
            self.frogAnTimer.stop()
            self.techStop = False
            return
        if self.frogIsX:
            self.frog.moveBy(self.frogPlusOrMinus*0.5, 0)
        else:
            self.frog.moveBy(0, self.frogPlusOrMinus*0.5)
        self.frogAnTime-=1

    def fillLine(self,texture,y,z):
        for i in range(14):
            img = self.playScene.addPixmap(texture)
            img.setPos(50*i,y)
            img.setZValue(z)

    def clearLeaderBoard(self):
        try:
            with open("leaderboard.txt", "w") as base:
                base.write("")
                return False
        except IOError:
            return True

    def addRec(self):
        try:
            with open("leaderboard.txt", "a") as base:
                base.write(str(self.score) + "\n")

            self.sortRecs()
        except IOError:
            return True

    def sortRecs(self):
        try:
            with open("leaderboard.txt", "r") as base:
                scoreSorted = base.readlines()
            for line in scoreSorted:
                line.replace("\n", "")
            scoreSorted = list(map(int, scoreSorted))
            scoreSorted.sort()
            scoreSorted.reverse()
            with open("Scores.txt", "w") as base:
                for i in range(len(scoreSorted)):
                    base.write(str(scoreSorted[i]) + "\n")

            return False
        except IOError:
            return True

    def closeEvent(self, event):
        try:
            with open("settings.txt","w") as settings:
                settings.write(str(self.volumeslider.value()) + "\n" + str(self.svolumslider.value()))
        except IOError:
            print("IOError")
        event.accept()


def application():
    app = QApplication(sys.argv)
    Wind = Wind1()

    Wind.show()
    #Wind.viewPS.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    application()