/**
 * Created by xufengtian on 16-3-18.
 */
var action_type = '';
var worksheet_id = $('#worksheet_id').text();
var reject_reason = '';

$(".decision").click(function(){
    var this_elt = $(this);
    var tips = $("#tips");
    var reject_advice = $("#reject-advice");
    action_type = this_elt.text();
    if (this_elt.hasClass("tl_reject")){
        $("#tips").hide();
        reject_advice.show();
        action_type = "主管打回";
    }else if(this_elt.hasClass("tl_pass")){
        tips.show().text("确认通过吗？");
        reject_advice.hide();
        action_type = "主管确认";
    }else if (this_elt.hasClass("ops_reject")){
        tips.hide();
        reject_advice.show();
        action_type = "运维打回";
    } else if(this_elt.hasClass("ops_pass")) {
        tips.show().text("确认认领吗？");
        reject_advice.hide();
        action_type = "运维认领";
    } else if(this_elt.hasClass("ops_done")) {
        tips.show().text("确认完成了吗？");
        reject_advice.hide();
        action_type = "运维执行成功";
    }
});

$("#toSave").click(function(){
    if (action_type == "主管打回" || action_type == "运维打回"){
        reject_reason = $("#reject-reason").val();
    }else {
        reject_reason = "";
    }
    $.post("/worksheet/update/worksheetstate/", {
        action_type: action_type,
        worksheet_id: worksheet_id,
        reject_reason: reject_reason
    }, function(result){
        if (result.status == "200") {

        }else{

        }
    }, "json");
    location.reload();
});