Title: All Work and no Play
Date: 2023-08-16 00:00
Category: post
card_image: /images/awanp.webp
hero_image: /images/awanp.webp
hero_caption: Photo credit: <a href="https://thelastindex.com"><strong>TheLastIndex</strong></a>
hero_text: I can only describe it as a mix of scantron, dot matrix printer, and typewriter aesthetic. Sometimes the simplest things grab my attention.

Take an arrayList and fill it with floating point numbers that have a standard distribution around the value of width/2, and spread them out a little by multiplying. These obviously will represent x coordinates.

```java
ArrayList<Float> xPoints = new ArrayList<Float>();

void setup() {
  size(2048, 2048);
  colorMode(HSB, 360, 100, 100, 1);

  for (int j = 0; j < 200; j++) {
    xPoints.add(width/2 + randomGaussian() * 300);
  }
}
```

Select a nice background [color](https://www.color-hex.com/color/e0c9a6) vaguely reminiscent of old paper.

Choose a random spacing intervall (step), and choose a set range in the y axis with which to “jitter” things along the x axis (mark1 and mark2). This will move a chunk of rows from the rest of the output, looking like some sort of paper alignment related error.

Traverse the y axis drawing small circles of slightly varying size and strokeweight at the points previously stored in our arrayList.

```java
void draw() {

  background(#E0C9A6);
  float mark1 = random(100, 150);
  float mark2 = random(200, 250);
  float step = random(10, 20);

  for (float y = 50; y < height - 50; y+=step) {
    step = random(10, 20);
    for (float xP : xPoints) {
      strokeWeight(random(.1, 2));
      stroke(360, 100, random(30));
      noFill();
      float offset = random(-2, 2);
      if (y > mark1 && y < mark2) {
        offset += random(10, 20);
      }
      circle(xP + offset, y, random(2, 3));
    }
  }

  noLoop();
}
```

I don’t know, I just find the results pleasing. Not everything needs to be complicated.

![final output](/images/final.webp)
