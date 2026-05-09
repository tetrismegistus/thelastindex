// endings -- these functions should tell how to end a pair of vectors


function endWithArrowEndCap(p1, p2) {
  let dx = p2.x - p1.x;
  let dy = p2.y - p1.y;
  let lineLength = sqrt(dx * dx + dy * dy);
  let angle = atan2(dy, dx) + TWO_PI;  
  arrowEndCap(p2, angle, lineLength * 0.1);
}



function endWithSpiral(p1, p2) {
  let dx = p2.x - p1.x;
  let dy = p2.y - p1.y;
  let lineLength = sqrt(dx * dx + dy * dy);
  let angle = atan2(dy, dx) + TWO_PI;  
  spiralCap(p2, angle, lineLength * 0.1);
}


let crescentScale = .1;
function endWithCrescentCap(p1, p2) {
  let dx = p1.x - p2.x;  // reversed: p1 - p2, not p2 - p1
  let dy = p1.y - p2.y;
  let angle = atan2(dy, dx);  // no + PI
  let lineLength = sqrt(dx * dx + dy * dy);
  crescentEndCap(p2, angle, lineLength * crescentScale);
}

function endWithCrescentCapReversed(p1, p2) {
  let dx = p1.x - p2.x;
  let dy = p1.y - p2.y;
  let angle = atan2(dy, dx) + PI;
  let lineLength = sqrt(dx * dx + dy * dy);
  crescentEndCap(p1, angle, lineLength * crescentScale);
}


function endWithCrescentCaps(p1, p2) {
  endWithCrescentCap(p1, p2);
  endWithCrescentCapReversed(p1, p2);
}

function endWithOrnamentedCross(p1, p2) {
  let dx = p2.x - p1.x;
  let dy = p2.y - p1.y;
  let lineLength = sqrt(dx * dx + dy * dy);
  let angle = atan2(dy, dx) + TWO_PI;
  let nx = dx / lineLength;
  let ny = dy / lineLength;
  let offset = lineLength * 0.03; // tweak this to taste

  let wingBase = {
    x: p2.x - nx * offset,
    y: p2.y - ny * offset
  };
  
  let ornamentType = random(1);
  if (ornamentType < 0.25) {
    arrowEndCap(wingBase, angle - HALF_PI, lineLength * 0.1);
    arrowEndCap(wingBase, angle + HALF_PI, lineLength * 0.1);
    arrowEndCap(p2, angle, lineLength * 0.1);
  } else if (ornamentType < .25) {
    crescentEndCap(wingBase, angle - HALF_PI, lineLength * 0.1);
    crescentEndCap(wingBase, angle + HALF_PI, lineLength * 0.1);
    crescentEndCap(p2, angle, lineLength * 0.1);
    
  } else {
    capWithCircle(wingBase);
    capWithCircle(p2);
  }
  
}


  

function endWithArrowEndCaps(p1, p2) {
  endWithArrowEndCap(p1, p2);
  endWithArrowEndCap(p2, p1);
}
  



