function show_table(publishers) {
    let table_div = document.getElementById("publishers");
    let table = document.createElement("table");
    table.setAttribute("class", "mdl-data-table mdl-js-data-table mdl-shadow--2dp")

    let table_body = document.createElement("table_body");
    let header = ["name", "screen_name", "country", "city", "language"];
    let header_names = ["Name", "Twitter Name", "Country", "City", "Language"];

    let header_row = document.createElement("tr");
    header_names.forEach(function (value) {
        var cell = document.createElement("th");
        cell.setAttribute("class", "mdl-data-table__cell--non-numeric")

        var cell_text = document.createTextNode(value);
        cell.appendChild(cell_text);
        header_row.appendChild(cell);
    });
    table_body.appendChild(header_row);

    for (let i = 0; i < publishers.length; i++) {
        var row = document.createElement("tr");
        header.forEach(function (item) {
            var cell = document.createElement("td");
            cell.setAttribute("class", "mdl-data-table__cell--non-numeric")
            var cellText = document.createTextNode(publishers[i][item]);
            cell.appendChild(cellText);
            row.appendChild(cell);
        });
        table_body.appendChild(row);
    }
    table.appendChild(table_body);
    table_div.appendChild(table);
}
