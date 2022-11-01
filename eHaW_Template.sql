/*
	The following key words will be replaced by the
	eHaW configuration utility to create and then
	execute the Setup_eHaW_support_database.sql script

		WINLINKEXEPATH
		WINLINKOUTPATH
		WINLINKSENTPATH
		EVENTLOCATION
		OPERATORCALL
		WINLINKCALL
		EHAWUSER
		MODERATORUSER
		ADMINNAME
*/

-- Create application database
CREATE DATABASE IF NOT EXISTS eHaW;
USE eHaW;

-- create eHaW config structure
DROP TABLE IF EXISTS ehawConfig;
CREATE TABLE ehawConfig (
	cfgId INT NOT NULL AUTO_INCREMENT,
    cfgWinlinkExePath VARCHAR(255),
    cfgOutPath VARCHAR(255) NOT NULL,
    cfgSentPath VARCHAR(255) NOT NULL,
    PRIMARY KEY (cfgId) 
);

-- insert eHaW config
TRUNCATE ehawConfig;
INSERT INTO ehawConfig (
	cfgWinlinkExePath,
    cfgOutPath,
    cfgSentPath )
VALUES (
	'WINLINKEXEPATH',
    'WINLINKOUTPATH',
    'WINLINKSENTPATH' );

-- create event metadata structure
DROP TABLE IF EXISTS eventMetadata;
CREATE TABLE eventMetadata (
	eventId INT NOT NULL AUTO_INCREMENT,
    eventLocation VARCHAR(255) NOT NULL,
    eventOperatorCallsign VARCHAR(12) NOT NULL,
    eventWinlinkCallsign VARCHAR(12) NOT NULL,
    PRIMARY KEY (eventId) 
);

-- insert initial event metadata
TRUNCATE eventMetadata;
INSERT INTO eventMetadata (
	eventLocation,
    eventOperatorCallsign,
    eventWinlinkCallsign )
VALUES (
	'EVENTLOCATION',
    'OPERATORCALL',
    'WINLINKCALL' );

-- create event metadata structure
DROP TABLE IF EXISTS transportAlias;
CREATE TABLE transportAlias (
	aliasId INT NOT NULL AUTO_INCREMENT,
    tAlias VARCHAR(255) NOT NULL,
    PRIMARY KEY (aliasId) 
);

-- insert default alias
-- Note! there should only be 1 event metadata record...
TRUNCATE transportAlias;
INSERT INTO transportAlias (tAlias)
VALUES ('telnet');

-- Create message queue table
--  note that timestamp fields are maintaied by mysql
-- DROP TABLE msgQueue;
CREATE TABLE IF NOT EXISTS msgQueue (
	msgId INT NOT NULL AUTO_INCREMENT,
    msgType VARCHAR(5) NOT NULL,
    msgFrom VARCHAR(255) NOT NULL,
    msgTo VARCHAR(255) NOT NULL,
    msgText MEDIUMTEXT NOT NULL,
    msgStatus varchar(20) NOT NULL,
    msgWinlinkId varchar(20),
    msgEventId INT NOT NULL,
    msgUpdate TIMESTAMP DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    msgCreate TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (msgId) 
);

-- Create user view
CREATE OR REPLACE VIEW userMsgQueue AS (
	SELECT
		msgId,
        msgFrom,
        CASE
          WHEN msgStatus = 'Declined' THEN ''
          ELSE msgText
		END as msgText,
        msgStatus,
        DATE_FORMAT(msgUpdate, '%b %d, %Y %H:%i') AS msgUpdate,
        DATE_FORMAT(msgCreate, '%b %d, %Y %H:%i') AS msgCreate,
        msgWinlinkId
    FROM
		msgQueue
	WHERE
    	msgEventId = (SELECT MAX(eventMetadata.eventId) FROM eventMetadata)
	ORDER BY
		msgId DESC
);

