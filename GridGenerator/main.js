const PDFDocument = require('pdfkit');
const fs = require('fs');

//makeGridPDF('output.pdf', 2.5, 0.1, 0, false, 0, 0);


// Global
var global_loc = 'output';
var global_name = 'hexgrid';
// Hex size
[0.1, 0.2, 0.25, 0.5, 0.9, 1, 1.9, 2, 2.5].forEach((hexSize) => {
    var hexsize_loc = global_loc + '/hexsize_' + hexSize.toString() + '_inch';
    fs.mkdirSync(hexsize_loc);
    var hexsize_name = global_name + '_' + hexSize.toString();
    // Line width
    [0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10].forEach((lineWidth) => {
        var linewidth_loc = hexsize_loc + '/linewidth_' + lineWidth.toString() + '_pt';
        fs.mkdirSync(linewidth_loc);
        var linewidth_name = hexsize_name + '_' + lineWidth.toString();
        // Hex padding
        [0, 0.1, 0.5, 1].forEach((hexPadding) => {
            var hexpadding_loc = linewidth_loc + '/hexpadding_' + hexPadding.toString() + '_inch';
            fs.mkdirSync(hexpadding_loc);
            var hexpadding_name = linewidth_name + '_' + hexPadding.toString();
            // Dash
            [false, true].forEach((dash) => {
                var dash_loc = hexpadding_loc + '/dash_' + dash.toString();
                fs.mkdirSync(dash_loc);
                var dash_name = hexpadding_name + '_' + dash.toString();
                // Done!
                makeGridPDF(dash_loc + '/' + dash_name + '.pdf', hexSize, lineWidth, hexPadding, dash);
                console.log(dash_name);
            });
        });
    });
});
console.log('Done!');

function makeGridPDF(location, hexSize, lineWidth, hexPadding, dash, dashLength=1, dashSpace=1) {
    // Set up variables
    var hexSlantMult = 0.433;
    var hexHeightMult = 0.866;
    var docSize = {x: 595.28, y: 841.89};
    var doc = new PDFDocument({size: 'A4'});
    doc.pipe(fs.createWriteStream(location));
    hexSize *= 72;
    hexPadding *= 72;

    var xCount;
    var yCount;
    var altRow = false;

    for (xCount = -hexSize/2-hexPadding*3/4; xCount < docSize.x+hexSize/2; xCount += hexSize*3/4 + hexPadding*3/4) {
        if (altRow) {
            yCount = -(hexSize*hexSlantMult + hexPadding/2);
            altRow = false;
        } else {
            yCount = 0;
            altRow = true;
        }
        for (; yCount < docSize.y; yCount += hexSize*hexHeightMult + hexPadding) {
            doc.lineWidth(lineWidth);
            if (hexPadding) {
                // use slow method and draw each hexagon
                doc.polygon(
                    [xCount, yCount],
                    [xCount+hexSize/2, yCount],
                    [xCount+hexSize*3/4, yCount+hexSize*hexSlantMult],
                    [xCount+hexSize/2, yCount+hexSize*hexHeightMult],
                    [xCount, yCount+hexSize*hexHeightMult],
                    [xCount-hexSize/4, yCount+hexSize*hexSlantMult]
                );            
            } else {
                // use fast method and draw half hexagons
                // use only points 5, 6, 1, 2
                doc.moveTo(xCount, yCount+hexSize*hexHeightMult)
                .lineTo(xCount-hexSize/4, yCount+hexSize*hexSlantMult)
                .lineTo(xCount, yCount)
                .lineTo(xCount+hexSize/2, yCount)            
            }
            if (dash) {
                doc.dash(dashLength, {space: dashSpace});
            }
            doc.stroke();
        }
    }

    // Finalize PDF file
    doc.end();
}