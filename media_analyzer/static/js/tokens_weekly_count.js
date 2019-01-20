function get_tokens_weekly_count_chart(data) {
    let weeks = new Set();
    let tokens = Object.keys(data);

    for (let i in tokens) {
        token = tokens[i]
        for (let j in data[token]) {
            weeks.add(data[token][j]["week"])
        }
    };

    var colors = palette('tol', 10).map(function(hex) { return '#' + hex; })

    datasets = []
    for (let i in tokens) {
        token = tokens[i]
        weekly_data = {}
        for (let week in weeks) {
            weekly_data[week] = 0;
        }
        for (let j in data[token]) {
            cur = data[token][j];
            weekly_data[cur["week"]] = cur["count"];
        }
        let values = Object.keys(weekly_data).map(function(key){
            return weekly_data[key];
        });
        datasets.push({
            type: "bar",
            label: token,
            backgroundColor: colors.pop(),
            data: values
        });
    }


    var chartData = {
        labels: Array.from(weeks),
        datasets: datasets
    };

    var options = {
        responsive: true,
        // maintainAspectRatio: false
    };

    var ctx = document.getElementById("tokens_weekly_count")
    var myChart = new Chart(ctx, {
        type: "bar",
        data: chartData,
        options: options
    });
}
