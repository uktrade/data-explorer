import List from 'list.js';


$(function() {
    function SearchFocus() {
        if (!$(window.parent.document.getElementById("schema_frame")).hasClass('no-autofocus')) {
            $(".search").focus();
        }
    }
    var options = {
        valueNames: [ 'schema-header', 'app' ],
        handlers: { 'updated': [SearchFocus] }
    };
    var tableList = new List('tables', options);

    $('#collapse_all').click(function(){
        $('.schema-table').hide();
    });
    $('#expand_all').click(function(){
        $('.schema-table').show();
    });
    $('.schema-header').click(function(){
        $(this).parent().find('.schema-table').toggle();
    });
});

window.onload = function() {
    document.getElementById("schema-wrapper-loaded").style.display = "block";
};
