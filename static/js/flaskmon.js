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

    $('.nodebut').click(function() {
            var thisnode = $(this).text()
            $.getJSON($SCRIPT_ROOT + '/get_metric', {
                node : $(this).text()
            }, function(data) {
                /* Should add a top level div for the node title*/
                $('#metricdisplay').append('<div class="nodeMetrics" id="' + thisnode + '" >');
                $('#' + thisnode).append('<h2>' + thisnode + '</h2');
                for (var metric in data.metrics.f)
                {
                    $('#' + thisnode).append('<div class="metricBlock" id="block' + thisnode + metric + '" >');
                    /* Should add a second inline block to put the metric title in*/
                    $('#block' + thisnode + metric).append('<h3>' + metric + '</h3>');
                    $('#block' + thisnode + metric).append('<ul class="verticalBarGraph" id="' + thisnode + metric + '" >');

                    /* Float Metrics */
                    for (var i = 0; i < data.metrics.f[metric].length; i++)
                    {
                        $('#' + thisnode + metric).append('<li><a class="p1" style="height: ' + data.metrics.f[metric][i][0] + 'px; left: ' + i*10 + 'px;" href="#" rel="popover" data-content="' + data.metrics.f[metric][i][1] + '" ></a></li>');
                    }
                    $('#' + thisnode).append('</ul>');
                    /* String Metrics */
                }
                $('#metricdisplay').append('</div>');
                $("a[rel=popover]")
                    .popover();
            });

    });
});


