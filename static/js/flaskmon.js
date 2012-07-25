$(function()
{
    $("a[rel=popover]")
        .popover();


    $('.servbtn').width(
        Math.max.apply( 
            Math, 
            $('.servbtn').map(function(){
                return $(this).outerWidth();
            }).get()
        )
    );        
});

/*var graphs = $('.verticalBarGraph');
graphs.hide()*/

