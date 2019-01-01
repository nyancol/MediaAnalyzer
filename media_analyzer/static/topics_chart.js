function get_topics_chart(data) {
    var ctx = document.getElementById("topics_chart")
    var options = {
        scales: {
          yAxes: [{
            stacked: true
          }],
          xAxes: [{
            stacked: true
          }]
        },
        // responsive: true,
        // maintainAspectRatio: false
    }
    var colors = palette('tol', 10).map(function(hex) { return '#' + hex; })
    for (var i in data["datasets"]) {
        var length = data["datasets"][i]["data"].length
        data["datasets"][i]["backgroundColor"] = Array(length).fill(colors[i])
    }

    var myChart = new Chart(ctx, {
        type: "bar",
        data: data,
        options: options
    });
}
