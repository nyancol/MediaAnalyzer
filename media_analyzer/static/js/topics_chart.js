function get_topics_chart(data) {
    let weeks = []
    let positives = []
    let negatives = []
    let counts = []

    for (let i in data) {
        weeks.push(data[i]["week"]);
        positives.push(data[i]["avg_positive"]);
        negatives.push(data[i]["avg_negative"]);
        counts.push(data[i]["count"]);
    }

    var colors = palette('tol', 10).map(function(hex) { return '#' + hex; })

    datasets = [{
        yAxisID: 'A',
        type: "line",
        label: "positives",
        data: positives,
        borderColor: "green"
    }, {
        yAxisID: 'A',
        type: "line",
        label: "negatives",
        data: negatives,
        borderColor: "red"
    }, {
        yAxisID: 'B',
        type: "bar",
        label: "counts",
        data: counts,
        backgroundColor: colors.pop()
    }];

    var chartData = {
        labels: weeks,
        datasets: datasets
    };

    var ctx = document.getElementById("topics_chart")
    var options = {
        scales: {
            yAxes: [{
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                  max: 1,
                  min: 0
                }
            }, {
                id: 'B',
                type: 'linear',
                position: 'right',
            }]
        },
        // responsive: true,
        // maintainAspectRatio: false
    };

    var myChart = new Chart(ctx, {
        type: "bar",
        data: chartData,
        options: options
    });
}
