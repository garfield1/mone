/**
 * Created by huangfuzepeng on 16/4/19.
 */
/* JS 代码 */
$.get("/release_apply/get/all/taskpad/", {}, function (result) {
    result = JSON.parse(result);
    var newEvents = [];
    if (result.status == 200) {
        for (var i = 0; i < result.data.release_apply_list.length; i++) {
            var event_color = '';
            if (result.data.release_apply_list[i].state == "已关闭上线申请单" ||result.data.release_apply_list[i].state == "待经理确认" || result.data.release_apply_list[i].state== "待开发构建确认"){
                event_color = "green"
            }
            else if(result.data.release_apply_list[i].state == "待开发修改" ||result.data.release_apply_list[i].state == "待开发关闭" || result.data.release_apply_list[i].state== "待主管确认"){
                event_color = "blue"

            }
            else if(result.data.release_apply_list[i].state == "待主管修改" ||result.data.release_apply_list[i].state == "待主管构建确认" || result.data.release_apply_list[i].state == "待主管关闭"){
                event_color = "red"
            }
            else if(result.data.release_apply_list[i].state== "待测试确认" ||result.data.release_apply_list[i].state == "待运维认领" || result.data.release_apply_list[i].state == "待运维执行"){
                event_color = "blue"
            }
            else {
                event_color = "red"
            }
            newEvents.push({
                title: result.data.release_apply_list[i].title + '<br>' + '申请人： ' + result.data.release_apply_list[i].applier + '<br>' + '<span>' + result.data.release_apply_list[i].state + '</span>',
                desc: result.data.release_apply_list[i].title,
                start: result.data.release_apply_list[i].created_at,
                end: result.data.release_apply_list[i].created_at,
                ref: '/release_apply/details/' + result.data.release_apply_list[i].release_apply_id,
                allDay: true,
                calendar: event_color
            })

        }
    }
     $('#calendar').calendar({
        clickEvent: function (event) {
            window.open(event.event.ref);
        },
        data: {
            calendars:
              [
                  {name: "green", color: '#33FF00'},
                  {name: "yellow", color: 'yellow'},
                  {name: "red", color: '#F87979'},
                  {name: "blue", color: '#23BBEC'},
                  {name: "brown", color: 'brown'},
                  {name: "purple", color: 'purple'},
                  {name: "primary", color: 'primary'}
              ],
              events: newEvents
        },
         dragThenDrop: false
    });

    //      get instance
    var calendar = $('#calendar').data('zui.calendar');


});
