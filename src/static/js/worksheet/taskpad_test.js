/**
 * Created by huangfuzepeng on 16/3/22.
 */
var taskpad_type = '';
var page_num = '';

function ajax_get_taskpad_list(taskpad_type, page_num){
    var post_data = {};
    if (taskpad_type){
        post_data['taskpad_type'] = taskpad_type
    }
    if (page_num){
        post_data['page_num'] = page_num
    }
    $.post("/worksheet/get/taskpad/", post_data, function(result){
        result = JSON.parse(result);
        //if (result.status == 200){
        //    //console.log(result.data.worksheet_list);
        //    //result.data.worksheet_list.each(
        //    //    console.log(this.title)
        //    )
        //}
    })

}
ajax_get_taskpad_list(taskpad_type, page_num);