-- create view for building accepted messages
CREATE OR REPLACE VIEW buildMsg AS (
SELECT
	msgId,
	CASE
      WHEN msgType = 'Email' THEN CONCAT('Status Radio Email From: ',msgFrom,' - DO NOT REPLY!')
      WHEN msgType = 'SMS'   THEN CONCAT('ONE WAY EMAIL-DO NOT REPLY')
	END AS msgSubject,
    REPLACE(msgTo,',',';') AS msgTo,
	CASE
      WHEN msgType = 'Email' THEN 
		CONCAT(	'Radio Email is From: ',msgFrom,'\n\r',
				'It Was Sent From: ',eventLocation,'\n\r',
				'Sent at: ',DATE_FORMAT(current_timestamp, '%b %d, %Y %H:%i'),'\n\r',
				'[The following status message is from a family member or friend] \n\r',
				'====================\n\r',
				msgText,'\n\r',
				'====================\n',
				'[PLEASE DO NOT RESPOND TO THIS MESSAGE.  IT WILL NOT BE RECEIVED] \n\r',
				'This is a ONE WAY email sent by Amateur Radio Operator: [',eventOperatorCallsign,']\n\r',
				'via the Winlink Radio System.  www.winlink.org \n\r',
				'Sent from the above location, to provide information about the above named party(s).\n',
				'--------------------\n',
				'Express Sending Station: ',eventWinlinkCallsign,'\n',
				'Template Version: eHaW v1.0\n'
		)
	  WHEN msgType = 'SMS' THEN
        CONCAT(
				msgText,'\n',msgFrom,'\n'
		)
	END AS msgBody
FROM 
	eHaW.msgQueue join eHaW.eventMetadata
WHERE
	msgStatus = 'Submitted' 
    AND msgType IN ('Email','SMS')
	AND eventId = (SELECT MAX(eventMetadata.eventId) FROM eHaW.eventMetadata)
);

-- Create Open Message view
CREATE OR REPLACE VIEW openMsgQueue AS (
	SELECT
		msgId,
        msgFrom,
        msgTo,
        msgText,
        DATE_FORMAT(msgCreate, '%b %d, %Y %H:%i') AS msgCreate
    FROM
		msgQueue
	WHERE
    	msgEventId = (SELECT MAX(eventMetadata.eventId) FROM eHaW.eventMetadata)
	and	msgStatus = 'Submitted'
	ORDER BY
		msgId
);
 
 -- Create Accepted Messages view for Moderator
CREATE OR REPLACE VIEW acceptedMsgs AS (
	SELECT
		msgId,
        msgWinlinkId
    FROM
		msgQueue
	WHERE
		msgStatus = 'Accepted'
    AND	msgEventId = (SELECT MAX(eventMetadata.eventId) FROM eHaW.eventMetadata)
	ORDER BY
		msgId DESC
);

-- Create Event Status Update To List
CREATE OR REPLACE VIEW esuToList AS (
	SELECT DISTINCT
		msgTo
    FROM
		msgQueue
	WHERE
    	msgEventId = (SELECT MAX(eventMetadata.eventId) FROM eHaW.eventMetadata)
	AND msgType = 'Email'
    AND msgStatus = 'Sent'
	ORDER BY
		msgTo DESC
);

 -- Create eHaW user account
GRANT INSERT, SHOW VIEW ON eHaW.msgQueue TO EHAWUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.userMsgQueue TO EHAWUSER@localhost;
GRANT SELECT, SHOW VIEW on eHaW.eventMetadata to EHAWUSER@localhost;
SHOW GRANTS FOR EHAWUSER@localhost;

 -- Create eHaW user account for PAT extension
GRANT SELECT, INSERT, UPDATE, SHOW VIEW ON eHaW.msgQueue TO MODERATORUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.userMsgQueue TO MODERATORUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.buildMsg TO MODERATORUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.openMsgQueue TO MODERATORUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.acceptedMsgs TO MODERATORUSER@localhost;
GRANT SELECT, INSERT, UPDATE, SHOW VIEW ON eHaW.ehawConfig TO MODERATORUSER@localhost;
GRANT SELECT, INSERT, UPDATE, SHOW VIEW ON eHaW.eventMetadata TO MODERATORUSER@localhost;
GRANT SELECT, INSERT, UPDATE, SHOW VIEW ON eHaW.transportAlias TO MODERATORUSER@localhost;
GRANT SELECT, SHOW VIEW ON eHaW.esuToList TO MODERATORUSER@localhost;
SHOW GRANTS FOR MODERATORUSER@localhost;

GRANT ALL ON eHaW.* TO ADMINNAME@localhost;
