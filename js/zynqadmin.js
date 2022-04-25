var time_only_count = 0;

// 開始時に実行される関数
$(document).ready(function(){
	$("#file_uploader").change(function(e){
		fileChanged(e);
	}
	);
	GetAdminState();
});


function GetPassword()
{
	return $("#password").val();
}

function GetAdminState() {
	let senddata = (time_only_count > 0) ? "timeonly" : "";

	$.ajax({
		timeout: 2000,
		url: './cgi-bin/adminstate.cgi',
		async: false,
		data: senddata,
		success: function(text){
			ShowAdminState(text);
		}
	});
}

function ShowAdminState(text) {
    var obj = JSON.parse(text);
    
	Object.keys(obj).forEach(function(key) {
		if(key == "ipsetting")
		{
			if(obj[key] == "dhcp")
			{
				$("#ipsetting").text("自動(DHCP)");
			}
			else if(obj[key] == "static")
			{
				$("#ipsetting").text("固定");
			}
			else if(obj[key] == "apipa")
			{
				$("#ipsetting").text("自動(APIPA)");
			}
			else
			{
				$("#ipsetting").text("不明");
			}
			return;
		}

		if(key.indexOf("input_") >= 0)
		{
			// ネットワークの諸設定であれば
			$("#"+key).val(obj[key]);
		}
		if(key.indexOf("service.") >= 0)
		{
			// サービス名であれば
			service_name = key.substr("service.".length);
			switch(obj[key])
			{
				case "run":
					$("#"+service_name).html("実行中");
					$("#enable_"+service_name).prop("disabled", true);
					$("#disable_"+service_name).prop("disabled", false);
					break;
				case "stop":
					$("#"+service_name).html("停止");
					$("#enable_"+service_name).prop("disabled", false);
					$("#disable_"+service_name).prop("disabled", true);
					break;
				case "none":
					$("#"+service_name).html("なし");
					$("#enable_"+service_name).prop("disabled", true);
					$("#disable_"+service_name).prop("disabled", true);
					break;
				default:
					$("#"+service_name).html("不明");
					$("#enable_"+service_name).prop("disabled", true);
					$("#disable_"+service_name).prop("disabled", true);
					break;
			}
		}
		else
		{
		    $("#"+key).html(obj[key]);
		}
	});

	if(obj["date_not_set"] == true)
	{
		$("#date_error").html("<span style=\"color:red;font-weight:bold\">時刻が設定されていません</span>");
	}
	else
	{
		$("#date_error").html("");
	}

    //
///*    $("#os").text(obj.os);
	if(time_only_count > 0) time_only_count--;
	else
	{
		time_only_count = 5;
	}
    setTimeout("GetAdminState()",1000);
}

function ntpdate()
{
	message="<div id=\"dialog_result\">同期しています・・</div>";
	caption="NTP同期";
	$("#dialog").html(message);
	$("#dialog").dialog({
		modal: true,
		title: caption,
		width: 640,
		buttons: {
			"閉じる": function() {
				$( this ).dialog( "close" );
			}
		}
	});
	$.ajax({
		timeout: 10000,
		url: './cgi-bin/ntpdate.cgi',
		async: true,
		success: function(text){
			$("#dialog_result").html(text);
		}
	})
}

bootfile = null;

function fileChanged(input) {
	bootfile = input.target.files[0];
	$("#file_upload_dialog").caption = bootfile.name + "を送信します";
}

function FileUpload() {
	caption="ファイル送信";
	$("#file_upload_dialog").dialog({
		modal: true,
		title: caption,
		width: 640,
		buttons: {
			"送信": function() {
				var reader = new FileReader();
				var formData = null;
				reader.onloadend = function() {
					upload(bootfile.name, Math.floor(bootfile.lastModified / 1000), reader.result);
				}
				reader.readAsArrayBuffer(bootfile);
				$( this ).dialog( "close" );
			},
			"キャンセル": function() {
				$( this ).dialog( "close" );
			}
		}
	});
}

function upload(filename, lastModified,  binaryData)
{
	let password = GetPassword();
	if(password=="")
	{
		ShowMessage("パスワードを入力してください");
		return;
	}
	$.ajax({
		type: "POST",
		url: './cgi-bin/upload.cgi?password=' + password + '&filename=' + filename + '&lastModified=' + lastModified + '&_=' + Date.now(),
		cache: false,
		processData: false,
		data: binaryData
	}).done(function(data){
		ShowMessage(data,"File送信結果");
	}).fail(function(){
		ShowMessage("File送信失敗","failed");
	});
}

function Reboot() {
	let password = GetPassword();
	if(password=="")
	{
		ShowMessage("パスワードを入力してください");
		return;
	}
	message="本当に再起動しますか？";
	caption="確認";
	$("#reboot_dialog").html(message);
	$("#reboot_dialog").dialog({
		modal: true,
		title: caption,
		width: 360,
		buttons: {
			"OK": function() {
				ShowMessage("再起動します。1分ほどお待ちください。", "再起動します");
				setTimeout("location.reload()" , 60000);
				$.ajax({
					timeout: 2000,
					url: './cgi-bin/reboot.cgi',
					async: false,
					data: password,
					success: function(text){
						ShowMessage(text , "メッセージ");
					}
				});
				$( this ).dialog( "close" );
			},
			"キャンセル": function() {
				$( this ).dialog( "close" );
			}
		}
	});
}

function ShowMessage(message, caption) {
	message=message.replace(/\n/g,'<br>')
	$("#dialog_message").html(message);
	$("#dialog_message").dialog({
		modal: true,
		title: caption,
		width: 640,
		buttons: {
			"OK": function() {
				$( this ).dialog( "close" );
			}
		}
	});
}
