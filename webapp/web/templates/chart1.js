$(function () {
    $('#chart1').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'Ratings Comparison'
        },
        subtitle: {
            text: 'IGN Writers vs Community'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'IGN Score'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Community Score'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: -1000,
            y: -1000,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 2,
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
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: 'IGN: {point.x}, Community: {point.y}'
                }
            }
        },
        series: [
            {% for g in plotData %}{% if g['ign_score'] %}{% if g['comm_score'] %}
                { name: "{{ g['name'] }}", color: 'rgba(119, 152, 191, .5)', data: [[{{ g['ign_score'] }}, {{ g['comm_score'] }}]]}, 
            {% endif %}{% endif %}{% endfor %}
        ]
    });
});