## Overview

The Emergency Health & Welfare Message service (eHaW) allows members of the public to sumbit basic health and welfare messages directly from any device with a WiFi interface and browser.  Submittted messages are stored in a database that can be accessed by a local amateur radio operator and sent by radio to an email server outside of an emergency zone where no Internet or celualr service are available.

* Email messages may contain up tp 1000 characters and sent to multiple email addresses
* Txt/SMS messages may contain up to 160 characters for destination where only a cell phone number is known
* The eHaW web application is a Node.js solution and can be run on systems as small as a Raspberry Pi
* The eHaw web application includes a message status page showing the current status of each message
    - Submitted    
    - Accepted
    - Sent
    - Declined
* Messages submitted through the eHaW web application are stored and managed in a database
* The eHaW Moderator application allows a licensed amateur radio operator to
    - Review and at their discretion, decline submitted messages for regulatory compliance before they are transmitted by amateur radio services
    - Accept submitted message, automatically formatting them for radio transmission
    - Send accepted messages by radio using the Winlink Radio System  http://www.winlink.org
    - Automatically update message status for efficient feedback to the public
* A new Support_Material folder has been created. It contains the document "R3EMCOMM eHaW Handout - 220914a.pdf" and several other sample documents created to support eHaW related discussions.  The handout was created for an initial eHaW overview presentation to a local emergency communications support group and may be of use to others.


## Copyright/License

Copyright (c) 2022 Bob Segrest KO2F

Developers must read the LICENSE.md file in this archive

### Contributors (alphabetical)

* KO2F   - Bob Segrest
