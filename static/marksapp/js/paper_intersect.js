var circ1 = new Path.Circle({
    center: view.center + new Point(-100, 0),
    radius: 140,
    fillColor: 'white',
    strokeColor: 'black',
    strokeWidth: 5
});

var circ2 = new Path.Circle({
    center: view.center + new Point(100, 0),
    radius: 200,
    fillColor: 'white',
    strokeColor: 'black',
    strokeWidth: 5
});

var result = circ1['intersect'](circ2);
result.fillColor = 'black';

function onResize() {
    text.position = view.center + [0, 200];
    square.position = view.center;
}
