// Daniel Shiffman
// Code for: https://youtu.be/E1B4UE1B4UoSQMFwoSQMFw

// variables: A B
// axiom: A
// rules: (A → AB), (B → A)
var angle;
var axiom = "F";
var sentence = axiom;


var rules = [];

const chooser = new Chooser();
const capChooser = new Chooser();

let bufferSize = 2500;
var len = bufferSize * .5;
let gridRes = 1;
let snakiness = 20;
let buffer;

let strokeColor = '#FCECC9';

rules[0] = {
  a: "F",
  b: "F[-FF[+F][-F]]",
}

function generate() {
  
    len *= 0.8; 
    var nextSentence = "";
    for (var i = 0; i < sentence.length; i++) {
      var current = sentence.charAt(i);
      var found = false;
      for (var j = 0; j < rules.length; j++) {
        if (current == rules[j].a) {
          found = true;
          nextSentence += rules[j].b;
          nextSentence += rules[j].c;
          break;
        }
      }
      if (!found) {
        nextSentence += current;
      }
    }
    sentence = nextSentence;
    turtle();
  

}



function turtle() {
  buffer.background('#445E93');
  buffer.resetMatrix();
  buffer.translate(bufferSize / 2, bufferSize * 0.95);
  buffer.stroke(strokeColor);
  let depth = 0;


  const terminals = findTerminals(sentence); 
  
  for (var i = 0; i < sentence.length; i++) {
    var current = sentence.charAt(i);
    
    angle += .00001;
    // in the loop:
    if (current == "F") {
      let p1 = createVector(0, 0);
      let p2 = createVector(0, -len);
      if (terminals.has(i)) {
        // always the same cap treatment
        chooser.pick(p1, p2);
        endWithSpiral(p1, p2); // or whatever you want as the signature
      } else {
        chooser.pick(p1, p2);
        capChooser.pick(p1, p2);
      }
      buffer.translate(0, -len);
  
    } else if (current == "[") {
      depth++;
      buffer.push();
    } else if (current == "]") {
      depth--;
      buffer.pop();  
    } else if (current == "+") {
      buffer.rotate(angle);
    } else if (current == "-") {
      buffer.rotate(-angle)
    } 
  }
  
  
}

function setup() {
  createCanvas(windowHeight, windowHeight);
  buffer = createGraphics(bufferSize, bufferSize);
  angle = radians(TWO_PI);
  background(51);

  
  chooser
    .register((p1, p2) => { drawLine(p1, p2); }, 1)
    .register((p1, p2) => { drawHorseShoe(p1, p2); }, 1)
    .register((p1, p2) => { drawArrow(p1, p2); }, 1)
    .register((p1, p2) => { drawULine(p1, p2); }, 1)
    .register((p1, p2) => { drawCrosses(p1, p2); }, 1);
  
  capChooser
    .register((p1, p2) => endWithArrowEndCaps(p1, p2), 1)
    .register((p1, p2) => capWithCircles(p1, p2), 1)
    .register((p1, p2) => endWithCrescentCaps(p1, p2), 1)
    .register((p1, p2) => endWithSpiral(p1, p2), 1)
    .register((p1, p2) => endWithOrnamentedCross(p1, p2), 1);
  
  
  turtle();
  var button = createButton("generate");
  var saved = createButton("save");
  button.mousePressed(generate);
  saved.mousePressed(saveButton);
}

function draw() {
  background(255);
  image(buffer, 0, 0, width, width);
}

function keyPressed() {
  if (key === 's' || key === 'S') {
    save(buffer, 'lsigil.png');
  }
}


function saveButton() {
  save(buffer, 'lsigil.png');
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}
