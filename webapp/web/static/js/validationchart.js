$(function () {
    $('#highchart').highcharts({
        title: {
            style: { 'display': 'none' }
        },
        xAxis: {
            categories: ['6', '12', '18', '24', '30', '36', '42'],
            title: {
                text: '# of Recommendations Shown'
            }
        },
        yAxis: {
            title: {
                text: '% of Users Correctly Predicted'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }],
            min: 0
        },
        tooltip: {
            crosshairs: true,
            shared: true
        },
        series: [{
            name: 'RespawnInto',
            data: [27.0, 34.1, 41.5, 45.4, 49.2, 51.4, 54.4]    // [305, 386, 469, 513, 556, 581, 615] / 1131
        }, {
            name: 'Best In Genre',
            data: [12.4, 19.7, 28.7, 34.6, 40.2, 44.6, 49.4]    // [177, 281, 408, 493, 572, 635, 703] / 1423
        }, {
            name: 'Random',
            data: [0.5, 1.1, 1.6, 2.1, 2.7, 3.3, 3.9]           // [7, 15, 23, 31, 39, 47, 55] / 1423
        }]
    });
});
