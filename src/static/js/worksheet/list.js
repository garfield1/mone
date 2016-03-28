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

var title = '';
var apply_name = '';
var operator_id = '';
var worksheet_type_id = '';
var status = '';
var start_time = '';
var end_time = '';
var page_num = '';
var myworksheet_status = '';

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

function ajax_post(title,apply_name,operator_id,worksheet_type_id,status,start_time,end_time,page_num,myworksheet_status){
    var post_data = {};
    if(title){post_data['title']=title;}
    if(apply_name){post_data['apply_name']=apply_name;}
    if(operator_id){post_data['operator_id']=operator_id;}
    if(worksheet_type_id){post_data['worksheet_type_id']=worksheet_type_id;}
    if(start_time){post_data['start_time']=start_time;}
    if(end_time){post_data['end_time']=end_time;}
    if(status){post_data['status']=status;}
    if(page_num){post_data['page_num']=page_num;}
    if(myworksheet_status){post_data['myworksheet_status']=myworksheet_status;}

    $.post("/worksheet/search_worksheet/", post_data, function(result){
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
                for(i=0; i<result.data.worksheet_list.length; i++){
                    var temp = $("table.hide .template").clone();
                    worksheet_list_item =  result.data.worksheet_list[i];
                    temp.find(".title").text(worksheet_list_item.title);
                    temp.find(".type").text(worksheet_list_item.worksheet_type);
                    temp.find(".state").text(worksheet_list_item.status);
                    temp.find(".applytime").text(worksheet_list_item.apply_time);
                    temp.find(".finishtime").text(worksheet_list_item.finish_time);
                    temp.find(".applyname").text(worksheet_list_item.apply_name);
                    temp.find(".opsname").text(worksheet_list_item.operator_name);
                    temp.find("a").attr("href","/worksheet/details/"+worksheet_list_item.worksheet_id);
                    temp.appendTo($("table.nohide tbody"));
                    $("table.nohide .template").removeClass("template");
                }
            }
        }
    }, "json");
}

$("input#submit").click(function(){
    title = $.trim($("#title").val());
    apply_name = $.trim($("#applyname").val());
    operator_id = $.trim($("#opsname").val());
    worksheet_type_id = $.trim($("#type").val());
    status = $.trim($("#state").val());
    start_time = $.trim($("#starttime").val());
    end_time = $.trim($("#endtime").val());
    myworksheet_status = '';
    page_num = 1;
    ajax_post(title,apply_name,operator_id,worksheet_type_id,status,start_time,end_time,page_num,myworksheet_status);
});

$(".aboutme").click(function(){
    var this_button = $(this);
    title = '';
    apply_name = '';
    operator_id = '';
    worksheet_type_id = '';
    status = '';
    start_time = '';
    end_time = '';
    page_num = 1;
    myworksheet_status = this_button.val();
    ajax_post(title,apply_name,operator_id,worksheet_type_id,status,start_time,end_time,page_num,myworksheet_status);
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
    ajax_post(title,apply_name,operator_id,worksheet_type_id,status,start_time,end_time,page_num,myworksheet_status);
});

$(".query").click(function(){
    $(".query").removeClass("btn-primary");
    var this_button = $(this);
    this_button.addClass("btn-primary");
});

ajax_post(title,apply_name,operator_id,worksheet_type_id,status,start_time,end_time,1,myworksheet_status);
