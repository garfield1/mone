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
    var release_title = $.trim($("#release_title").val());
    var producter = $.trim($("#producter").val());
    var release_title

    if (name=="" || git_url==""){
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
        if (application_id){
            application_data = {
            application_id: application_id,
            name: name,
            git_url: git_url}
        }else{
            application_data = {
            name: name,
            git_url: git_url}
        }
        $.post("/release_apply/add/application/", application_data, function(result){
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