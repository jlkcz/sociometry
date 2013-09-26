//basic shapes
joint.shapes.sm = {};

//definition of rings

joint.shapes.sm.Ring = joint.shapes.basic.Circle.extend({
    //markup: '<g class="rotatable"><g class="scalable"><circle/><text/></g></g>',
    markup: '<g class="rotatable"><g class="scalable"><circle class="root"/><g class="tokens" /></g><text class="label"/></g>',
    defaults: joint.util.deepSupplement({

        type: 'sm.Ring',
        size: { width: 1, height: 1 },

        attrs: {
            '.': { magnet: false, 'pointer-events':'none' },
            '.label': {
                'text-anchor': 'middle',
                'ref-x': .5,
                'ref-y': -25,
                ref: '.root',
                fill: 'pink',
                'font-size': 99
            },
            circle: {
                r : 50,
                "stroke-width": 1,
                magnet: true,
                stroke: '#cccccc',
                fill:'transparent'
            }

        }

    }, joint.shapes.basic.Generic.prototype.defaults)
});



//definition of Child
joint.shapes.sm.Child = joint.shapes.basic.Circle.extend({
    defaults: joint.util.deepSupplement({
        type: 'sm.Child',
        orbit: 300,
        attrs: {
            circle: { 'stroke-width': 3 },
            text: { 'font-weight': 'bold' }
        }
    }, joint.shapes.basic.Circle.prototype.defaults)
});

//oneway link
joint.shapes.sm.OneWay = joint.dia.Link.extend({
    defaults: joint.util.deepSupplement({
        attrs: {
            '.marker-target': { d: 'M 10 0 L 0 5 L 10 10 z' },
            '.connection':{stroke:'black', fill:"transparent", 'stroke-width':1},
            '.marker-vertices': { fill:"#cccccc" },
            '.marker-arrowheads': { display: 'none' },
            '.connection-wrap': { display: 'none' },
            '.link-tools': { display : 'none' }
        },
        type: "sm.OneWay",
        smooth: true
    }, joint.dia.Link.prototype.defaults)
});

//twoway link
joint.shapes.sm.TwoWay = joint.dia.Link.extend({
    defaults: joint.util.deepSupplement({
        attrs: { '.marker-target': { d: 'M 10 0 L 0 5 L 10 10 z' },
	        '.marker-source': { d: 'M 10 0 L 0 5 L 10 10 z' },
	        '.connection':{stroke:'black', fill:"transparent", 'stroke-width':5},
	        '.marker-vertices': { fill:"#cccccc" },
            '.marker-arrowheads': { display: 'none' },
            '.connection-wrap': { display: 'none', fill:"white" },
            '.link-tools': { display : 'none' }
	        },
        type: "sm.TwoWay",
        smooth: true

    }, joint.dia.Link.prototype.defaults)
});

