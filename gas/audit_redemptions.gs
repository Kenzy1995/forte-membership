/**
 * 福泰會員優惠活動 — 試算表維護腳本（綁定至本專案試算表）
 * 功能：每日稽核 Redemptions 重複列、標紅
 */
function auditDuplicateRedemptions() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Redemptions');
  if (!sheet) return;
  var data = sheet.getDataRange().getValues();
  if (data.length < 2) return;
  var headers = data[0];
  var memberIdx = headers.indexOf('member_id');
  var campaignIdx = headers.indexOf('campaign_id');
  var statusIdx = headers.indexOf('狀態');
  if (memberIdx < 0 || campaignIdx < 0) return;

  var seen = {};
  var bg = sheet.getRange(2, 1, data.length - 1, headers.length).getBackgrounds();
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    if (statusIdx >= 0 && row[statusIdx] !== 'completed') continue;
    var key = row[memberIdx] + '|' + row[campaignIdx];
    if (seen[key]) {
      for (var c = 0; c < headers.length; c++) bg[i - 1][c] = '#f4cccc';
    } else {
      seen[key] = true;
    }
  }
  sheet.getRange(2, 1, data.length - 1, headers.length).setBackgrounds(bg);
}
