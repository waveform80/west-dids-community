(function() {
    var width = 150;
    var height = 20;

    d3.json('crime.json').then(function(crimes) {
        /* Convert dates to JS Date objects */
        var parseDate = d3.timeParse('%Y-%m-%d');
        crimes.forEach(function(crime) {
            crime.incidents.forEach(function(incident) {
                incident.month = parseDate(incident.month);
            });
        });

        /* Append a row per crime to the table */
        var tr = d3
            .select('table#crime-stats tbody')
            .selectAll('tr')
            .data(crimes)
            .enter()
            .append('tr');

        /* Build the text contents for the first three columns, and bind the
         * crime data to the last column
         */
        var td = tr
            .selectAll('td')
            .data(function(row) {
                return [
                    row.crime,
                    row.incidents[row.incidents.length - 2].count,
                    row.incidents[row.incidents.length - 1].count,
                    row,
                ];
            })
            .enter()
            .append('td')
            .text(function(d, i) { return i < 3 ? d : null; });

        /* Draw sparklines in the last column */
        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);
        var line = d3.line()
            .x(function(d) { return x(d.month); })
            .y(function(d) { return y(d.count) + 2; });

        var svgs = tr.selectAll('td:last-child')
            .append('svg')
            .datum(function(data) { return data.incidents; })
            .attr('width', width + 2)
            .attr('height', height + 4);

        svgs
            .append('path')
            .attr('class', 'sparkline')
            .attr('d', function(data) {
                x.domain([data[0].month, data[data.length - 1].month]);
                y.domain(d3.extent(data, function(d) { return d.count; }));
                return line(data);
            });

        svgs
            .append('circle')
            .attr('class', 'marker')
            .attr('r', 2)
            .attr('cx', function(data) {
                x.domain([data[0].month, data[data.length - 1].month]);
                return x(data[data.length - 1].month);
            })
            .attr('cy', function(data) {
                y.domain(d3.extent(data, function(d) { return d.count; }));
                return y(data[data.length - 1].count) + 2;
            });
    });
})();