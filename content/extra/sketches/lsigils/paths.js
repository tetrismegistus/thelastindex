// these are the drawings for paths between two vectors, p1 and p2.  in general that is the signature for requesting a draw operation, but I did stretch my own contract a bit.  big tetris then called me up and told me to

function drawCrosses(p1, p2) {
  let idx = p2.x - p1.x;
  let idy = p2.y - p1.y;
  let lineLength = sqrt(idx * idx + idy * idy);
  let crossLength = lineLength * 0.25;
  if (crossLength < 1) {return}
  
  let n = round(random(1, lineLength/20));
  buffer.line(p1.x, p1.y, p2.x, p2.y);
  let dx = p2.x - p1.x;
  let dy = p2.y - p1.y;
  let cl = random(10, crossLength);
  // Perpendicular unit vector
  let len = dist(p1.x, p1.y, p2.x, p2.y);
  let px = (-dy / len) * (cl / 2);
  let py = ( dx / len) * (cl / 2);
  capChooser.pick(p1, p2);
                       
  for (let i = 0; i < n; i++) {
    let t = random(0, 1);
    let c = p5.Vector.lerp(p1, p2, t);
    c.x = c.x;
    c.y = c.y;
    let cp1 = createVector(c.x - px, c.y - py);
    let cp2 = createVector(c.x + px, c.y + py);
    capChooser.pick(cp2, cp1);
    if (random(1) > 0.5) { drawCrosses(cp1, cp2); }
    buffer.line(cp1.x, cp1.y, cp2.x, cp2.y);
  }
}


function drawHorseShoe(p1, p2) {
  let edge = p5.Vector.sub(p2, p1);  // vector along the p1->p2 edge
  let perp = createVector(-edge.y, edge.x).mult(2);  // rotate 90° by swapping and negating

  let cp1 = p5.Vector.add(p1, perp);
  let cp2 = p5.Vector.add(p2, perp);
  buffer.noFill();
  buffer.curve(cp1.x, cp1.y, p1.x, p1.y, p2.x, p2.y, cp2.x, cp2.y);
  capChooser.pick(p1, p2);
}

  
function drawLine(p1, p2) {
  buffer.line(p1.x, p1.y, p2.x, p2.y);
  capChooser.pick(p1, p2);
}
  

function drawULine(p1, p2) {
  let resolution = 20;
  let last = p1.copy();
  for (let i = 0; i < resolution; i++) {
    let lX = lerp(p1.x, p2.x, i/resolution);
    let lY = lerp(p1.y, p2.y, i/resolution);
    let current = createVector(lX, lY);
    drawHorseShoe(last, current);
    last = current.copy();
  }
  drawHorseShoe(last, p2);
  capChooser.pick(p1, p2);
}


function drawArrow(p1, p2, widthFraction = 0.05) {
  buffer.line(p1.x, p1.y, p2.x, p2.y);
  capChooser.pick(p1, p2);
  let dx = p2.x - p1.x;
  let dy = p2.y - p1.y;

  let ox = -dy * widthFraction;
  let oy =  dx * widthFraction;

  let baseT = random(0.1, 0.8);
  let tipT  = random(baseT + 0.1, .3);

  let base = p5.Vector.lerp(p1, p2, baseT);
  let tip  = p5.Vector.lerp(p1, p2, tipT);
  

  
  if (random(1) > 0.5) {
    // full triangle
    triangle(
      tip.x,       tip.y,
      base.x + ox, base.y + oy,
      base.x - ox, base.y - oy
    );

  } else {
    // half triangle: tip to one base corner only, pick side randomly
    let corner = random(1) > 0.5
      ? createVector(base.x + ox, base.y + oy)
      : createVector(base.x - ox, base.y - oy);
    buffer.line(tip.x, tip.y, corner.x, corner.y);
    buffer.line(corner.x, corner.y, base.x, base.y); // close back to line
  }
}

function drawSnakePath(points) {
    for (let i = 0; i < points.length - 1; i++) {
        buffer.line(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y);
    }
}
