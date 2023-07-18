## NodeJS Security Update - 230718 for eHaW Deployment Notes

If you have previously deployed eHaW for Linux using any kit prior to v2.1 or eHaW for Windows v2.2.4 (July 18, 2023), you need to update your NodeJS deployment to avoid security issues.


## Linux Deployment Steps

* 1. Login into your Linux Mint system, open a terminal window and browse to the bin/eHaW/Node folder

* 2. Issue the following commands:

* 3. npm update browser-sync

* 4. npm audit fix --force

* 5. If eHaW Node is running, stop and then restart the application


## Windows Deployment Steps

* 1. Login into your Windows system, open a CMD window and browse to the c:\eHaW\Node directory

* 2. Issue the following commands:

* 3. npm update browser-sync

* 4. npm audit fix --force

* 5. If eHaW Node is running, stop and then restart the application


Bob Segrest, KO2F