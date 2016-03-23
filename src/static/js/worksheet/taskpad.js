var taskpad_type = 'own';
var page_num = '1';

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

function ajax_post(taskpad_type,page_num){
    var post_data = {};
    if(taskpad_type){post_data['taskpad_type']=taskpad_type;}
    if(page_num){post_data['page_num']=page_num;}

    $.post("/worksheet/get/taskpad/", post_data, function(result){
        if (result.status == 200) {
            page_num = result.data.page_num;
            page_count = result.data.page_count;
            adjust_pager(page_num, page_count);
            $("#cards").empty();
            if (result.data.total == 0){
//                $("table.hide .template0").clone().appendTo($("table.nohide tbody"));
//                $("table.nohide .template0").removeClass("template0");
            }else{
                var worksheet_list_item = '';
                for(i=0; i<result.data.worksheet_list.length; i++){
                    var temp = $(".template").clone();
                    worksheet_list_item =  result.data.worksheet_list[i];
                    temp.find("a").attr("href","/worksheet/details/"+worksheet_list_item.worksheet_id);
                    temp.find(".title").text("标题："+worksheet_list_item.title);
                    temp.find(".type").text("类型： "+worksheet_list_item.worksheet_type);
                    temp.find(".applytime").text("申请时间："+worksheet_list_item.created_at);
                    temp.find(".applyname").text("申请人："+worksheet_list_item.apply_name);
                    temp.find(".finishtime").text("期望完成时间："+worksheet_list_item.planned_at);
                    var ws_state_elt = temp.find(".state");
                    ws_state_elt.text(worksheet_list_item.status);
                    var ws_state = worksheet_list_item.status
                    if (ws_state=="待开发修改" || ws_state=="待主管修改" ){
                        ws_state_elt.addClass("label-danger");
                    }else if(ws_state=="待主管确认"){
                        ws_state_elt.addClass("label-warning");
                    }else if(ws_state=="待运维认领"){
                        ws_state_elt.addClass("label-info");
                    }else if(ws_state=="待运维执行"){
                        ws_state_elt.addClass("label-success");
                    }else if(ws_state=="待主管关闭工单" || ws_state=="待开发关闭工单" ){
                        ws_state_elt.addClass("label-primary");
                    }
                    temp.appendTo($("#cards"));
                    $("#cards .template").removeClass("template");
                }
            }
        }
    }, "json");
}

$(".task").click(function(){
    $(".task").removeClass("btn-primary");
    var this_button = $(this);
    this_button.addClass("btn-primary");
    taskpad_type = this_button.val();
    page_num = 1;
    ajax_post(taskpad_type,page_num);
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
    ajax_post(taskpad_type,page_num);
});

ajax_post(taskpad_type,page_num);