// node beam6.js OUTDIR: the beam on a wall for round 5's pick with the LED ring turned 0, 30 and 45 deg, one pair of
// doors closed to 50 deg at a time; raw RGBA images for compose_beam.py
const fs = require("fs"), path = require("path");
const D5 = require("./door5.js");
const out = process.argv[2] || "out/r6";
const K = JSON.parse(fs.readFileSync("out/r5/door5-constants.json"));
const M = D5.make(K);
const ps = M.pieces({ length: 40, width: 71, cut: 90 });
const N = 200, opts = { z0: 15.92, lensR: 8.75, winR: 9.3, faceDz: 1.5, sigma: 12.7, n: N, fov: 40, samples: 48 };
const ring = (rot) => [[90, 0], [210, 1], [330, 2]].map(([a, ch]) => [12 * Math.cos(((a + rot) * Math.PI) / 180), 12 * Math.sin(((a + rot) * Math.PI) / 180), ch]);
for (const rot of [0, 30, 45]) for (const [name, top, side] of [["tb50", 50, 90], ["s50", 90, 50]]) {
  const t = Date.now();
  const img = M.beam(ps, top, side, Object.assign({ leds: ring(rot) }, opts));
  fs.writeFileSync(path.join(out, `beam-rot${rot}-${name}.rgba`), Buffer.from(D5.tone(img, N).buffer));
  console.log(rot, name, Date.now() - t, "ms");
}
