import sys
import subprocess
import os
import argparse
import base64

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
    QTableWidgetItem
)
from moderator_ui import Ui_MainWindow
from dotenv import load_dotenv


#Define variables
eDict = {}


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.actMsgId = 0
        self.loadInitialData()
        self.pb_ActMsgAccept.clicked.connect(self.AcceptMsg)
        self.pb_ActMsgDecline.clicked.connect(self.DeclineMsg)
        self.pb_ActMsgIgnore.clicked.connect(self.IgnoreMsg)
        self.pb_Send.clicked.connect(self.sendWinlinkMsgs)
        self.pb_ActMsgRetrieve.clicked.connect(self.retrieveOpenMsg)
        self.pb_ReloadMsgQueue.clicked.connect(self.reloadMessageQueues)
        self.pb_RefreshOpenMsgQueue.clicked.connect(self.reloadMessageQueues)
        self.pb_ReloadAdmin.clicked.connect(self.reloadAdminData)
        self.pb_EventCreate.clicked.connect(self.createNewEvent)
        self.pb_AddTransport.clicked.connect(self.addTransportAlias)


    def loadInitialData(self):
        self.loadWinlinkConfig()
        self.loadEventMetadata()
        self.loadTransportAliases()
        self.loadTransportCb()
        self.loadOpenMessageQueue()
        self.loadActiveMessage()
        self.loadMessageQueue()
        self.reloadAdminData()
        self.lcd_OutCount.display(len(get_MIdList(self.le_WinlinkOutPath.text())))

        #Load Winlink configuration
    def loadWinlinkConfig(self):
        ehawCfg = QSqlQuery("SELECT cfgId, cfgWinlinkExePath, cfgOutPath, cfgSentPath FROM ehaw.ehawconfig")
        while ehawCfg.next():
            self.le_WinlinkExecPath.setText(ehawCfg.value(1))
            self.le_WinlinkOutPath.setText(ehawCfg.value(2))
            self.le_WinlinkSentPath.setText(ehawCfg.value(3))

        #Load Event Configuration
    def loadEventMetadata(self):
        self.tw_EventConfig.setAlternatingRowColors(True)
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
        rows = self.tw_EventConfig.rowCount()
        for i in range(rows):
            for j in range(4):
                cell_item = self.tw_EventConfig.item(i,j)
                cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)
        self.tw_EventConfig.resizeColumnToContents(0)
        self.tw_EventConfig.resizeColumnToContents(1)
        self.tw_EventConfig.resizeColumnToContents(2)
        self.tw_EventConfig.horizontalHeader().setStretchLastSection(True)

        #Add a new row to the Event configuration table
    def createNewEvent(self):
        rows = self.tw_EventConfig.rowCount()
        self.tw_EventConfig.setRowCount(rows + 1)
        self.tw_EventConfig.setItem(rows, 1, QTableWidgetItem(""))
        self.tw_EventConfig.setItem(rows, 2, QTableWidgetItem(""))
        self.tw_EventConfig.setItem(rows, 3, QTableWidgetItem(""))
        #make the blank event Id read-only
        rows = self.tw_EventConfig.rowCount()
        cell_item = self.tw_EventConfig.item(0,1)
        cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

        #Load Transport Aliases
    def loadTransportAliases(self):
        self.lw_Transport.setAlternatingRowColors(True)
        self.lw_Transport.clear()
        tAliases = QSqlQuery("SELECT tAlias FROM ehaw.transportAlias")
        while tAliases.next():
            self.lw_Transport.addItem(tAliases.value(0))

        #Load Open Message Queue
    def loadOpenMessageQueue(self):
        self.tw_OpenMsgQueue.setAlternatingRowColors(True)
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
        self.tw_OpenMsgQueue.setColumnWidth(3, int(tableWidth * 0.6))
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
        self.lcd_OutCount.display(len(get_MIdList(self.le_WinlinkOutPath.text())))
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
        self.tw_MsgQueue.setColumnWidth(3, int(tableWidth * 0.58))
        self.tw_MsgQueue.horizontalHeader().setStretchLastSection(True)

    def AcceptMsg(self):
        outBefore = get_MIdList(self.le_WinlinkOutPath.text())
        #Submit message to Pat
        if len(self.le_WinlinkExecPath.text()) > 0:
            cmd = [self.le_WinlinkExecPath.text(),'compose','-s']
        else:
            cmd = ['pat','compose','-s']
        cmd.append(self.le_ActSubject.text())
        print(self.le_ActTo.text())
        print((self.le_ActTo.text()).replace(';',', '))

        msgTo = self.le_ActTo.text().split(';')
        for i in range(len(msgTo)):
            cmd.append(msgTo[i])
        print(cmd)
        msg = bytes(self.tb_ActiveMessage.toPlainText() + "\c",'utf-8')
        subprocess.run(cmd,input=msg)
        outAfter = get_MIdList(self.le_WinlinkOutPath.text())
        self.lcd_OutCount.display(len(outAfter))
        newMId = list(set(outAfter) - set(outBefore))
        #Update active message status
        qString = "UPDATE msgQueue SET msgStatus = 'Accepted', msgWinlinkId = '" + newMId[0] + "' WHERE msgId = " + str(self.actMsgId)
        updateMsg = QSqlQuery(qString)
        updateMsg.exec()
        #Clear the active mesage Id
        self.actMsgId = 0
        #Reload open message queue
        self.reloadMessageQueues()
        #Load new active message
        self.loadActiveMessage()
        #Refresh message queue
        self.loadMessageQueue()
        statusMsg = "Message accepted with Winlink Id " + str(newMId[0])
        self.statusbar.showMessage(statusMsg,3000)

    def DeclineMsg(self):
        #Update active message status
        qString = "UPDATE msgQueue SET msgStatus = 'Declined' WHERE msgId = " + str(self.actMsgId)
        updateMsg = QSqlQuery(qString)
        updateMsg.exec()
        #update status bar
        statusMsg = "eHaW message " + str(self.actMsgId) + " Declined"
        self.statusbar.showMessage(statusMsg,3000)
        #Clear the active mesage Id
        self.actMsgId = 0
        #Reload open message queue
        self.reloadMessageQueues()
        #Load new active message
        self.loadActiveMessage()
        #Refresh message queue
        self.loadMessageQueue()
 
    def IgnoreMsg(self):
        #Move active message Id to next message in open message queue
        newActMsgId = self.getNextActMsgId()
        if newActMsgId > 0:
            self.actMsgId = newActMsgId
            self.selectActMsgRow()
            #Load new active message
            self.loadActiveMessage()
            statusMsg = "Active message set to " + str(newActMsgId)
            self.statusbar.showMessage(statusMsg,2000)

    def sendWinlinkMsgs(self):
        #Send Connect command to Pat
        if len(self.le_WinlinkExecPath.text()) > 0:
            cmd = [self.le_WinlinkExecPath.text(),'connect']
        else:
            cmd = ['pat','connect']
        cmd.append(self.cb_Transport.currentt())
        subprocess.run(cmd)
        #Refresh message queue
        self.loadMessageQueue()
        #Update the Outbox count
        self.lcd_OutCount.display(len(get_MIdList(self.le_WinlinkOutPath.text())))

    def addTransportAlias(self):
        newAlias = self.le_NewTransport.text()
        if newAlias:
            aDupe = False
            for a in range(self.lw_Transport.count()):
                if self.lw_Transport.item(a).text() == newAlias:
                    aDupe = True
            if not aDupe:
                qString = 'Insert INTO transportAlias (tAlias) VALUES ("' + newAlias + '")'
                insertAlias = QSqlQuery(qString)
                self.loadTransportAliases()
                self.statusbar.showMessage("New Transport Alias Created",2000)
                self.le_NewTransport.clear()
                aliasNow = self.cb_Transport.currentText()
                self.loadTransportCb()
                for t in range(self.cb_Transport.count()):
                    if self.cb_Transport.currentText() == newAlias:
                        self.cb_Transport.setCurrentIndex(t)
            else:
                self.statusbar.showMessage("That alias appears to already be in the Transport Alias list.",2000)

        #Load the Transport comboBox
    def loadTransportCb(self):
        self.cb_Transport.clear()
        for a in range(self.lw_Transport.count()):
            self.cb_Transport.addItem(self.lw_Transport.item(a).text())

    def retrieveOpenMsg(self):
        self.actMsgId = int(self.le_ActMsgSelectId.text())
        self.selectActMsgRow()
        #Load new active message
        self.loadActiveMessage()
        statusMsg = "Active message set to " + str(self.actMsgId)
        self.statusbar.showMessage(statusMsg,2000)
        
    def updateSentMsgStatus(self):
        sentMsgs = set(get_MIdList(self.le_WinlinkSentPath.text()))
        acceptedMsgs = QSqlQuery("SELECT msgId, msgWinlinkId FROM ehaw.acceptedMsgs")
        while acceptedMsgs.next():
            if acceptedMsgs.value(1) in sentMsgs:
                qString = "UPDATE msgQueue SET msgStatus = 'Sent' WHERE msgId = " + str(acceptedMsgs.value(0))
                updateMsg = QSqlQuery(qString)
                updateMsg.exec()
                self.statusbar.showMessage("Winlink Outbox messages have been sent",5000)

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
                    self.reloadMessageQueues()
                    newCell_item = self.tw_OpenMsgQueue.item(0, 0)
                    newActMsgId = int(newCell_item.text())
        return newActMsgId

    def selectActMsgRow(self):
        for r in range(self.tw_OpenMsgQueue.rowCount()):
            cell_item = QTableWidgetItem()
            cell_item = self.tw_OpenMsgQueue.item(r,0)
            if cell_item.text() == str(self.actMsgId):
                self.tw_OpenMsgQueue.selectRow(r)

    def reloadMessageQueues(self):
        while self.tw_OpenMsgQueue.rowCount() > 0:
            self.tw_OpenMsgQueue.removeRow(0)
        self.loadOpenMessageQueue()
        self.loadActiveMessage()
        while self.tw_MsgQueue.rowCount() > 0:
            self.tw_MsgQueue.removeRow(0)
        self.loadMessageQueue()

    def reloadAdminData(self):
        while self.tw_EventConfig.rowCount() > 0:
            self.tw_EventConfig.removeRow(0)
        self.loadEventMetadata()
        self.loadWinlinkConfig()


