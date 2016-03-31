//获取worksheet_id
var aQuery = window.location.href.split("?");  //取得Get参数
var aGET = new Array();
if(aQuery.length > 1)
{
    var aBuf = aQuery[1].split("&");
    for(var i=0, iLoop = aBuf.length; i<iLoop; i++)
    {
        var aTmp = aBuf[i].split("=");  //分离key与Value
        aGET[aTmp[0]] = aTmp[1];
    }
}
var release_apply_id = aGET['release_apply_id'];

//日期时间选择器
$(".form-datetime").datetimepicker({
    weekStart: 1,
    todayBtn:  1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    forceParse: 0,
    showMeridian: 1,
    format: "yyyy-mm-dd hh:ii"
});

var git_url_dict = JSON.parse($("#git_url_dict").text());
alert(git_url_dict);

$("input#submit").click(function(){
    var release_title = $.trim($("#release_title").val());
    var producter = $.trim($("#producter").val());
    var release_way = $.trim($("#release_way").val());
    var risk_level = $.trim($("#risk_level").val());
    var developer = $.trim($("#developer").val());
    var tester = $.trim($("#tester").val());
    var release_app = $.trim($("#release_app").val());
//    var git_url = $.trim($("#git_url").val());
    var self_test = $.trim($("#self_test").val());
    var release_class = $.trim($("#release_class").val());
    var release_time = $.trim($("#release_time").val());
    var wiki_url = $.trim($("#wiki_url").val());    //不必填
    var jira_url = $.trim($("#jira_url").val());    //不必填
    var model_modified = $.trim($("#model_modified").val());
    var attension = $.trim($("#attension").val());
    var content_modified = $.trim($("#content_modified").val());
    var explanation = $.trim($("#explanation").val());

    if (release_title=="" || producter=="" || release_way=="" || risk_level=="" || developer=="" || tester=="" ||
        release_app=="" || self_test=="" || release_class=="" || release_time==""
//        || model_modified=="" || attension=="" || content_modified=="" || explanation=="" || git_url==""
        ){
        $("#badnews .content").text('抱歉！表单填写不完整！请重新填写！');
        $("#badnews").addClass("alert alert-warning with-icon").show();
        setTimeout(function(){
            $("#badnews").removeClass("alert alert-warning with-icon").hide();
        },3000);
    }else if (release_title.length>20){
        $("#badnews .content").text('抱歉！标题过长，长度应小于20个！');
        $("#badnews").addClass("alert alert-warning with-icon").show();
        setTimeout(function(){
            $("#badnews").removeClass("alert alert-warning with-icon").hide();
        },3000);
    }else {
        var this_elt = $(this);
        this_elt.addClass("disabled");
        var release_apply_data;
        if (release_apply_id){
            release_apply_data = {
            release_apply_id: release_apply_id,
            title: release_title,
            producter_id: producter,
            release_type: release_way,
            risk_level: risk_level,
            tester_id: tester,
            application_id: release_app,
            deploy: release_class,
            planned_at: release_time,
            wiki_url: wiki_url,
            jira_url: jira_url,
            is_self_test: self_test}
        }else{
            release_apply_data = {
            title: release_title,
            producter_id: producter,
            release_type: release_way,
            risk_level: risk_level,
            tester_id: tester,
            application_id: release_app,
            deploy: release_class,
            planned_at: release_time,
            wiki_url: wiki_url,
            jira_url: jira_url,
            is_self_test: self_test}
        }
        $.post("/release_apply/update/release_apply/", release_apply_data, function(result){
            if (result.status == 200) {
                if (result.status == "200") {
                    $("#goodnews").addClass("alert alert-success with-icon").show();
                    setTimeout(function(){
                        location.href = "/release_apply/list/"
                    },3000);
                }else{
                    $("#badnews .content").text('抱歉！服务器正忙！请尝试重新提交，或者联系运维！');
                    $("#badnews").addClass("alert alert-danger with-icon").show();
                    setTimeout(function(){
                        $("#badnews").removeClass("alert alert-danger with-icon").hide();
                        this_elt.removeClass("disabled");
                    },3000);
                }
            }
        }, "json");
    }
});