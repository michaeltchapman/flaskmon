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
            var thisnode = $(this).text()
            $.getJSON($SCRIPT_ROOT + '/get_metric', {
                node : $(this).text()
            }, function(data) {
                for (var metric in data.metrics)
                {

//                    $('div.metricdisplay ul').append('<ul class="verticalBarGraph">');
                    $('#metricdisplay').append('<ul class="verticalBarGraph" id="' + thisnode + metric + '" >');
                    for (var i = 0; i < data.metrics[metric].length; i++)
                    {
                        //$('div.metricdisplay ul').append('<p>' + data.metrics[metric][i][0] + '</p>');
                        $('#' + thisnode + metric).append('<li><a class="p1" style="height: ' + data.metrics[metric][i][0] + 'px; left: ' + i*10 + 'px;" href="#" rel="popover" data-content="' + data.metrics[metric][i][2] + '"></a></li>');
                    }
                    $('#metricdisplay').append('</ul>');
                }
            });

            //$('div.metricdisplay ul').append('<a class="p1" style="height: 50px; left: ' + i*10 + 'px;" href="#" rel="popover" data-content="' + data.result[j][i]'"></a>');
    });

});