def getEnvironmentVariables():
    load_dotenv(".env")
    # Decode the environment variables into our environmental dictionary
    eDict.update({"MODERATORUSER" : base64.b64decode(os.getenv("MODERATORUSER")).decode("utf-8")})
    eDict.update({"MODERATORPWD" : base64.b64decode(os.getenv("MODERATORPWD")).decode("utf-8")})

def get_MIdList(path):
    mList = list()
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            mList.append(file[:-4])
    return mList

def createConnection():
    getEnvironmentVariables()
    con = QSqlDatabase.addDatabase("QMYSQL")
    con.setHostName("localhost")
    con.setDatabaseName("ehaw")
    if not con.open(eDict.get("MODERATORUSER"), eDict.get("MODERATORPWD")):
        QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True

# main
app = QApplication(sys.argv)
parser = argparse.ArgumentParser()
parser.add_argument("-ubuntu", 
                    help="The ubuntu stylesheet will be used.",
                    action="store_true")
parser.add_argument("-none", 
                    help="No stylesheet will be used.",
                    action="store_true")
args = parser.parse_args()
if not createConnection():
    sys.exit(1)
if __name__ == "__main__":
    win = Window()
    win.show()
    if args.ubuntu:
        with open('ubuntu.qss','r') as f:
            style = f.read()
            app.setStyleSheet(style)
    elif args.none:
        print("launching without style...")
    else:
        win.tw_EventConfig.setStyleSheet("alternate-background-color: gray;")
        win.tw_OpenMsgQueue.setStyleSheet("alternate-background-color: gray;")
        win.tw_MsgQueue.setStyleSheet("alternate-background-color: gray;")
        with open('Combinear.qss','r') as f:
            style = f.read()
            app.setStyleSheet(style)
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
