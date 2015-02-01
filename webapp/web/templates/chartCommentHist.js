$(function () {
    $('#chartCommentHist').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            style: {"display": "none"}
        },
        xAxis: {
            title: {
                text: '# of Games Commented On'
            },
	    categories: ['0', '', '', '', '', '5', '', '', '', '', '10', '', '', '', '', '15', '', '', '', '', '20', '', '', '', '', '25', '', '', '', '', '30', '', '', '', '', '35', '', '', '', '', '40', '', '', '', '', '45', '', '', '', '', '50']
        },
        yAxis: {
            title: {
                text: '# of Users'
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
            color: '#DF5353',
            data: [0, 0, 7453, 3627, 2066, 1397, 984, 679, 524, 427, 354, 251, 235, 175, 162, 141, 121, 98, 84, 69, 60, 56, 44, 48, 42, 32, 27, 21, 25, 30, 17, 23, 13, 13, 9, 19, 11, 8, 8, 12, 6, 6, 8, 11, 10, 3, 9, 4, 6, 5, 5]
		}]
    });
});
