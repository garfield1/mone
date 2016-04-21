/**
 * Created by huangfuzepeng on 16/4/19.
 */
/* JS 代码 */
$('#calendar').calendar({
    clickEvent: function(event)
    {
        window.open(event.event.ref);
    },
    dragThenDrop: false
});
var calendar = $('#calendar').data('zui.calendar');
$.get("/release_apply/get/all/taskpad/", {}, function(result){
    result = JSON.parse(result);
    var newEvents = [];
    if (result.status == 200){
        for(var i=0; i<result.data.release_apply_list.length; i++){
            newEvents.push({title: result.data.release_apply_list[i].title + '<br>'+ '申请人： ' + result.data.release_apply_list[i].applier + '<br>'+ '<span style="background-color: aqua;">'+result.data.release_apply_list[i].state+ '</span>', desc: result.data.release_apply_list[i].title, start: result.data.release_apply_list[i].created_at, end: result.data.release_apply_list[i].created_at, ref: '/release_apply/details/' + result.data.release_apply_list[i].release_apply_id, allDay: true, color: '#ff0000'})

        }
    }
    console.log(newEvents);
    calendar.addEvents(newEvents);

});