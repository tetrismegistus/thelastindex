function findTerminals(sentence) {
  const terminals = new Set();
  for (let i = 0; i < sentence.length; i++) {
    if (sentence[i] !== 'F') continue;
    // scan ahead: is there another F before we close or end?
    let isTip = true;
    for (let j = i + 1; j < sentence.length; j++) {
      if (sentence[j] === 'F') { isTip = false; break; }
      if (sentence[j] === ']') break;
    }
    if (isTip) terminals.add(i);
  }
  return terminals;
}

function centroid(a, b, c) {
  return createVector(
    (a.x + b.x + c.x) / 3,
    (a.y + b.y + c.y) / 3
  );
}


// in general I want to quantize the drawing space. 
function snapToGrid(i) {
  return i;
}


function circleIntersections(O1, r1, O2, r2) {
  let d = dist(O1.x, O1.y, O2.x, O2.y);

  // No intersection guard
  if (d > r1 + r2 || d < abs(r1 - r2) || d === 0) return null;

  // Distance from O1 to the radical axis
  let a = (r1 * r1 - r2 * r2 + d * d) / (2 * d);
  // Height of the intersection points above the O1-O2 line
  let h = sqrt(r1 * r1 - a * a);

  // Midpoint on O1-O2 line
  let mx = O1.x + a * (O2.x - O1.x) / d;
  let my = O1.y + a * (O2.y - O1.y) / d;

  // Perpendicular offset
  let dx = h * (O2.y - O1.y) / d;
  let dy = h * (O2.x - O1.x) / d;

  return [
    createVector(mx + dx, my - dy),  // c1
    createVector(mx - dx, my + dy),  // c2
  ];
}

function getCoordsOfArc(center, degree1, degree2, radius) {
  let resolution = 0.1; // radians; smaller = smoother
  let points = [];
  for (let i = degree1; i <= degree2; i += resolution) {
    let x = center.x + cos(i) * radius;
    let y = center.y + sin(i) * radius;
    points.push(createVector(x, y));
  }
  return points;
}


