var express = require('express');
var router = express.Router();
var mysql = require("mysql2");
var LoremIpsum = require("lorem-ipsum").LoremIpsum;
var env = require('dotenv').config();

var databaseOptions = {
    host     : process.env.host,
    database : process.env.database,
    user     : process.env.user,
    password : process.env.password
};

const lorem = new LoremIpsum({
	sentencesPerParagraph: {
	  max: 6,
	  min: 2
	},
	wordsPerSentence: {
	  max: 12,
	  min: 4
	}
});

// set event specific values
var con = mysql.createConnection(databaseOptions);

var eventId = 0;
var eventTxtStr = "";
var eventOperatorCallStr = "";
var eventWinlinkCallStr = "";
con.connect( function(err) {
	if (err) {
		console.log("mysql connection error!");
		throw err;
	};
	console.log("Database Connected!");
	con.query("SELECT * FROM eventMetadata WHERE eventId = (SELECT MAX(eventId) FROM eventMetadata)", 
			  function(err, data, fields) {
		if (err) throw err;
		eventId = data[0].eventId;
		eventTxtStr = data[0].eventLocation;
		eventOperatorCallStr = data[0].eventOperatorCallsign;
		eventWinlinkCallStr = data[0].eventWinlinkCallsign;
	});	
});


/* GET home page. */
router.get('/', function(req, res, next) {
  res.render("home", {eventTxt:eventTxtStr});
});

router.get("/createEmail", (req, res) => {
	res.render("createEmail.ejs", {eventTxt:eventTxtStr});
});

router.get("/createTxt", (req, res) => {
	res.render("createTxt.ejs", {eventTxt:eventTxtStr});
});

router.get("/status", (req,res) => {
	let sql = "SELECT * FROM userMsgQueue";
	con.query(sql, function(err, data, fields) {
		if (err) throw err;
	//	console.log(data);
		res.render("msgStatus", {eventTxt:eventTxtStr, msgQueueData:data});
	});
});

router.post("/createMsg", (req, res) => {
	let mType = req.body.mType;
	let from = req.body.from;
	let to = req.body.email;
	let message = req.body.msg;

	let msgStr = message.replace(/'/g,"`");

	let sql = "INSERT INTO msgQueue ";
	sql = sql + "(msgType, msgFrom, msgTo, msgText, msgStatus, msgEventId) ";
	sql = sql + "VALUES ('";
	sql = sql + mType + "','";
	sql = sql + from + "','";
	sql = sql + to + "','";
	sql = sql + msgStr + "','";
	sql = sql + "Submitted" + "',";
	sql = sql + eventId + ")";

	con.query(sql, function(err, result) {
		if (err) {
			throw err;
			console.log("Message Submitted");
			return res.redirect("/");
		}
	});
	
	return res.redirect("/status");
});

/*
	The following code, and the testGen.ejs file are used
	to create email messages in bulk for testing.  While
	it is included in the source, it should be deleted or
	disabled before any operational us or deployment.


router.get("/test", (req, res) => {
	res.render("testGen.ejs", {eventTxt:eventTxtStr});
});


router.post("/generateMsgs", (req, res) => {
	let from = req.body.from;
	let to = req.body.email;
	let mCount = parseInt(req.body.msgCount);

	for (let msgNum = 0; msgNum < mCount; msgNum++) {

		let message = "";
		do {
			let iNum = Math.floor((Math.random() * 5) + 1);
			message = lorem.generateParagraphs(iNum);
		} while (message.length > 1000);

		let msgStr = message.replace(/'/g,"`");

		let sql = "INSERT INTO msgQueue ";
		sql = sql + "(msgType, msgFrom, msgTo, msgText, msgStatus, msgEventId) ";
		sql = sql + "VALUES ('Email','";
		sql = sql + from + "','";
		sql = sql + to + "','";
		sql = sql + msgStr + "','";
		sql = sql + "Submitted" + "',";
		sql = sql + eventId + ")";

		con.query(sql, function(err, result) {
			if (err) {
				throw err;
				console.log("Message Submitted");
				return res.redirect("/");
			}
		});
	};
	return res.redirect("/status");
});

	End of test code to be disabled or deleted prior to
	operational use
*/

module.exports = router;
