import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QApplication, QMessageBox
# #import mysql.connector
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

from PyQt5.QtCore import QtMsgType
from PyQt5.QtSql import (
    QSqlDatabase,
    QSqlQuery
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox
)

config = {
    'user':'ko2f', 
    'password':'Ko2f2018!', 
    'host':'127.0.0.1', 
    'database':'ehaw'
}



# msgs = QSqlQuery
# msgs.exec("SELECT msgId,msgType,msgFrom,msgTo,msgStatus,msgWinlinkId FROM msgQueue ORDER BY msgId DESC")

from moderator_ui import Ui_MainWindow

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ehawCfg = QSqlQuery("SELECT cfgId, cfgWinlinkExePath, cfgOutPath, cfgSentPath FROM ehaw.ehawconfig")
        while ehawCfg.next():
            self.ui.ln_WinlinkExecPath.setText(ehawCfg.value(1))
            self.ui.ln_WinlinkOutPath.setText(ehawCfg.value(2))
            self.ui.ln_WinlinkSentPath.setText(ehawCfg.value(3))

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
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
