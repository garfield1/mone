//日期时间选择器
$(".form-date").datetimepicker({
    language:  "zh-CN",
    weekStart: 1,
    todayBtn:  1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    minView: 2,
    forceParse: 0,
    format: "yyyy-mm-dd"
});

function adjust_pager(page_num,page_count){
    $(".btn-pager").show().removeClass("btn-primary disabled");
    if (page_count == 1 || page_count == 0){
        $("#first").addClass("disabled");
        $("#previous").addClass("disabled");
        $("#ppage").text(1).addClass("btn-primary");
        $("#cpage").hide();
        $("#npage").hide();
        $("#next").addClass("disabled");
        $("#last").addClass("disabled");
    }else if (page_count == 2){
        $("#first").addClass("disabled");
        $("#previous").addClass("disabled");
        if (page_num == 1){
            $("#ppage").text(1).addClass("btn-primary");
            $("#cpage").text(2);
        }else{
            $("#ppage").text(1);
            $("#cpage").text(2).addClass("btn-primary");
        }
        $("#npage").hide();
        $("#next").addClass("disabled");
        $("#last").addClass("disabled");
    }else if (page_count == 3){
        if (page_num == 1){
            $("#first").addClass("disabled");
            $("#previous").addClass("disabled");
            $("#ppage").text(1).addClass("btn-primary");
            $("#cpage").text(2);
            $("#npage").text(3);
        }else if (page_num == 2){
            $("#ppage").text(1);
            $("#cpage").text(2).addClass("btn-primary");
            $("#npage").text(3);
        }else {
            $("#ppage").text(1);
            $("#cpage").text(2);
            $("#npage").text(3).addClass("btn-primary");
            $("#next").addClass("disabled");
            $("#last").addClass("disabled");
        }
    }else if (page_count > 3){
        if ( page_num ==1 ) {
            $("#first").addClass("disabled");
            $("#previous").addClass("disabled");
            $("#ppage").text(1).addClass("btn-primary");
            $("#cpage").text(2);
            $("#npage").text(3);
        }else if (page_num == page_count) {
            $("#ppage").text(page_count-2);
            $("#cpage").text(page_count-1);
            $("#npage").text(page_count).addClass("btn-primary");
            $("#next").addClass("disabled");
            $("#last").addClass("disabled");
        }else {
            $("#ppage").text(page_num-1);
            $("#cpage").text(page_num).addClass("btn-primary");
            $("#npage").text(page_num+1);
        }
    }
}

var release_title = '';
var release_app = '';
var release_state = '';
var developer = '';
var tester = '';
var operator = '';
var producter = '';
var start_formal_at = '';
var end_formal_at = '';
var page_num = '';
var my_app_status = '';

function ajax_post(release_title,release_app,release_state,developer,tester,operator,producter,start_formal_at,end_formal_at,page_num,own_release_apply_status_id){
    var post_data = {};
    if(release_title){post_data['title']=release_title;}
    if(release_app){post_data['application_id']=release_app;}
    if(release_state){post_data['state']=release_state;}
    if(developer){post_data['applier']=developer;}
    if(tester){post_data['tester']=tester;}
    if(operator){post_data['operator']=operator;}
    if(producter){post_data['producter']=producter;}
    if(start_formal_at){post_data['start_formal_at']=start_formal_at;}
    if(end_formal_at){post_data['end_formal_at']=end_formal_at;}
    if(page_num){post_data['page_num']=page_num;}
    if(own_release_apply_status_id){post_data['own_release_apply_status_id']=own_release_apply_status_id;}

    $.post("/release_apply/search_release_apply/", post_data, function(result){
        if (result.status == 200) {
            page_num = result.data.page_num;
            page_count = result.data.page_count;
            adjust_pager(page_num, page_count);
            $("table.nohide tbody").empty();
            if (result.data.total == 0){
                $("table.hide .template0").clone().appendTo($("table.nohide tbody"));
                $("table.nohide .template0").removeClass("template0");
            }else{
                var worksheet_list_item = '';
                for(i=0; i<result.data.release_apply_list.length; i++){
                    var temp = $("table.hide .template").clone();
                    release_apply_list_item =  result.data.release_apply_list[i];
                    temp.find(".title a").text(release_apply_list_item.title);
                    temp.find(".appname").text(release_apply_list_item.application_name);
                    temp.find(".state").text(release_apply_list_item.state);
                    temp.find(".applyname").text(release_apply_list_item.applier_name);
                    temp.find(".testname").text(release_apply_list_item.tester_name);
                    temp.find(".opsname").text(release_apply_list_item.operator_name);
                    temp.find(".productername").text(release_apply_list_item.producter_name);
                    temp.find(".applytime").text(release_apply_list_item.apply_time);
                    temp.find(".deploytime").text(release_apply_list_item.finish_time);
                    temp.find("a").attr("href","/release_apply/details/"+release_apply_list_item.release_apply_id);
                    temp.appendTo($("table.nohide tbody"));
                    $("table.nohide .template").removeClass("template");
                }
            }
        }
    }, "json");
};

$("input#submit").click(function(){
    release_title = $.trim($("#release_title").val());
    release_app = $.trim($("#release_app").val());
    release_state = $.trim($("#release_state").val());
    developer = $.trim($("#developer").val());
    tester = $.trim($("#tester").val());
    operator = $.trim($("#operator").val());
    producter = $.trim($("#producter").val());
    start_formal_at = $.trim($("#start_formal_at").val());
    end_formal_at = $.trim($("#end_formal_at").val());
    page_num = 1;
    own_release_apply_status_id = '';
    ajax_post(release_title,release_app,release_state,developer,tester,operator,producter,start_formal_at,end_formal_at,page_num,own_release_apply_status_id);
});

$(".aboutme").click(function(){
    var this_button = $(this);
    release_title = '';
    release_app = '';
    release_state = '';
    developer = '';
    tester = '';
    operator = '';
    producter = '';
    start_formal_at = '';
    end_formal_at = '';
    page_num = 1;
    own_release_apply_status_id = this_button.val();
    ajax_post(release_title,release_app,release_state,developer,tester,operator,producter,start_formal_at,end_formal_at,page_num,own_release_apply_status_id);
});

$(".btn-pager").click(function () {
    var this_button = $(this);
    var this_text = this_button.text();
    if (this_text == "<<") {
        page_num = 1;
    }else if (this_text == "<") {
        page_num = page_num-1;
    }else if (this_text == ">") {
        page_num = page_num+1;
    }else if (this_text== ">>") {
        page_num = page_count;
    }else {
        page_num = this_text;
    }
    ajax_post(release_title,release_app,release_state,developer,tester,operator,producter,start_formal_at,end_formal_at,page_num,own_release_apply_status_id);
});

$(".query").click(function(){
    $(".query").removeClass("btn-primary");
    var this_button = $(this);
    this_button.addClass("btn-primary");
});

ajax_post(release_title,release_app,release_state,developer,tester,operator,producter,start_formal_at,end_formal_at,page_num,my_app_status);
