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

    $('.metriclist')
        .hide();

    /*$('.nodebutton').click(function() {
            $(this).next().toggle();
    });*/

    $('.nodebutton').click(function() {

            $.getJSON($SCRIPT_ROOT + '/get_metric', {
                node : $(this).text, 
            }, function(data) {
                $('div.metricdisplay ul').append(data.result);
            });

            /*$('div.metricdisplay ul').append($(this).next().children().size());
            for(var j = 0; j < data.result.size(); j++)
            {
                $('div.metricdisplay ul').append('<ul class="verticalBarGraph">');
                for(var i = 0; i < data.result[j].size(); i++)
                {
                    $('div.metricdisplay ul').append('<a class="p1" style="height: 50px; left: ' + i*10 + 'px;" href="#" rel="popover" data-content="' + data.result[j][i]'"></a>');
                }
                $('div.metricdisplay ul').append('</ul>');

            }*/
            var output = '<p>' + i + '</p>';
            $('div.metricdisplay ul').append(output);
    });

});


