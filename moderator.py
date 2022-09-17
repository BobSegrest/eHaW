import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QApplication, QMessageBox
# #import mysql.connector
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableView,
)

config = {
    'user':'ehawuser2', 
    'password':'eHaW$user2', 
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
#        self.connectSignalsSlots()

        # setup the data model
        self.model = QSqlTableModel(self)
        self.model.setTable("msgQueue")
        self.model.setHeaderData(0, Qt.Horizontal, "msgId")
        self.model.setHeaderData(1, Qt.Horizontal, "msgType")
        self.model.setHeaderData(2, Qt.Horizontal, "msgFrom")
        self.model.setHeaderData(3, Qt.Horizontal, "msgTo")
        self.model.setHeaderData(4, Qt.Horizontal, "msgStatus")
        self.model.setHeaderData(5, Qt.Horizontal, "msgWinlinkId")
        self.model.select()
        # setup the table view
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.resizeColumnsToContents()





def createConnection():
    con = QSqlDatabase.addDatabase("QMYSQL")
    con.setHostName(config["host"])
    con.setDatabaseName(config["database"])
    con.setUserName(config["user"])
    con.setPassword(config["password"])
    if not con.open():
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
