from operator import truediv
import sys
import subprocess
import os

from tkinter import OFF, Scrollbar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
    QPushButton
)
from moderator_ui import Ui_MainWindow

#Define variables
config = {
    'user':'ehawuser2', 
    'password':'eHaW$user2', 
    'host':'127.0.0.1', 
    'database':'ehaw'
}


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.actMsgId = 0
        self.loadInitialData()
        self.pb_ActMsgAccept.clicked.connect(self.AcceptMsg)
        self.pb_ActMsgDecline.clicked.connect(self.DeclineMsg)
        self.pb_ActMsgIgnore.clicked.connect(self.IgnoreMsg)

    def loadInitialData(self):
        self.loadWinlinkConfig()
        self.loadEventMetadata()
        self.loadOpenMessageQueue()
        self.loadActiveMessage()
        self.loadMessageQueue()
        
        #Load Winlink configuration
    def loadWinlinkConfig(self):
        ehawCfg = QSqlQuery("SELECT cfgId, cfgWinlinkExePath, cfgOutPath, cfgSentPath FROM ehaw.ehawconfig")
        while ehawCfg.next():
            self.le_WinlinkExecPath.setText(ehawCfg.value(1))
            self.le_WinlinkOutPath.setText(ehawCfg.value(2))
            self.le_WinlinkSentPath.setText(ehawCfg.value(3))

        #Load Event Configuration
    def loadEventMetadata(self):
        self.tw_EventConfig.setAlternatingRowColors(1)
        self.tw_EventConfig.setColumnCount(4)
        self.tw_EventConfig.setHorizontalHeaderLabels(["Event Id", "Operator Call", "Winlink Call", "Event Location / Description"])
        ehawEvents = QSqlQuery("SELECT eventId, eventOperatorCallsign, eventWinlinkCallsign, eventLocation FROM ehaw.eventMetadata")
        while ehawEvents.next():
            rows = self.tw_EventConfig.rowCount()
            self.tw_EventConfig.setRowCount(rows + 1)
            self.tw_EventConfig.setItem(rows, 0, QTableWidgetItem(str(ehawEvents.value(0))))
            self.tw_EventConfig.setItem(rows, 1, QTableWidgetItem(ehawEvents.value(1)))
            self.tw_EventConfig.setItem(rows, 2, QTableWidgetItem(ehawEvents.value(2)))
            self.tw_EventConfig.setItem(rows, 3, QTableWidgetItem(ehawEvents.value(3)))
        self.tw_EventConfig.resizeColumnToContents(0)
        self.tw_EventConfig.resizeColumnToContents(1)
        self.tw_EventConfig.resizeColumnToContents(2)
        self.tw_EventConfig.horizontalHeader().setStretchLastSection(True)
        self.tw_EventConfig.resizeColumnsToContents()

        #Load Open Message Queue
    def loadOpenMessageQueue(self):
        self.tw_OpenMsgQueue.setAlternatingRowColors(1)
        self.tw_OpenMsgQueue.setColumnCount(5)
        self.tw_OpenMsgQueue.setHorizontalHeaderLabels(["Msg Id", "From", "To", "Message", "Created"])
        openMsgs = QSqlQuery("SELECT msgId, msgFrom, msgTo, msgText, msgCreate FROM ehaw.openMsgQueue")
        rows = -1
        while openMsgs.next():
            rows = self.tw_OpenMsgQueue.rowCount()
            self.tw_OpenMsgQueue.setRowCount(rows + 1)
            self.tw_OpenMsgQueue.setItem(rows, 0, QTableWidgetItem(str(openMsgs.value(0))))
            self.tw_OpenMsgQueue.setItem(rows, 1, QTableWidgetItem(openMsgs.value(1)))
            self.tw_OpenMsgQueue.setItem(rows, 2, QTableWidgetItem(openMsgs.value(2)))
            self.tw_OpenMsgQueue.setItem(rows, 3, QTableWidgetItem(openMsgs.value(3)))
            self.tw_OpenMsgQueue.setItem(rows, 4, QTableWidgetItem(openMsgs.value(4)))
            if rows == 0:
                self.actMsgId = openMsgs.value(0)
        #Make each cell in each row read only
        for i in range(rows):
            for j in range(5):
                cell_item = QTableWidgetItem()
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)
        tableWidth = self.tw_OpenMsgQueue.width()
        self.tw_OpenMsgQueue.resizeColumnToContents(0)
        self.tw_OpenMsgQueue.resizeColumnToContents(1)
        self.tw_OpenMsgQueue.resizeColumnToContents(2)
        self.tw_OpenMsgQueue.setColumnWidth(3, int(tableWidth * 0.7))
        self.tw_OpenMsgQueue.horizontalHeader().setStretchLastSection(True)
        self.tw_OpenMsgQueue.selectRow(0)

        #Retrieve Active Message
    def loadActiveMessage(self):
        if self.actMsgId > 0:
            qString = "SELECT msgId, msgSubject, msgTo, msgBody FROM ehaw.buildMsg WHERE msgId = " + str(self.actMsgId)
            actMsg = QSqlQuery(qString)
            actMsg.next()
            self.le_ActMsgId.setText(str(actMsg.value(0)))
            self.le_ActSubject.setText(actMsg.value(1))
            self.le_ActTo.setText(actMsg.value(2))
            self.tb_ActiveMessage.setText(actMsg.value(3))
        else:
            self.le_ActMsgId.clear()
            self.le_ActSubject.clear()
            self.le_ActTo.clear()
            self.tb_ActiveMessage.clear()

        #Load Message Queue
    def loadMessageQueue(self):
        #first update any messages that were sent
        self.updateSentMsgStatus()
        #and then get on with it
        self.tw_MsgQueue.setAlternatingRowColors(1)
        self.tw_MsgQueue.setColumnCount(7)
        self.tw_MsgQueue.setHorizontalHeaderLabels(["Msg Id","Status","From","Message","Updated","Created","Winlink Id"])
        msgQueue = QSqlQuery("SELECT msgId, msgStatus, msgFrom, msgText, msgUpdate, msgCreate, msgWinlinkId FROM ehaw.userMsgQueue")
        rows = 0
        while msgQueue.next():
            rows = self.tw_MsgQueue.rowCount()
            self.tw_MsgQueue.setRowCount(rows + 1)
            self.tw_MsgQueue.setItem(rows, 0, QTableWidgetItem(str(msgQueue.value(0))))
            self.tw_MsgQueue.setItem(rows, 1, QTableWidgetItem(msgQueue.value(1)))
            self.tw_MsgQueue.setItem(rows, 2, QTableWidgetItem(msgQueue.value(2)))
            self.tw_MsgQueue.setItem(rows, 3, QTableWidgetItem(msgQueue.value(3)))
            self.tw_MsgQueue.setItem(rows, 4, QTableWidgetItem(msgQueue.value(4)))
            self.tw_MsgQueue.setItem(rows, 5, QTableWidgetItem(msgQueue.value(5)))
            self.tw_MsgQueue.setItem(rows, 6, QTableWidgetItem(msgQueue.value(6)))
        #Make each cell in each row read only
        for i in range(rows + 1):
            for j in range(7):
                cell_item = QTableWidgetItem()
                cell_item = self.tw_MsgQueue.item(i, j)
                if j == 1:
                    #Set the status field color while we are at it
                    if cell_item.text() == "Submitted": 
                        cell_item.setBackground(QColor("darkBlue"))
                        cell_item.setForeground(QColor("white"))
                    elif cell_item.text() == "Accepted":
                        cell_item.setBackground(QColor(255,255,60))
                        cell_item.setForeground(QColor("black"))
                    elif cell_item.text() == "Sent":
                        cell_item.setBackground(QColor("darkGreen"))
                        cell_item.setForeground(QColor("white"))
                    elif cell_item.text() == "Declined":
                        cell_item.setBackground(QColor("darkRed"))
                        cell_item.setForeground(QColor("white"))
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)
        tableWidth = self.tw_MsgQueue.width()
        self.tw_MsgQueue.resizeColumnsToContents()
        self.tw_MsgQueue.setColumnWidth(3, int(tableWidth * 0.60))
        self.tw_MsgQueue.horizontalHeader().setStretchLastSection(True)

    def AcceptMsg(self):
        outBefore = get_MIdList(self.le_WinlinkOutPath.text())
        #Submit message to Pat
        cmd = ['pat','compose','-s']
        cmd.append(self.le_ActSubject.text())
        cmd.append(self.le_ActTo.text())
        msg = bytes(self.tb_ActiveMessage.toPlainText() + "\c",'utf-8')
        subprocess.run(cmd,input=msg)
        outAfter = get_MIdList(self.le_WinlinkOutPath.text())
        newMId = list(set(outAfter) - set(outBefore))
        #Update active message status
        qString = "UPDATE msgQueue SET msgStatus = 'Accepted', msgWinlinkId = '" + newMId[0] + "' WHERE msgId = " + str(self.actMsgId)
        updateMsg = QSqlQuery(qString)
        updateMsg.exec()
        #Clear the active mesage Id
        self.actMsgId = 0
        #Reload open message queue
        self.reloadOpenMessageQueue()
        #Load new active message
        self.loadActiveMessage()
        #Refresh message queue
        self.loadMessageQueue()
        print("accepted")

    def DeclineMsg(self):
        #Submit message to Pat
        cmd = ['pat','compose','-s']
        cmd.append(self.le_ActSubject.text())
        cmd.append(self.le_ActTo.text())
        msg = bytes(self.tb_ActiveMessage.toPlainText() + "\c",'utf-8')
        subprocess.run(cmd,input=msg)
        #Update active message status
        qString = "UPDATE msgQueue SET msgStatus = 'Declined' WHERE msgId = " + str(self.actMsgId)
        updateMsg = QSqlQuery(qString)
        updateMsg.exec()
        #Clear the active mesage Id
        self.actMsgId = 0
        #Reload open message queue
        self.reloadOpenMessageQueue()
        #Load new active message
        self.loadActiveMessage()
        #Refresh message queue
        self.loadMessageQueue()
        print("accepted")

    def IgnoreMsg(self):
        #Move active message Id to next message in open message queue
        newActMsgId = self.getNextActMsgId()
        if newActMsgId > 0:
            self.actMsgId = newActMsgId
            self.selectActMsgRow()
            #Load new active message
            self.loadActiveMessage()
            print("Ignored")

    def updateSentMsgStatus(self):
        sentMsgs = set(get_MIdList(self.le_WinlinkSentPath.text()))
        acceptedMsgs = QSqlQuery("SELECT msgId, msgWinlinkId FROM ehaw.acceptedMsgs")
        while acceptedMsgs.next():
            if acceptedMsgs.value(1) in sentMsgs:
                qString = "UPDATE msgQueue SET msgStatus = 'Sent' WHERE msgId = " + str(acceptedMsgs.value(0))
                updateMsg = QSqlQuery(qString)
                updateMsg.exec()
                print("Message ",acceptedMsgs.value(1)," Sent")

    def getNextActMsgId(self):
        newActMsgId = 0
        if self.tw_OpenMsgQueue.rowCount() == 1:
            return newActMsgId
        for r in range(self.tw_OpenMsgQueue.rowCount()):
            cell_item = QTableWidgetItem()
            cell_item = self.tw_OpenMsgQueue.item(r,0)
            if cell_item.text() == str(self.actMsgId):
                newCell_item = QTableWidgetItem()
                if r < (self.tw_OpenMsgQueue.rowCount() - 1):
                    newCell_item = self.tw_OpenMsgQueue.item(r + 1, 0)
                    if newCell_item.text() != None:
                        newActMsgId = int(newCell_item.text())
                else:   #reset to top of queue
                    self.reloadOpenMessageQueue()
                    newCell_item = self.tw_OpenMsgQueue.item(0, 0)
                    newActMsgId = int(newCell_item.text())
        return newActMsgId

    def selectActMsgRow(self):
        for r in range(self.tw_OpenMsgQueue.rowCount()):
            cell_item = QTableWidgetItem()
            cell_item = self.tw_OpenMsgQueue.item(r,0)
            if cell_item.text() == str(self.actMsgId):
                self.tw_OpenMsgQueue.selectRow(r)

    def reloadOpenMessageQueue(self):
        while self.tw_OpenMsgQueue.rowCount() > 0:
            self.tw_OpenMsgQueue.removeRow(0)
        self.loadOpenMessageQueue()
        while self.tw_MsgQueue.rowCount() > 0:
            self.tw_MsgQueue.removeRow(0)
        self.loadMessageQueue()



def get_MIdList(path):
    mList = list()
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            mList.append(file[:-4])
    return mList



def createConnection():
    con = QSqlDatabase.addDatabase("QMYSQL")
    con.setHostName(config["host"])
    con.setDatabaseName(config["database"])
    if not con.open(config["user"], config["password"]):
        QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True

# main
app = QApplication(sys.argv)
if not createConnection():
    sys.exit(1)
if __name__ == "__main__":
    win = Window()
    win.show()
    with open('ubuntu.qss','r') as f:
        style = f.read()
        app.setStyleSheet(style)
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
