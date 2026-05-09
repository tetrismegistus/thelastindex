// this is the rng for segment generation.  it's weighted.  and vibe coded.  shh

class Chooser {
  constructor() {
    this.choices = [];
  }

  register(fn, weight = 1) {
    this.choices.push({ fn, weight });
    return this; // chainable
  }

pick(...args) {
    const depth = args[args.length - 1]; // depth is last arg
    const total = this.choices.reduce((sum, c, i) => {
      return sum + c.weight * (1 + i * (depth / 10));
    }, 0);
    let r = Math.random() * total;
    let accumulated = 0;
    for (let i = 0; i < this.choices.length; i++) {
      const bias = this.choices[i].weight * (1 + i * (depth / 10));
      accumulated += bias;
      if (r <= accumulated) return this.choices[i].fn(...args);
    }
    return this.choices.at(-1).fn(...args);
  }
}
