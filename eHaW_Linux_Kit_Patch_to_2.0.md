## eHaW Linux Kit Patch to 2.0 Deployment Notes

The eHaW Linux kits are intended for new eHaW installations and they should not be used to update an existing eHaW deployment.

The eHaW_Linux_Kit_Patch_to_2.0 kit contains the files required to update an eHaW Linux 1.0 deployment to v2.0.

Before attempting to deploy this update, please be sure your eHaW v1.0 deployment is working correctly.  It is unlikely that deploying the update will fix a broken eHaW configuration, and it may likely make correcting an existing configuration problem more difficult.



## Deployment Steps

* 1. Download the eHaW_Linux_Kit_Patch_to_2.0.tar.gz file to the Downloads folder on your Linux system

* 2. Navigate to the Downloads folder using the Files application, right-click the tar.gz file and select the extract here option

* 3. Navigate into the new Downloads/eHaW_Patch_Kit folder and select the eHaWconfig, moderator and moderator_sm files, then right-click and select the Copy option

* 4. Navigate to the folder where you installed the previous eHaW kit (~/bin/eHaW) and replace the 3 old files with the 3 you just copied

* 5. Navigate to the Downloads/ehaW_Patch_Kit/Node/Views foler, select the createEmail.ejs and createTxt.ejs files, then righ-click and select the Copy option

* 6. Navigate to the ~/bin/eHaW/Node/views folder and replace the 2 old files with the 2 you just copied

* 7. Open a Term app and enter the following command:  sudo mysql

* 8. Enter your password when prompted

* 9. Enter the following commands:  (don't forget the semicolon ; at the end of each line)
    - USE eHaW;
    - GRANT SELECT, INSERT, UPDATE, DELETE, SHOW VIEW ON eHaW.transportAlias TO moderator@localhost;

Bob Segrest, KO2F