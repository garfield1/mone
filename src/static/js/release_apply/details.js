/**
 * Created by xufengtian on 16-3-18.
 */
$("#worksheet_content").html($("#worksheet_content").attr("content"));

var action_type = '';
var worksheet_id = $('#worksheet_id').text();
var reject_reason = '';

$(".decision").click(function(){
    var this_elt = $(this);
    var tips = $("#tips");
    var reject_advice = $("#reject-advice");
    if (this_elt.hasClass("reject")){
        $("#tips").hide();
        reject_advice.find("label").text("请填写打回原因(必填):");
        reject_advice.show();
        action_type = $("#last_action").val();
    } else {
        $("#tips").hide();
        reject_advice.find("label").text("请填写通过意见:");
        reject_advice.show();
        action_type = "主管确认";
    }
});

$("#toSave").click(function(){
    reject_reason = $("#reject-reason").val();
    $.post("/worksheet/update/worksheetstate/", {
        action_type: action_type,
        worksheet_id: worksheet_id,
        reject_reason: reject_reason
    }, function(result){
        if (result.status == "200") {
            location.reload();
        }else{
        }
    }, "json");
});