/**
 * Created by huangfuzepeng on 16/1/6.
 */
$('.save').click(function(){
    var this_elt = $(this);
    var this_parent = this_elt.parents(".user_data");
    var user_name = this_parent.find(".user_name").text();
    this_elt.next().find(".modal-body-text").text("是否保存"+user_name+"的信息？");
});

$(".toSave").click(function(){
    var this_elt = $(this);
    var this_parent = this_elt.parents(".user_data");
    var user_id = this_parent.find(".user_id").text();
    var role_list = [];
    this_parent.find("input[type=checkbox]:checked").each(
        function () {
            role_list.push($(this).val());
        }
    );
    var organization_id = this_parent.find('.organization').val();
    $.post("/change_information/", {
        user_id: user_id,
        role_list: JSON.stringify(role_list),
        organization_id: organization_id

    }, function(result){}, "json");
});