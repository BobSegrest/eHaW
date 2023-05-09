import sys
import base64
import os
import platform
import time
import subprocess

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QMessageBox
)
from eHaWconfig_ui import Ui_MainWindow
eDict = {}

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.le_AdminPwd.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.le_UserPwd.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.le_ModeratorPwd.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.pb_Save.clicked.connect(self.saveSettings)
        self.pb_Cancel.clicked.connect(self.cancelConfig)
        self.setWinlinkPaths()
        self.pb_Save.setFocus()
        
    def setWinlinkPaths(self):
        patEnv = self.getPatEnv()
        if bWindows:
            oPath = str(patEnv[0]) + "\\\\"
            oPath = oPath + patEnv[1]
            self.le_WinlinkOutPath.setText((oPath +  r"\\out").replace("\\\\","\\"))
            self.le_WinlinkSentPath.setText((oPath +  r"\\sent").replace("\\\\","\\"))
            self.le_WinlinkCall.setText(patEnv[1])
        else:
            oPath = str(patEnv[0]) + "/"
            oPath = oPath + patEnv[1]
            self.le_WinlinkOutPath.setText(oPath +  "/out")
            self.le_WinlinkSentPath.setText(oPath +  "/sent")
            self.le_WinlinkCall.setText(patEnv[1])


    def saveSettings(self):
        # validate the configuration input fields
        if len(self.le_AdminName.text()) < 4:
            self.tb_Info.setText("Please enter the user name you created when you configured your MySQL server into the eHaW Admin User field")
            self.le_AdminName.setFocus()
            return
        elif len(self.le_AdminPwd.text()) < 5:
            self.tb_Info.setText("Please enter the password you created when you configured your MySQL server into the eHaW Admin User field")
            self.le_AdminPwd.setFocus()
            return
        elif len(self.le_UserName.text()) < 5:
            self.tb_Info.setText("Please enter a username in the eHaW User field.")
            self.le_UserName.setFocus()
            return
        elif len(self.le_UserPwd.text()) < 5:
            self.tb_Info.setText("Please enter password for the eHaw User in the eHaW password field.  Make it a good strong password as you will probably never need to use it again!")
            self.le_UserPwd.setFocus()
            return
        elif len(self.le_ModeratorName.text()) < 5:
            self.tb_Info.setText("Please enter a name for the Moderator user account.  Do NOT use the same name you used for the eHaW Admin or user accounts!")
            self.le_ModeratorName.setFocus()
            return
        elif len(self.le_ModeratorPwd.text()) < 5:
            self.tb_Info.setText("Please enter password in the eHaW password field.  Make it a good strong password as you will probably never need to use it again!")
            self.le_ModeratorPwd.setFocus()
            return
        elif len(self.le_WinlinkCall.text()) < 3:
            self.tb_Info.setText("Please enter the amateur radio callsign you used to configure Pat Winlink in the Winlink Callsign field.")
            self.le_WinlinkCall.setFocus()
            return
        elif len(self.le_OperatorCall.text()) < 3:
            self.tb_Info.setText("Please the amateur radio callsign for the eHaW Moderator in the Operator Callsign field.  This may be the same as the Winlink calsign.")
            self.le_OperatorCall.setFocus()
            return
        elif len(self.le_EventLocation.text()) < 20:
            self.tb_Info.setText("Please enter a short [20-60 character] description/location in the Initial Event Location field.")
            self.le_EventLocation.setFocus()
            return
        elif len(self.le_WinlinkOutPath.text()) < 5:
            self.tb_Info.setText("Please enter the configured file path for the Pat outbox folder in the Winlink Out Folder Path field.")
            self.le_WinlinkOutPath.setFocus()
            return
        elif len(self.le_WinlinkSentPath.text()) < 5:
            self.tb_Info.setText("Please enter the configured file path for the Pat sent folder in the Winlink Sent Folder Path field.")
            self.le_WinlinkSentPath.setFocus()
            return
        else:
            self.appConfig()
        
        #Configure the eHaW Node web and Moderator applications
    def appConfig(self):
        self.statusbar.showMessage("Begining automated eHaW configuration",1000)
        self.configureEnvironmentVariables()
        self.statusbar.showMessage("Configure the eHaW database script",3000)
        self.configureSqlScript()
        self.statusbar.showMessage("Configuring the eHaW Node shortcut",2000)
        if bWindows:
            self.finalizeNodeShortcut()
            self.displaySqlInstructions()
            os.remove("pat.exe")
        else:
            self.createDesktopFiles()
        self.statusbar.showMessage("Completing the Npm Install for eHaW Node",10000)
        self.runNpmInstall()
        self.statusbar.showMessage("All done for now.  Click Cancel to close this dialog, Launch the eHaW Node, the Moderator and give it a go!",10000)

        # Initialize the environmental variables
    def configureEnvironmentVariables(self):
        # create the Moderator .env file
        print("creating Moderator .env file")
        envFile = open(".env", "w")
        envFile.write("ADMINNAME=" + base64.b64encode(self.le_AdminName.text().encode("utf-8")).decode("utf-8") + "\n")
        envFile.write("ADMINPWD=" + base64.b64encode(self.le_AdminPwd.text().encode("utf-8")).decode("utf-8") + "\n")
        envFile.write("EHAWUSER=" + base64.b64encode(self.le_UserName.text().encode("utf-8")).decode("utf-8") + "\n")
        envFile.write("EHAWUSERPWD=" + base64.b64encode(self.le_UserPwd.text().encode("utf-8")).decode("utf-8") + "\n")
        envFile.write("MODERATORUSER=" + base64.b64encode(self.le_ModeratorName.text().encode("utf-8")).decode("utf-8") + "\n")
        envFile.write("MODERATORPWD=" + base64.b64encode(self.le_ModeratorPwd.text().encode("utf-8")).decode("utf-8") + "\n")
        cwd = os.getcwd()
        envFile.write("WD=" + base64.b64encode(cwd.encode("utf-8")).decode("utf-8") + "\n") 
        envFile.close()
        # retrieve the env contents
        print("retrieving Moderator .env file")
        from dotenv import load_dotenv
        load_dotenv(".env")
        # decode the environment variables into our environmental dictionary
        eDict.update({"ADMINNAME" : base64.b64decode(os.getenv("ADMINNAME")).decode("utf-8")})
        eDict.update({"ADMINPWD" : base64.b64decode(os.getenv("ADMINPWD")).decode("utf-8")})
        eDict.update({"EHAWUSER" : base64.b64decode(os.getenv("EHAWUSER")).decode("utf-8")})
        eDict.update({"EHAWUSERPWD" : base64.b64decode(os.getenv("EHAWUSERPWD")).decode("utf-8")})
        eDict.update({"MODERATORUSER" : base64.b64decode(os.getenv("MODERATORUSER")).decode("utf-8")})
        eDict.update({"MODERATORPWD" : base64.b64decode(os.getenv("MODERATORPWD")).decode("utf-8")})
        eDict.update({"WD" : base64.b64decode(os.getenv("WD")).decode("utf-8")})
        # and we will add a few local references too for convenience during configuration
        eDict.update({"WINLINKCALL" : self.le_WinlinkCall.text()})
        eDict.update({"OPERATORCALL" : self.le_OperatorCall.text()})
        eDict.update({"EVENTLOCATION" : self.le_EventLocation.text()})
        patEnv = self.getPatEnv()
        if bWindows:
            oPath = str(patEnv[0]) + "\\\\"
            oPath = oPath + patEnv[1]
            eDict.update({"WINLINKEXEPATH" : ""})
            eDict.update({"WINLINKOUTPATH" : oPath + r"\\out"})
            eDict.update({"WINLINKSENTPATH" : oPath + r"\\sent"})
        else:
            oPath = str(patEnv[0]) + "/"
            oPath = oPath + patEnv[1]
            eDict.update({"WINLINKEXEPATH" : ""})
            eDict.update({"WINLINKOUTPATH" : oPath + "/out"})
            eDict.update({"WINLINKSENTPATH" : oPath + "/sent"})
        # create the eHaW .env file
        print("creating eHaW Node .env file")
        self.statusbar.showMessage("Setting up the eHaW Web environment variables",3000)
        # create the Moderator .env file
        if bWindows:
            envFile = open(".\\Node\\.env", "w")
        else:
            envFile = open("Node/.env", "w")
        envFile.write("host=localhost\n")
        envFile.write("database=eHaW\n")
        envFile.write("user=" + eDict.get("EHAWUSER") + "\n")
        envFile.write("password=" + eDict.get("EHAWUSERPWD") + "\n")
        envFile.close()

        # Create Setup_eHaW_support_database SQL Script
    def configureSqlScript(self):
        # get the SQL configuration template
        print("creating database setup script")
        self.statusbar.showMessage("Creating a database setup script for your configuration",3000)
        if bWindows:
            fileName = os.getcwd() + r"\eHaW_Template.sql"
        else:
            fileName = os.getcwd() + "/eHaW_Template.sql"
        fileContent = []
        with open(fileName, 'r') as reader:
            fileContent = reader.readlines()
        reader.close()
        # write the localized SQL script
        if bWindows:
            scriptFile = open(".\\Node\\Setup_eHaW_support_database.sql", "w")
        else:
            scriptFile = open("./Node/Setup_eHaW_support_database.sql", "w")
        t = ""
        keyList = list(eDict.keys())
        valList = list(eDict.values())
        for l in range(len(fileContent)):
            t = fileContent[l]
            # replace any environmental placeholders
            for e in range(len(eDict)):
                if t.find(keyList[e]) != -1:
                    t = t.replace(str(keyList[e]), str(valList[e]))
            scriptFile.write(t)
        scriptFile.close()

        # Create linux desktop and shell files
    def createDesktopFiles(self):
        print("Creating Linux desktop files")
        self.statusbar.showMessage("Creating eHaW menu entries",1000)
        wd = os.getcwd()
        appPath = os.path.expanduser("~") + "/.local/share/applications"
        # drop and create Moderator desktop file
        if os.path.exists(appPath +"/eHaWModerator.desktop"):
            os.remove(appPath + "/eHaWModerator.desktop")
        with open(appPath + "/eHaWModerator.desktop", 'w') as outFile:
            outFile.write("[Desktop Entry]\n")
            outFile.write("Encoding=UTF-8\n")
            outFile.write("Exec=" + wd + "/moderator -workDir " + wd + "\n")
            outFile.write("Icon=" + wd + "/KO2FClientIcon.ico\n")
            outFile.write("Type=Application\n")
            outFile.write("Terminal=false\n")
            outFile.write("Comment=eHaW Moderator Tool\n")
            outFile.write("Name=eHaW Moderator\n")
        outFile.close()
        # drop and create Moderator Small desktop file
        if os.path.exists(appPath +"/eHaWModeratorSm.desktop"):
            os.remove(appPath + "/eHaWModeratorSm.desktop")
        with open(appPath + "/eHaWModeratorSm.desktop", 'w') as outFile1:
            outFile1.write("[Desktop Entry]\n")
            outFile1.write("Encoding=UTF-8\n")
            outFile1.write("Exec=" + wd + "/moderator_sm -workDir " + wd + "\n")
            outFile1.write("Icon=" + wd + "/KO2FClientIcon.ico\n")
            outFile1.write("Type=Application\n")
            outFile1.write("Terminal=false\n")
            outFile1.write("Comment=eHaW Moderator small Tool\n")
            outFile1.write("Name=eHaW Moderator small\n")
        outFile1.close()
        # drop and create eHaW Node desktop file
        if os.path.exists(appPath +"/eHaWNode.desktop"):
            os.remove(appPath + "/eHaWNode.desktop")
        with open(appPath + "/eHaWNode.desktop", 'w') as outFile2:
            outFile2.write("[Desktop Entry]\n")
            outFile2.write("Encoding=UTF-8\n")
            outFile2.write("Exec=" + wd + "/eHaWNode\n")
            outFile2.write("Icon=" + wd + "/KO2FClientIcon.ico\n")
            outFile2.write("Type=Application\n")
            outFile2.write("Terminal=true\n")
            outFile2.write("Comment=eHaW Node Web Application\n")
            outFile2.write("Name=eHaW Node\n")
        outFile2.close()
        # drop and create eHaW Node shell script
        if os.path.exists(wd +"/eHaWModerator.desktop"):
            os.remove(wd + "/eHaWNode")
        with open(wd + "/eHaWNode", 'w') as outFile3:
            outFile3.write("#!/bin/sh\n")
            outFile3.write("cd " + wd + "/Node\n")
            outFile3.write("npm start\n")
        outFile3.close()
        os.chmod(wd + "/eHaWNode",
                 0o010 |
                 0o020 |
                 0o040 |
                 0o100 |
                 0o200 |
                 0o400 )

        # Configure the batch file for the eHaW Node shortcut
    def finalizeNodeShortcut(self):
        print("finalizing eHaW Node shortcut")
        self.statusbar.showMessage("Finalizing the eHaW Node shortcut",1000)
        batchPath = os.getcwd() 
        batchFile = batchPath + r"\Node\eHaWNode.bat"
        os.remove(batchFile)
        with open(batchFile, 'w') as outFile:
            outFile.write("cd " + batchPath + "\\Node\n")
            outFile.write("npm start\n")
        outFile.close()

        # Open a popup to guide user through running SQL script
    def displaySqlInstructions(self):
        print("open msgbox with mysql script instruction")
        self.statusbar.showMessage("this is where we need to run the database script...",3000)
        msg = QMessageBox()
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowTitle("Please do the following:")
        msg.setStyleSheet("QLabel{min-width:650 px; font-size: 15px;} QPushButton{ width:25px; font-size: 18px; }")
        details = "1. Open a new Cmd window\n"
        details = details + "2. Start MySql with the following command:\n"
        details = details + r'   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u adminName -p' + "\n"
        details = details + "      [don't forget to include the quotation marks...]\n"
        details = details + "3. When prompted, enter you eHaW admin password\n"
        details = details + "4. Enter the following command line:\n"
        details = details + '    source ' + os.getcwd() + r'\Node\Setup_eHaW_support_database.sql' + "\n"
        details = details + "5. Scroll your Cmd window as needed and verify there were no errors\n"
        details = details + "     [warnings are Ok... There are normally 3 of them]\n"
        details = details + "6. Close the Cmd window, then click Ok on this dialog window to proceed\n"
        msg.setText(details)
        d = msg.exec_()

        # create and execute a batch file to do the npm install for eHaW Node
    def runNpmInstall(self):
        print("creating batch file to execute npm install")
        if bWindows:
            npmBatchPath = os.getcwd() + r"\Node"
            npmBatchFile =  npmBatchPath + r"\npmInstall.bat"
            with open(npmBatchFile, 'w') as outFile:
                outFile.write("cd " + npmBatchPath + "\n")
                outFile.write("npm install\n")
            outFile.close()
            print("running npm install")
            subprocess.call(npmBatchFile)
            os.remove(npmBatchFile)
        else:
            npmBatchFile = os.getcwd() + "/Node/npmInstall.sh"
            with open(npmBatchFile, 'w') as outFile:
                outFile.write("cd " + os.getcwd() + "/Node\n")
                outFile.write("npm install\n")
            outFile.close()
            os.system("sh " + npmBatchFile)
            os.remove(npmBatchFile)

    def cancelConfig(self):
        self.close()

    def getPatEnv(self):
        if bWindows:
            myCall = ""
            mailBox = ""
            proc = subprocess.Popen(['pat.exe', 'env'],
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    )
            while True: # Infinite loop
                output = proc.stdout.readline()
                if proc.poll() is not None:
                    break
                if output:
                    ln = str(output.strip())
                    if ln.find("PAT_MYCALL") != -1:
                        myCall = ln[14:len(ln)-2]
                    if ln.find("PAT_MAILBOX_PATH") != -1:
                        mailBox = ln[20:len(ln)-2]
        else:
            proc = subprocess.Popen("pat env",
                                shell=True,
                                stdout=subprocess.PIPE,
                                )
            while True: # Infinite loop
                output = proc.stdout.readline()
                if proc.poll() is not None:
                    break
                if output:
                    ln = str(output.strip())
                    if ln.find("PAT_MYCALL") != -1:
                        myCall = ln[14:len(ln)-2]
                    if ln.find("PAT_MAILBOX_PATH") != -1:
                        mailBox = ln[20:len(ln)-2]
        return [mailBox, myCall, bWindows]



# main
app = QApplication(sys.argv)
global bWindows
print("defining bWindows")
if platform.system() == "Windows":
    bWindows = True
else:
    bWindows = False
if __name__ == "__main__":
    win = Window()
    win.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
