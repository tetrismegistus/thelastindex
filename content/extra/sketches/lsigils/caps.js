// these are the drawing specifications for the end cap options

function capWithCircles(p1, p2) {
  buffer.noFill();
  buffer.circle(p1.x, p1.y, gridRes * .1);
  buffer.circle(p2.x, p2.y, gridRes * .1);
}

function capWithCircle(p1) {
  buffer.noFill();
  buffer.circle(p1.x, p1.y, gridRes * .1);
}


function crescentEndCap(entryPoint, rotation, size) {
  let r1 = size;
  let r2 = size * 0.9;

  let O1 = createVector(
    entryPoint.x - cos(rotation) * r1,
    entryPoint.y - sin(rotation) * r1
  );
  let O2 = createVector(
    entryPoint.x - cos(rotation) * (r1 + size * 0.2),
    entryPoint.y - sin(rotation) * (r1 + size * 0.2)
  );

  let intersections = circleIntersections(O1, r1, O2, r2);
  if (!intersections) return;
  let [c1, c2] = intersections;

  let ang1_c1 = atan2(c1.y - O1.y, c1.x - O1.x);
  let ang1_c2 = atan2(c2.y - O1.y, c2.x - O1.x);
  let ang2_c1 = atan2(c1.y - O2.y, c1.x - O2.x);
  let ang2_c2 = atan2(c2.y - O2.y, c2.x - O2.x);

  // rotation points from O1 toward entryPoint, so use it to pick the correct arc half
  // we want the arc that spans TOWARD rotation (the entryPoint side)
  // normalize angles so we sweep through rotation
  function arcThroughAngle(center, a1, a2, target, radius) {
    // ensure we sweep the half that contains target
    let mid = (a1 + a2) / 2;
    // if mid isn't near target, use the other half
    if (abs(angleDiff(mid, target)) > HALF_PI) {
      // swap to sweep the other arc
      return getCoordsOfArc(center, max(a1, a2), min(a1, a2) + TWO_PI, radius);
    }
    return getCoordsOfArc(center, min(a1, a2), max(a1, a2), radius);
  }

  function angleDiff(a, b) {
    let d = (b - a + PI) % TWO_PI - PI;
    return d;
  }

  let arc1 = arcThroughAngle(O1, ang1_c1, ang1_c2, rotation, r1);
  let arc2 = arcThroughAngle(O2, ang2_c1, ang2_c2, rotation, r2);

  buffer.fill(strokeColor);
  buffer.beginShape();
  for (let p of arc1) buffer.vertex(p.x, p.y);
  for (let i = arc2.length - 1; i >= 0; i--) buffer.vertex(arc2[i].x, arc2[i].y);
  buffer.endShape(CLOSE);
  noFill();
}

function arrowEndCap(entryPoint, rotation, distance=50) {
   outlinePoints = [createVector(0, 0)];

  buffer.push();
  buffer.translate(entryPoint.x, entryPoint.y);
  
  let dp1 = createVector(cos(radians(45) + rotation) * distance, sin(radians(45) + rotation) * distance); 
  let dp2 = createVector(cos(TWO_PI - radians(45) + rotation) * distance, sin(TWO_PI - radians(45) + rotation) * distance); 
  let cp1 = centroid(createVector(0, 0), dp1, dp2);
  let side1 = [];
  let side2 = [];
  for (let i = 0; i < 1; i+=0.1) {
    let j = 1.0 - i;
    let curve1x = bezierPoint(0, cp1.x, cp1.x, dp1.x, j); 
    let curve1y = bezierPoint(0, cp1.y, cp1.y, dp1.y, j); 
    let curve2x = bezierPoint(0, cp1.x, cp1.x, dp2.x, i); 
    let curve2y = bezierPoint(0, cp1.y, cp1.y, dp2.y, i); 
    side1.push(createVector(curve1x, curve1y));
    side2.push(createVector(curve2x, curve2y));
  }

  outlinePoints = outlinePoints.concat(side2);
  
  outlinePoints.push(dp1);
  outlinePoints = outlinePoints.concat(side1);
  outlinePoints.push(createVector(0, 0));
  buffer.fill(strokeColor);
  buffer.beginShape();
  for (var p of outlinePoints) {

    buffer.vertex(p.x, p.y);
  }
  buffer.endShape(CLOSE);
  buffer.pop();
 
}


function spiralCap(entryPoint, rotation, distance = 10) {
  let turns = 1.1;
  let totalAngle = TWO_PI * turns;
  let step = radians(0.5);

  let spiralCenter = createVector(
    cos(HALF_PI + rotation) * distance + entryPoint.x,
    sin(HALF_PI + rotation) * distance + entryPoint.y
  );

  // Exact angle from spiralCenter back to entryPoint
  let startAngle = atan2(entryPoint.y - spiralCenter.y, entryPoint.x - spiralCenter.x);

  for (let theta = 0; theta <= totalAngle; theta += step) {
    let r = distance * (1 - (theta / totalAngle) * 0.85);
    let angle = startAngle + theta;

    buffer.point(
      spiralCenter.x + cos(angle) * r,
      spiralCenter.y + sin(angle) * r
    );
  }
}
