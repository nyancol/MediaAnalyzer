function get_thirty_days_chart(data) {
    var data = data[0]["topics"]

    var labels = []
    var values = []
    for (var i in data) {
        labels.push(data[i]["keywords"].join(', '))
        values.push(data[i]["matches"])
    }

    var color = Chart.helpers.color;
    var bar_chart_data = {
        labels: labels,
        datasets: [{
            backgroundColor: '#ff6384',
            data: values
        }]
    };

    var ctx = document.getElementById("thirty_days_topics")

    var options = {
        responsive: true,
        // maintainAspectRatio: false
    };

    var myChart = new Chart(ctx, {
        type: "horizontalBar",
        data: bar_chart_data,
        options: options
    });
}
