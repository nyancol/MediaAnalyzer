function get_language_stats_chart(data) {
    var colors = palette('tol', data["languages"].length).map(function(hex) { return '#' + hex; })
    var data = {
       labels : data["languages"],
       datasets : [
          {
             backgroundColor: colors,
             data : data["counts"]
          } ]
       }

    var options = {
        legend: {
            display: false,
        }
    };
    // get bar chart canvas
    var ctx = document.getElementById("languages_chart");
    // draw bar chart
    var chart = new Chart(ctx, {
        type: "bar",
        data: data,
        options: options
    });
}
