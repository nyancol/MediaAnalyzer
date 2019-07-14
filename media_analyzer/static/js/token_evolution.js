function draw_chart(data) {
    console.log(data)
    let datasets = {}
    let labels = new Set()
    let dates = {}
    for (var i in data) {
        var date = data[i]["month"]
        labels.add(date);
        if (!(data[i]["publisher"] in datasets)) {
            datasets[data[i]["publisher"]] = [{"month": new Date(date), "value": data[i]["matches"]}];
        } else {
            datasets[data[i]["publisher"]].push({"month": new Date(date), "value": data[i]["matches"]});
        }
    }

    labels = Array.from(labels).map(d => new Date(d)).sort(function (d1, d2) { return d1 > d2 ? 1 : -1; });

    var colors = palette('tol', 10).map(function(hex) { return '#' + hex; })

    var maximi = []
    for (var key in datasets) {
        maximi.push(Math.max.apply(null, datasets[key].map(v => v["value"])));
    }
    var threshold = maximi.sort((a, b) => a-b).reverse()[10]
    let datasets_ = []
    for (var key in datasets) {
        var max = Math.max.apply(null, datasets[key].map(v => v["value"]));
        if (max > threshold) {
            values = labels.map(function(l) {
                                       var value = null
                                       if (datasets[key].length > 0 && l.getTime() == datasets[key][0]["month"].getTime()) {
                                           value = datasets[key][0]["value"];
                                           datasets[key].shift();
                                       }
                                       return value;
                                     });
            datasets_.push({label: key,
                            fill: false,
                            borderColor: colors[0],
                            backgroundColor: colors[0],
                            data: values,
                           });
            colors.shift();
        }
    }

	var config = {
            type: 'line',
            // events: ['click'],
            onClick: (e, b) => { console.log(e); console.log(b); },
            data: {
                labels: labels,
                datasets: datasets_,
            },
            options: {
				responsive: true,
				title: {
					display: true,
					text: 'Pattern occurences by month'
				},
				scales: {
					xAxes: [{
                        type: 'time',
                        time: { unit: 'month' },
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Month'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Value'
						}
					}]
				}
			}
        };
    var ctx = document.getElementById("token_evolution");
    new Chart(ctx, config);
};
