/**
 * Created by huangfuzepeng on 16/1/6.
 */
$('.save').click(function(){
    var this_elt = $(this);
    var this_parent = this_elt.parents(".org_data");
    var org_name = this_parent.find(".org_name").text();
    this_elt.next().find(".modal-body-text").text("是否保存 "+org_name+" 的信息？");
});

$(".toSave").click(function(){
    var this_elt = $(this);
    var this_parent = this_elt.parents(".org_data");
    var org_id = this_parent.find(".org_id").text();
    var user_id = this_parent.find('.user').val();
    $.post("/update/org_leader/", {
        org_id: org_id,
        user_id: user_id
    }, function(result){}, "json");
});