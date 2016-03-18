/**
 * Created by xufengtian on 16-3-18.
 */
var action_type = '';
$(".decision").click(function(){
    var this_elt = $(this);
    if (this_elt.hasClass("reject")){
        $("#tips").hide();
        $("#reject-advice").show();
        action_type = '';
    }else {
        $("#tips").show();
        $("#reject-advice").hide();
    }
});