$(function () {
    $('#chartReviewHist').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            style: {"display": "none"}
        },
        xAxis: {
            title: {
                text: '# of Characters in Review (in thousands)'
            },
	    categories: [{% for p in reviewHist %}'{{ p[0] }}',{% endfor %}]
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
	    data: [{% for p in reviewHist %}{{ p[1] }},{% endfor %}]
		}]
    });
});
