$(function () {
    $('#chart1').highcharts({
        chart: {
            type: 'scatter'
        },
        title: {
            text: 'Ratings Comparison'
        },
        subtitle: {
            text: 'IGN Writers vs Community For Specific Genres'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'IGN Score'
            },
	    min: 0,
	    max: 10,
            startOnTick: false,
            endOnTick: false,
            showLastLabel: true
        },
        yAxis: {
            title: {
		enabled: true,
                text: 'Community Score'
            },
	    min: 0,
	    max: 10,
	    startOnTick: false,
	    endOnTick: false
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'bottom',
            x: -5,
            y: -50,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
	tooltip: {
	    enabled: false
	},
        plotOptions: {
            scatter: {
                marker: {
                    radius: 3,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                }
            }
        },
        series: [{
	    name: 'Sports',
	    marker: { symbol: 'circle' },
	    color: 'rgba(119, 152, 191, .5)',
	    data: [{% for g in plotData['Sports'] %}{% if g['ign_score'] %}{% if g['comm_score'] %}[{{ g['ign_score'] }}, {{ g['comm_score'] }}], {% endif %}{% endif %}{% endfor %}]},
	{
            name: 'RPG',
	    marker: { symbol: 'circle' },
            color: 'rgba(223, 83, 83, .5)',
            data: [{% for g in plotData['RPG'] %}{% if g['ign_score'] %}{% if g['comm_score'] %}[{{ g['ign_score'] }}, {{ g['comm_score'] }}], {% endif %}{% endif %}{% endfor %}]},
	{
            name: 'Shooter',
	    marker: { symbol: 'circle' },
            color: 'rgba(119, 166, 63, .5)',
            data: [{% for g in plotData['Shooter'] %}{% if g['ign_score'] %}{% if g['comm_score'] %}[{{ g['ign_score'] }}, {{ g['comm_score'] }}], {% endif %}{% endif %}{% endfor %}]},
	{
            name: 'Action',
	    marker: { symbol: 'circle' },
            color: 'rgba(115, 75, 120, .5)',
            data: [{% for g in plotData['Action'] %}{% if g['ign_score'] %}{% if g['comm_score'] %}[{{ g['ign_score'] }}, {{ g['comm_score'] }}], {% endif %}{% endif %}{% endfor %}]}
	]
    });
});
