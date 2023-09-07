from PyQt5 import QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QPixmap, QMovie, QTransform
from PyQt5.QtCore import Qt, QTimer, QUrl, QRunnable, pyqtSlot, QThreadPool, QThread, pyqtSignal
import sys
import time


class Wind1(QMainWindow):
    def __init__(self):
        super(Wind1, self).__init__()
        self.setWindowTitle("Frogger")
        self.setGeometry(0,0,700,800)
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

        self.river = QtWidgets.QGraphicsRectItem(0, 0, 699, 249)
        self.river.setBrush(QBrush(Qt.darkBlue))
        self.river.setPos(0, 51)
        self.river.setZValue(101)
        self.playScene.addItem(self.river)

        '''
        self.railRoad = QPixmap("railroad.png")
        self.fillLine(self.railRoad, 300, 102)
        self.fillLine(self.railRoad, 350, 102)
        '''

        self.frogPix = QPixmap("FrogAnim/tile000.png").scaledToWidth(50).scaledToHeight(50)
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

        self.gameOverButtonMenu = QtWidgets.QPushButton(self)
        self.gameOverButtonMenu.setText("В меню")
        self.gameOverButtonMenu.adjustSize()
        self.gameOverButtonMenu.move(300, 400)
        self.gameOverButtonMenu.hide()

        self.timeoutMessage = QtWidgets.QLabel(self)
        self.timeoutMessage.setText("Время вышло")
        self.timeoutMessage.adjustSize()
        self.timeoutMessage.move(300, 450)
        self.timeoutMessage.hide()

        self.timerMessage = QtWidgets.QLabel(self)
        self.timerMessage.setText('Времени осталось:'+'300')
        self.timerMessage.adjustSize()
        self.timerMessage.move(400, 700)
        self.timerMessage.hide()

        self.jumpTimer = QTimer()
        self.jumpTimer.timeout.connect(self.frogMove)

        self.gameOverTime = 300
        self.gameOverTimer = QTimer()
        self.gameOverTimer.timeout.connect(self.mainTimerTick)


        self.shift = 0
        self.jumpCt = 0
        class Platform:
            def __init__(self,playScene,row, fPos, speed, side, frog, isBorder):
                self.plat = playScene.addPixmap(QPixmap("platform.png").scaledToWidth(50).scaledToHeight(50))
                self.plat.setZValue(0)
                self.frog = frog
                self.isBorder = isBorder
                self.y =50+50*row
                self.fPos = fPos
                self.plat.setPos(-100,-100)
                self.x = fPos
                self.side =side
                self.speed = speed
                self.Timer = QTimer()
                self.Timer.timeout.connect(lambda: self.move1())

            def start(self):
                self.plat.setPos(self.fPos, self.y)
                self.plat.setZValue(209)
                self.Timer.start(30-self.speed*3)

            def pause(self):
                self.Timer.stop()

            def resume(self):
                self.Timer.start(30 - self.speed*3)

            def stop(self):
                self.Timer.stop()
                self.plat.setPos(-100,-100)
                self.plat.setZValue(0)

            def move1(self):
                if self.x > 701: self.x=-51
                elif self.x < -51: self.x=701
                self.x+=self.side*3
                self.plat.setPos(self.x,self.y)
                if self.frog.x() >=0 and self.frog.x() <=650 and self.plat in self.frog.collidingItems(): self.frog.moveBy(self.side*self.isBorder*3,0)

        self.threadpool = QThreadPool()

        class Car1(QThread):
            def __init__(self, gameOver, playScene, frog, sprite, row, startPos, returnPos, endPos, speed):
                super().__init__()
                self.Car = playScene.addPixmap(QPixmap(sprite).scaledToHeight(50))
                self.y = 300 + 50 * row
                self.startPos = startPos
                self.Car.setPos(-100, -100)
                self.gO = gameOver
                self.frog = frog
                self.returnPos = returnPos
                self.endPos = endPos
                self.x = startPos
                self.speed = speed
                self.Car.setZValue(0)
                print("carCreated")

                if startPos < endPos:
                    self.side = 1
                else:
                    self.side = -1

            def run(self):
                sleep_time = (50 - self.speed * 5)
                print("carStartedToMove")
                self.Car.setPos(self.startPos, self.y)
                self.Car.setZValue(211)
                while True:
                    if (self.side == 1 and self.x > self.endPos) or (self.side == -1 and self.x < self.endPos):
                        self.x = self.returnPos
                    else:
                        self.x += self.side * 10
                    self.Car.setPos(self.x, self.y)
                    if self.Car in self.frog.collidingItems():
                        self.gO()
                    QThread.msleep(sleep_time)
                print("carStoped")



            def stop(self):
                self.Car.setZValue(1)
                self.Car.setPos(-100, -100)
                self.quit()
                self.wait()

        car = Car1(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 2, -100, -50, 700, 0)
        car.start()


        self.fieldUpdater = QTimer()
        self.fieldUpdater.timeout.connect(self.fieldUpdate)
        self.fieldUpdater.start(1)
        class Car:
            def __init__(self, gameOver, playScene, frog, sprite, row, startPos, returnPos, endPos, speed):
                self.Car = playScene.addPixmap(QPixmap(sprite).scaledToHeight(50))
                self.y=300+50*row
                self.startPos = startPos
                self.Car.setPos(-100, -100)
                self.gO = gameOver
                self.frog=frog
                self.returnPos=returnPos
                self.endPos = endPos
                self.x =startPos
                self.speed = speed
                self.Car.setZValue(0)
                if startPos < endPos: self.side = 1
                else:self.side=-1


            def start(self):
                self.Car.setPos(self.startPos, self.y)
                self.Car.setZValue(211)
                self.Timer = QTimer()
                self.Timer.timeout.connect(self.carMove)
                self.Timer.start(20-self.speed*2)

            def pause(self):
                self.Timer.stop()

            def resume(self):
                self.Timer.start(20-self.speed*2)

            def stop(self):
                self.Car.setZValue(1)
                self.Car.setPos(-100,-100)
                self.Timer.stop()
                self.Car.setPos(-100,-100)

            def carMove(self):

                if (self.side==1 and self.x>self.endPos)or(self.side==-1 and self.x<self.endPos):
                    self.x=self.returnPos
                else:self.x+=self.side*2
                self.Car.setPos(self.x,self.y)
                if self.Car in self.frog.collidingItems():
                    self.gO()


        class Bird:
            def __init__(self, gameOver, playScene, frog, row, startY, speed):
                self.bbb = playScene.addPixmap(QPixmap("Bird.png").scaledToHeight(50))
                self.x = row * 50
                self.frog = frog
                self.y = startY
                self.bbb.setZValue(250)
                self.speed=speed
                self.gameOver = gameOver
                self.timer = QTimer();
                self.timer.timeout.connect(self.move)
            def start(self):

                self.timer.start(10-self.speed)

            def pause(self):
                self.Timer.stop()

            def resume(self):
                self.Timer.start(10 - self.speed)

            def stop(self):
                self.timer.stop()
                self.bbb.setPos(-100,-100)

            def move(self):
                if self.bbb.y() > 710:
                    self.bbb.setPos(self.x,-60)
                else: self.bbb.setPos(self.x,self.bbb.y()+2)
                if self.bbb in self.frog.collidingItems(): self.gameOver()



        self.menuBackground = []

        # self.testLevel = [
        #     Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 2, -100, -50, 700, 0),
        #     Car(self.gameOver, self.playScene, self.frog, "carRight.png", 3, -160, -50, 700, 5),
        #     Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 4, -220, -50, 700, 9),
        #     Car(self.gameOver, self.playScene, self.frog, "carFast.png", 1, -50, -50, 700, 5),
        #     Car(self.gameOver, self.playScene, self.frog, "carFast.png", 1, -100, -50, 700, 5),
        #     Car(self.gameOver, self.playScene, self.frog, "carFast.png", 1, -150, -50, 700, 5),
        #     Car(self.gameOver, self.playScene, self.frog, "carFast.png", 1, -200, -50, 700, 5),
        #     #Bird(self.gameOver, self.playScene, self.frog,7,0,5),
        #     Platform(self.playScene, 4, 100, 3, -1, self.frog,1),
        #     Platform(self.playScene, 4, 150, 3, -1, self.frog,0),
        #     Platform(self.playScene, 4, 200, 3, -1, self.frog,1),
        #     Platform(self.playScene, 3, 200, 2, 1, self.frog,1),
        #     Platform(self.playScene, 3, 250, 2, 1, self.frog,0),
        #     Platform(self.playScene, 3, 300, 2, 1, self.frog,1),
        #     Platform(self.playScene, 2, 100, 3, -1, self.frog,1),
        #     Platform(self.playScene, 2, 150, 3, -1, self.frog,0),
        #     Platform(self.playScene, 2, 200, 3, -1, self.frog,1),
        #     Platform(self.playScene, 1, 100, 3, -1, self.frog,1),
        #     Platform(self.playScene, 1, 150, 3, -1, self.frog,0),
        #     Platform(self.playScene, 1, 200, 3, -1, self.frog,1),
        #     Platform(self.playScene, 0, 400, 2, -1, self.frog,1),
        #     Platform(self.playScene, 0, 350, 2, -1, self.frog,0),
        #     Platform(self.playScene, 0, 300, 2, -1, self.frog,1)
        # ]



        """self.fullObjList =[[
            Car1(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, -150, -50, 700, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 100, -50, 700, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowRight.png", 6, 350, -50, 700, 3),

            Car(self.gameOver, self.playScene, self.frog, "carRight.png", 4, -160, -50, 700, 5),

            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 600, 700, -50, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 100, 700, -50, 3),
            Car(self.gameOver, self.playScene, self.frog, "carSlowLeft.png", 3, 350, 700, -50, 3),

            Car(self.gameOver, self.playScene, self.frog, "carFastRight.png", 1, -160, -50, 700, 9),

            Platform(self.playScene, 4, 100, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 150, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 200, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 300, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 350, 4, -1, self.frog, 0),
            Platform(self.playScene, 4, 400, 4, -1, self.frog, 1),

            Platform(self.playScene, 4, 500, 4, -1, self.frog, 1),
            Platform(self.playScene, 4, 550, 4, -1, self.frog, 0),
            #Platform(self.playScene, 4, 600, 4, -1, self.frog, 1),


        ]]"""

        self.levelNum = 0

        #self.displayMenu()
        self.frogAnTime = 200
        self.frogAnTimer = QTimer()
        self.frogAnTimer.timeout.connect(self.frogMove)
        self.frogIsX = True
        self.frogPlusOrMinus = 1

        self.Timer = QTimer()
        self.Timer.timeout.connect(self.gameOverChk)
        self.Timer.start(5)

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

        self.guideButton = QtWidgets.QPushButton(self)
        self.guideButton.setText("Как играть")
        self.guideButton.adjustSize()
        self.guideButton.move(300, 450)

        self.exitButton = QtWidgets.QPushButton(self)
        self.exitButton.setText("Выход")
        self.exitButton.adjustSize()
        self.exitButton.move(300, 500)
        self.exitButton.clicked.connect(sys.exit)


        '''self.menuLayout = QVBoxLayout()
        self.menuLayout.addWidget(self.startButton)
        self.menuLayout.addWidget(self.settingsButton)
        self.menuLayout.addWidget(self.leaderBoardButton)
        self.menuLayout.addWidget(self.guideButton)
        self.menuLayout.addWidget(self.exitButton)
        
        self.setLayout(self.menuLayout)
'''
        #settings
        self.settingsLayout = QGridLayout()

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
        self.svolumslider.setValue(100)
        self.svolumslider.adjustSize()
        self.svolumslider.move(430, 562)
        self.svolumslider.hide()

        self.svolumeLabel = QLabel(self)
        self.svolumeLabel.setText("Громкость звука")
        self.svolumeLabel.adjustSize()
        self.svolumeLabel.move(200, 550)
        self.svolumeLabel.hide()

        self.BackToMenu = QPushButton(self)
        self.BackToMenu.setText("В меню")
        self.BackToMenu.adjustSize()
        self.BackToMenu.move(300, 300)
        self.BackToMenu.clicked.connect(self.settingsHide)
        self.BackToMenu.hide()

        #howto


        #music starts here
        self.menuMusic = QMediaContent(QUrl.fromLocalFile("Sounds/menu.wav"))
        self.levelMusic = QMediaContent(QUrl.fromLocalFile("Sounds/level.wav"))

        self.musicPlayer = QMediaPlayer()
        self.volumeslider.valueChanged[int].connect(self.change_volume)
        self.musicPlayer.setMedia(self.menuMusic)
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

        self.carDsoundPlayer.setMedia(carDSound)
        self.jumpsoundPlayer.setMedia(jumpSound)
        self.startsoundPlayer.setMedia(startSound)
        self.timeDsoundPlayer.setMedia(timeSound)

        self.svolumslider.valueChanged[int].connect(self.schange_volume)

        self.iDontKnowHowToCorrectlyUseAudio()

        self.viewPS.show()

    def fieldUpdate(self):
        self.grass.setPos(self.grass.pos())

    def settingshow(self):
        self.menuhide()
        self.volumeLabel.showNormal()
        self.svolumeLabel.showNormal()
        self.volumeslider.showNormal()
        self.svolumslider.showNormal()
        self.BackToMenu.showNormal()

    def settingsHide(self):
        self.menuhide()
        self.volumeLabel.hide()
        self.svolumeLabel.hide()
        self.volumeslider.hide()
        self.svolumslider.hide()
        self.BackToMenu.hide()
        self.menushow()

    def schange_volume(self, value):
        self.timeDsoundPlayer.setVolume(value)
        self.startsoundPlayer.setVolume(value)
        self.carDsoundPlayer.setVolume(value)
        self.jumpsoundPlayer.setVolume(value)
    def change_volume(self, value):
        self.musicPlayer.setVolume(value)

    def timerReset(self):
        self.gameOverTimer.stop()
        self.gameOverTime = 300
        self.gameOverTimer.start(1000)
    def menuhide(self):
        self.startButton.hide()
        self.leaderBoardButton.hide()
        self.settingsButton.hide()
        self.exitButton.hide()
        self.guideButton.hide()

    def menushow(self):
        self.startButton.show()
        self.leaderBoardButton.show()
        self.settingsButton.show()
        self.exitButton.show()
        self.guideButton.show()

    def guideShow(self):
        self.menuhide()
        self.viewPS.hide()

    def start(self):
        self.musicPlayer.setMedia(self.levelMusic)
        self.menuhide()
        self.timerReset()
        self.LiveLabel.show()
        self.timerMessage.show()
        self.playFieldActive = False
        self.levelSwitch(0)
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
            self.fullGameOver()
        else:
            self.gameOverTime -=1
            self.timerMessage.setText('Времени осталось:' + str(self.gameOverTime))

    def gameOverChk(self):
        if self.river in self.frog.collidingItems() and len(self.frog.collidingItems()) == 2:self.gameOver()
        if self.grass in self.frog.collidingItems() and len(self.frog.collidingItems()) == 1:
            for item in self.fullObjList[self.levelNum]: item.stop()
            self.levelNum+=1
            self.levelSwitch(self.levelNum)


    def gameCycle(self):
        print("!")

    def levelSwitch(self,lvNm):
        self.startsoundPlayer.play()
        self.frog.setPos(0, 650)
        #for item in self.fullObjList[lvNm]: item.start()

    def gameOver(self): #trigger if player die
        self.carDsoundPlayer.play()
        self.frogAnTime=0
        self.LivesCt-=1
        self.updateLives()
        self.frog.setPos(0,650)
        print(self.LivesCt)
        if self.LivesCt <= 0:
            self.fullGameOver()


    def fullGameOver(self, isTimeout=False): #trigger if lives=0
        self.playFieldActive = True
        self.viewPS.hide()
        self.gameOverButtonMenu.show()
        self.gameOverLabel.show()
        if isTimeout:
            print("test5")
            self.timeoutMessage.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            print(self.playFieldActive)
        if self.playFieldActive or self.frogAnTimer.isActive(): return
        if e.key() == Qt.Key_D:
            self.facingSide = 270
            self.frogPlusOrMinus = 1
            self.frogIsX = True
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
            #print("R")
        if e.key() == Qt.Key_A:
            self.facingSide = 90
            self.frogPlusOrMinus = -1
            self.frogIsX = True
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
            #print("L")
        if e.key() == Qt.Key_W:
            self.facingSide = 180
            self.frogPlusOrMinus = -1
            self.frogIsX = False
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
            #print("U")
        if e.key() == Qt.Key_S:
            self.facingSide = 0
            self.frogPlusOrMinus = 1
            self.frogIsX = False
            self.frog.setPixmap(self.frogJumpPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTimer.start(1)
            #print("D")

    def frogMove(self):
        if self.frogAnTime <= 0 or ((self.frog.x() + self.frogPlusOrMinus * 50 >= 700 or self.frog.x() + self.frogPlusOrMinus * 50 <= -50) and self.frogIsX) or ((self.frog.y() + self.frogPlusOrMinus * 50 >= 700 or self.frog.y() + self.frogPlusOrMinus * 50 <= 0) and not(self.frogIsX)):
            print("anim stop")
            self.frog.setPixmap(self.frogPix.transformed(QTransform().rotate(self.facingSide)))
            self.frogAnTime = 200
            self.frogAnTimer.stop()
            return
        if self.frogIsX:
            self.frog.moveBy(self.frogPlusOrMinus*0.25, 0)
        else:
            self.frog.moveBy(0, self.frogPlusOrMinus*0.25)
        self.frogAnTime-=1

    def frogJump(self, x, y): #НЕ ИСПОЛЬЗУЕТСЯ
        if self.frog.x() + x >= 700.0 or self.frog.x() +x < 0.0 or self.frog.y() +y < 0.0 or self.frog.y() +y >=700.0:
            print("bad move")
        else: self.frog.moveBy(x,y)
        self.gameOverChk()
        print(self.frog.x(),self.frog.y())

    def fillLine(self,texture,y,z):
        for i in range(14):
            img = self.playScene.addPixmap(texture)
            img.setPos(50*i,y)
            img.setZValue(z)





def application():
    app = QApplication(sys.argv)
    Wind = Wind1()

    Wind.show()
    #Wind.viewPS.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    application()