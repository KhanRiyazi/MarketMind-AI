/**
 * MarketMind-AI Sheets bridge. Deploy as Web app (Execute as: Me, Access: Anyone).
 * Set Script Property TOKEN (Project Settings > Script properties) and use the same value
 * as GOOGLE_APPS_SCRIPT_TOKEN in the backend .env.
 * Bind the script to the spreadsheet described in ../spreadsheet_schema.md.
 */
var SHEETS = {
  Intraday:    ["timestamp", "symbol", "verdict", "entry", "stop", "target1", "quantity"],
  SIP:         ["timestamp", "monthly", "years", "expected_return", "invested", "value"],
  MutualFunds: ["timestamp", "scheme_code", "scheme", "verdict", "score", "cagr_3y"],
  IPO:         ["timestamp", "name", "verdict", "fair_value", "gmp_pct", "score"],
  Watchlist:   ["symbol", "added_on", "note"]
};

function authorised_(token) {
  var expected = PropertiesService.getScriptProperties().getProperty("TOKEN");
  return expected && token === expected;
}

function sheet_(name) {
  if (!SHEETS[name]) throw new Error("Unknown sheet: " + name);
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(SHEETS[name]);
    sh.setFrozenRows(1);
  }
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    if (!authorised_(body.token)) return json_({ ok: false, error: "unauthorised" });
    var row = [new Date()].concat(body.row);
    sheet_(body.sheet).appendRow(row);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doGet(e) {
  try {
    if (!authorised_(e.parameter.token)) return json_({ ok: false, error: "unauthorised" });
    var sh = sheet_(e.parameter.sheet);
    var limit = Math.min(Number(e.parameter.limit) || 50, 500);
    var last = sh.getLastRow();
    if (last < 2) return json_({ ok: true, rows: [] });
    var start = Math.max(2, last - limit + 1);
    return json_({ ok: true, rows: sh.getRange(start, 1, last - start + 1, sh.getLastColumn()).getValues() });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}
