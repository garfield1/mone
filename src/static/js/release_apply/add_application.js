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
var application_id = aGET['application_id'];

$("input#submit").click(function(){
    var name = $.trim($("#name").val());
    var git_url = $.trim($("#git_url").val());
    var file_path = $.trim($("#file_path").val());
    var test_mvn = $.trim($("#test_mvn").val());
    var pre_release_mvn = $.trim($("#pre_release_mvn").val());
    var formal_mvn = $.trim($("#formal_mvn").val());
    if (name=="" || git_url=="" || file_path==""){
        $("#badnews .content").text('抱歉！表单填写不完整！请重新填写！');
        $("#badnews").addClass("alert alert-warning with-icon").show();
        setTimeout(function(){
            $("#badnews").removeClass("alert alert-warning with-icon").hide();
        },3000);
    }else if (name.length>20){
        $("#badnews .content").text('抱歉！应用名称过长，长度应小于20个！');
        $("#badnews").addClass("alert alert-warning with-icon").show();
        setTimeout(function(){
            $("#badnews").removeClass("alert alert-warning with-icon").hide();
        },3000);
    }else {
        var this_elt = $(this);
        this_elt.addClass("disabled");
        var application_data;
        if (application_id == ""){
            application_data = {
            name: name,
            git_url: git_url,
            file_path: file_path,
            test_mvn: test_mvn,
            pre_release_mvn: pre_release_mvn,
            formal_mvn: formal_mvn}
        }else{
            application_data = {
            application_id: application_id,
            name: name,
            git_url: git_url,
            file_path: file_path,
            test_mvn: test_mvn,
            pre_release_mvn: pre_release_mvn,
            formal_mvn: formal_mvn}
        }
        $.post("/release_apply/update/application/", application_data, function(result){
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
        else if (result.status == 1002){
            $("#badnews .content").text('抱歉！应用名重复！请修改您的应用名！');
            $("#badnews").addClass("alert alert-danger with-icon").show();
            setTimeout(function(){
                $("#badnews").removeClass("alert alert-danger with-icon").hide();
                this_elt.removeClass("disabled");
            },3000);
        }
    }, "json");
    }
});