$(function () {
    $('#chartRatingHist').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: 'Ratings Comparison'
        },
        subtitle: {
            text: 'IGN Writers vs Community'
        },
        xAxis: {
            title: {
                text: 'Community - IGN Score'
            },
	    categories: [{% for p in scoreHist %}'{{ p[0] }}',{% endfor %}]
        },
        yAxis: {
            title: {
                text: '# of Games'
            },
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
	    column: {
		groupPadding: 0,
		pointPadding: 0,
		borderWidth: 1
	    }
	},
	tooltip: {
	    enabled: false
        },
        series: [{
	    data: [{% for p in scoreHist %}{{ p[1] }},{% endfor %}]
		}]
    });
});
