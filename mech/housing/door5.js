/* door5.js: round 5's door as the review page builds it from its sliders. The plate's outline (as round5.py's), the
   door as thin convex pieces, where the four doors stand at given angles, which doors collide, and how much of the
   lenses' light gets past them. Plain JavaScript without three.js, so node can run it against the CAD checks
   (test_door5.js). K holds round5.py's constants().
   Frame: the top door, closed, as in the CAD: z is the beam axis (front +z), the top door's pin along x at y = P,
   z = ZP. Door k (0 top, 1 left, 2 bottom, 3 right) is the top door turned k * 90 deg about z, swung about its pin. */
(function (root) {
  "use strict";

  function make(K) {
    const P = K.P, ZP = K.ZP, D = K.D, T = K.T, r = K.RIN, b = K.B, XF = K.XF;
    const zb = ZP + D, RAD = Math.PI / 180, EPS = 0.02;

    // ------------------------------------------------------------ outline
    function rawHalf(p) {
      const c = Math.cos(p.cut * RAD);
      const wsh = Math.max(p.width / 2, b);
      const half = [[b, P], [b, P - 5], [wsh, P - K.SHOULDER]];
      let wtip = wsh - (p.length - K.SHOULDER) * c, yk = null;
      if (wtip < K.W_MIN) {
        yk = P - (K.SHOULDER + (wsh - K.W_MIN) / c);
        half.push([K.W_MIN, yk]); wtip = K.W_MIN;
      }
      half.push([wtip, P - p.length]);
      return { half, wsh, wtip, yk };
    }
    function fillet(A, C, B, rad, n) {
      const ux = A[0] - C[0], uy = A[1] - C[1], vx = B[0] - C[0], vy = B[1] - C[1];
      const lu = Math.hypot(ux, uy), lv = Math.hypot(vx, vy);
      const u = [ux / lu, uy / lu], v = [vx / lv, vy / lv];
      const ang = Math.acos(Math.max(-1, Math.min(1, u[0] * v[0] + u[1] * v[1])));
      const dt = Math.min(rad / Math.tan(ang / 2), 0.45 * Math.min(lu, lv));
      const rr = dt * Math.tan(ang / 2);
      const bi = [u[0] + v[0], u[1] + v[1]], lb = Math.hypot(bi[0], bi[1]);
      const cx = C[0] + (bi[0] / lb) * (rr / Math.sin(ang / 2)), cy = C[1] + (bi[1] / lb) * (rr / Math.sin(ang / 2));
      const t1 = [C[0] + u[0] * dt, C[1] + u[1] * dt], t2 = [C[0] + v[0] * dt, C[1] + v[1] * dt];
      let a1 = Math.atan2(t1[1] - cy, t1[0] - cx), a2 = Math.atan2(t2[1] - cy, t2[0] - cx);
      let da = a2 - a1; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI;
      const out = [];
      for (let i = 0; i <= n; i++) { const a = a1 + (da * i) / n; out.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
      return out;
    }
    // the plate's outline with the tip corners rounded, clockwise seen from the front, and its convex pieces
    function shape(p) {
      const { half, wsh, wtip, yk } = rawHalf(p);
      const n = half.length, tip = half[n - 1], pre = half[n - 2];
      const right = fillet(pre, tip, [-tip[0], tip[1]], K.FILLET, 5);
      const left = right.map(([x, y]) => [-x, y]).reverse();
      const outline = half.slice(0, n - 1).concat(right, left, half.slice(0, n - 1).map(([x, y]) => [-x, y]).reverse());
      const strip = [[-b, P], [b, P], [b, P - 5], [-b, P - 5]];
      const mir = (pts) => pts.map(([x, y]) => [-x, y]).reverse();
      let body;
      if (yk === null) body = [[[b, P - 5], [wsh, P - K.SHOULDER]].concat(right, left, mir([[b, P - 5], [wsh, P - K.SHOULDER]]))];
      else body = [[[b, P - 5], [wsh, P - K.SHOULDER], [K.W_MIN, yk]].concat(mir([[b, P - 5], [wsh, P - K.SHOULDER], [K.W_MIN, yk]])),
                   [[K.W_MIN, yk]].concat(right, left, [[-K.W_MIN, yk]])];
      return { outline, plates: [strip].concat(body), wsh, wtip, clamped: yk !== null };
    }

    // ------------------------------------------------------------ the door as thin convex pieces (mid-surfaces)
    function piece(o, eu, ev, poly, t, tag) {
      const n = [eu[1] * ev[2] - eu[2] * ev[1], eu[2] * ev[0] - eu[0] * ev[2], eu[0] * ev[1] - eu[1] * ev[0]];
      return { o, eu, ev, n, poly, t, tag };
    }
    function quadAlong(a, bpt, side, lo, hi, tag) {        // a strip from point a to bpt (3-D), widened along unit side
      const d = [bpt[0] - a[0], bpt[1] - a[1], bpt[2] - a[2]], L = Math.hypot(d[0], d[1], d[2]);
      return piece(a, side, [d[0] / L, d[1] / L, d[2] / L], [[lo, 0], [hi, 0], [hi, L], [lo, L]], T, tag);
    }
    const hinge = (function () {
      const out = [], rm = r + T / 2, be = K.BETA * RAD;
      const q = (a) => [0, P + rm * Math.sin(a), zb - r + rm * Math.cos(a)];
      const steps = [0, be / 2, be];
      for (let i = 0; i < 2; i++) out.push(quadAlong(q(steps[i]), q(steps[i + 1]), [1, 0, 0], -XF, XF, "foot"));
      const e = q(be), f = [0, e[1] + K.FOOT * Math.cos(be), e[2] - K.FOOT * Math.sin(be)];
      out.push(quadAlong(e, f, [1, 0, 0], -XF, XF, "foot"));
      for (const sg of [-1, 1]) {
        const x = sg * (b + rm);
        const yz = (pts) => piece([x, 0, 0], [0, 1, 0], [0, 0, 1], pts, T, "ear");
        out.push(yz([[P - 5, ZP], [P, ZP], [P, zb - r], [P - 5, zb - r]]));
        const disc = [];
        for (let i = 0; i < 16; i++) { const a = (i / 16) * 2 * Math.PI; disc.push([P + K.EAR_R * Math.cos(a), ZP + K.EAR_R * Math.sin(a)]); }
        out.push(yz(disc));
        const w = (a) => [sg * (b + rm * Math.sin(a)), 0, zb - r + rm * Math.cos(a)];
        for (let i = 0; i < 2; i++) out.push(quadAlong(w((i * Math.PI) / 4), w(((i + 1) * Math.PI) / 4), [0, 1, 0], P - 5, P, "ear"));
      }
      return out;
    })();
    function pieces(p) {
      const s = shape(p);
      const plates = s.plates.map((poly) => piece([0, 0, zb + T / 2], [1, 0, 0], [0, 1, 0], poly, T, "plate"));
      return plates.concat(hinge);
    }

    // ------------------------------------------------------------ where door k stands
    // world = Rz(k 90) (pivot + Rx(-phi) (p - pivot)); returned as a 3x3 matrix m and an offset c: world = m p + c
    function pose(k, phi) {
      const a = -phi * RAD, ca = Math.cos(a), sa = Math.sin(a);
      const g = k * 90 * RAD, cg = Math.round(Math.cos(g)), sg = Math.round(Math.sin(g));
      const rx = [1, 0, 0, 0, ca, -sa, 0, sa, ca];
      const rz = [cg, -sg, 0, sg, cg, 0, 0, 0, 1];
      const m = mul(rz, rx);
      const pv = [0, P, ZP];
      const rpv = apply(rx, pv);
      const c = apply(rz, [pv[0] - rpv[0], pv[1] - rpv[1], pv[2] - rpv[2]]);
      return { m, c };
    }
    function mul(A, B) {
      const o = new Array(9);
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) o[3 * i + j] = A[3 * i] * B[j] + A[3 * i + 1] * B[3 + j] + A[3 * i + 2] * B[6 + j];
      return o;
    }
    function apply(m, v) { return [m[0] * v[0] + m[1] * v[1] + m[2] * v[2], m[3] * v[0] + m[4] * v[1] + m[5] * v[2], m[6] * v[0] + m[7] * v[1] + m[8] * v[2]]; }
    const angleOf = (k, top, side) => (k % 2 === 0 ? top : side);

    // ------------------------------------------------------------ collisions: SAT between thin convex prisms
    function worldPrisms(ps, ps_pose) {
      const { m, c } = ps_pose;
      return ps.map((pc) => {
        const n = apply(m, pc.n), h = pc.t / 2;
        const ring = pc.poly.map(([u, v]) => {
          const l = [pc.o[0] + u * pc.eu[0] + v * pc.ev[0], pc.o[1] + u * pc.eu[1] + v * pc.ev[1], pc.o[2] + u * pc.eu[2] + v * pc.ev[2]];
          const w = apply(m, l); return [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
        });
        const verts = [];
        ring.forEach((q) => { verts.push([q[0] + h * n[0], q[1] + h * n[1], q[2] + h * n[2]], [q[0] - h * n[0], q[1] - h * n[1], q[2] - h * n[2]]); });
        const edges = ring.map((q, i) => { const s = ring[(i + 1) % ring.length]; return [s[0] - q[0], s[1] - q[1], s[2] - q[2]]; });
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        verts.forEach((q) => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], q[i]); hi[i] = Math.max(hi[i], q[i]); } });
        return { verts, edges, n, lo, hi, tag: pc.tag };
      });
    }
    const cross = (a, c) => [a[1] * c[2] - a[2] * c[1], a[2] * c[0] - a[0] * c[2], a[0] * c[1] - a[1] * c[0]];
    function separated(A, B, ax) {
      const l = Math.hypot(ax[0], ax[1], ax[2]);
      if (l < 1e-9) return false;
      const x = ax[0] / l, y = ax[1] / l, z = ax[2] / l;
      let a0 = Infinity, a1 = -Infinity, b0 = Infinity, b1 = -Infinity;
      for (const q of A.verts) { const d = q[0] * x + q[1] * y + q[2] * z; if (d < a0) a0 = d; if (d > a1) a1 = d; }
      for (const q of B.verts) { const d = q[0] * x + q[1] * y + q[2] * z; if (d < b0) b0 = d; if (d > b1) b1 = d; }
      return a1 < b0 + EPS || b1 < a0 + EPS;
    }
    function overlap(A, B) {
      for (let i = 0; i < 3; i++) if (A.hi[i] < B.lo[i] + EPS || B.hi[i] < A.lo[i] + EPS) return false;
      if (separated(A, B, A.n) || separated(A, B, B.n)) return false;
      for (const e of A.edges) if (separated(A, B, cross(e, A.n))) return false;
      for (const e of B.edges) if (separated(A, B, cross(e, B.n))) return false;
      if (separated(A, B, cross(A.n, B.n))) return false;
      for (const e of A.edges) if (separated(A, B, cross(e, B.n))) return false;
      for (const e of B.edges) if (separated(A, B, cross(A.n, e))) return false;
      for (const e of A.edges) for (const f of B.edges) if (separated(A, B, cross(e, f))) return false;
      return true;
    }
    function boxOf(prisms) {
      const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
      prisms.forEach((q) => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], q.lo[i]); hi[i] = Math.max(hi[i], q.hi[i]); } });
      return { lo, hi };
    }
    const PAIRS = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]];
    // which pairs of doors collide with the top & bottom doors at top deg and the sides at side deg
    function collide(ps, top, side) {
      const W = [0, 1, 2, 3].map((k) => { const pr = worldPrisms(ps, pose(k, angleOf(k, top, side))); return { pr, box: boxOf(pr) }; });
      const hits = [];
      for (const [i, j] of PAIRS) {
        const A = W[i], B = W[j];
        let hit = false;
        for (let a = 0; a < 3 && !hit; a++) if (A.box.hi[a] < B.box.lo[a] || B.box.hi[a] < A.box.lo[a]) hit = null;
        if (hit === null) continue;
        outer: for (const pa of A.pr) for (const pb of B.pr) if (overlap(pa, pb)) { hit = true; break outer; }
        if (hit) hits.push([i, j]);
      }
      return hits;
    }

    // ------------------------------------------------------------ light: the page's rays against the four doors
    const SETS = {};                                // ray sets by name: one per arrangement of the lenses
    function setRays(points, rays, meta, key) {   // points: [x, y] per source point; rays: {i, d: [dx, dy, dz], f}
      const n = rays.length, o = new Float32Array(3 * n), d = new Float32Array(3 * n), f = new Uint8Array(n);
      rays.forEach((ry, k) => {
        o[3 * k] = points[ry.i][0]; o[3 * k + 1] = points[ry.i][1]; o[3 * k + 2] = meta.z;
        const l = Math.hypot(ry.d[0], ry.d[1], ry.d[2]);
        d[3 * k] = ry.d[0] / l; d[3 * k + 1] = ry.d[1] / l; d[3 * k + 2] = ry.d[2] / l; f[k] = ry.f;
      });
      SETS[key || "default"] = { n, o, d, f, total: meta.rays };
    }
    function framePieces(ps) {                      // per piece: plane, in-plane axes and the convex polygon's edge lines
      return ps.map((pc) => {
        const poly = pc.poly, m = poly.length, lines = [];
        let area = 0;
        for (let i = 0; i < m; i++) { const a = poly[i], c = poly[(i + 1) % m]; area += a[0] * c[1] - c[0] * a[1]; }
        const s = area > 0 ? 1 : -1;
        for (let i = 0; i < m; i++) {
          const a = poly[i], c = poly[(i + 1) % m];
          const nx = s * (c[1] - a[1]), ny = -s * (c[0] - a[0]);      // outward edge normal
          lines.push([nx, ny, nx * a[0] + ny * a[1]]);
        }
        const d0 = pc.n[0] * pc.o[0] + pc.n[1] * pc.o[1] + pc.n[2] * pc.o[2];
        return { o: pc.o, eu: pc.eu, ev: pc.ev, n: pc.n, faces: [d0 - pc.t / 2, d0 + pc.t / 2], lines };      // both faces of the sheet
      });
    }
    function sphereOf(ps) {
      const pts = [];
      ps.forEach((pc) => pc.poly.forEach(([u, v]) => pts.push([pc.o[0] + u * pc.eu[0] + v * pc.ev[0], pc.o[1] + u * pc.eu[1] + v * pc.ev[1], pc.o[2] + u * pc.eu[2] + v * pc.ev[2]])));
      const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
      pts.forEach((q) => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], q[i]); hi[i] = Math.max(hi[i], q[i]); } });
      const c = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2];
      let rr = 0; pts.forEach((q) => { rr = Math.max(rr, Math.hypot(q[0] - c[0], q[1] - c[1], q[2] - c[2])); });
      return { c, r: rr + 1 };
    }
    function hitsDoor(F, sph, ox, oy, oz, dx, dy, dz) {
      const wx = sph.c[0] - ox, wy = sph.c[1] - oy, wz = sph.c[2] - oz;
      const tc = wx * dx + wy * dy + wz * dz;
      if (tc < -sph.r) return false;
      const dd = wx * wx + wy * wy + wz * wz - tc * tc;
      if (dd > sph.r * sph.r) return false;
      for (const pc of F) {
        const den = pc.n[0] * dx + pc.n[1] * dy + pc.n[2] * dz;
        if (den > -1e-9 && den < 1e-9) continue;
        const no = pc.n[0] * ox + pc.n[1] * oy + pc.n[2] * oz;
        for (const f0 of pc.faces) {
          const t = (f0 - no) / den;
          if (t <= 1e-6) continue;
          const qx = ox + t * dx - pc.o[0], qy = oy + t * dy - pc.o[1], qz = oz + t * dz - pc.o[2];
          const u = qx * pc.eu[0] + qy * pc.eu[1] + qz * pc.eu[2], v = qx * pc.ev[0] + qy * pc.ev[1] + qz * pc.ev[2];
          let inside = true;
          for (const ln of pc.lines) if (ln[0] * u + ln[1] * v > ln[2]) { inside = false; break; }
          if (inside) return true;
        }
      }
      return false;
    }
    // the share of the lenses' light (worst case) that gets out the sides, and past 45 deg off the axis
    // sample: also return up to that many of the rays that get out the sides, as segments from the lens face to where
    // they leave the box |x|, |y| <= 40, z <= 62
    function light(ps, top, side, sample, key) {
      const RAYS = SETS[key || "default"];
      if (!RAYS) return null;
      const F = framePieces(ps), sph = sphereOf(ps);
      const inv = [0, 1, 2, 3].map((k) => {
        const { m, c } = pose(k, angleOf(k, top, side));
        const mt = [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]];         // the inverse of a rotation
        return { mt, c };
      });
      const { n, o, d, f } = RAYS;
      let sideN = 0, wideN = 0;
      const out = sample ? [] : null;
      for (let k = 0; k < n; k++) {
        const ox = o[3 * k], oy = o[3 * k + 1], oz = o[3 * k + 2], dx = d[3 * k], dy = d[3 * k + 1], dz = d[3 * k + 2];
        let blocked = false;
        for (let j = 0; j < 4 && !blocked; j++) {
          const { mt, c } = inv[j];
          const px = ox - c[0], py = oy - c[1], pz = oz - c[2];
          const lx = mt[0] * px + mt[1] * py + mt[2] * pz, ly = mt[3] * px + mt[4] * py + mt[5] * pz, lz = mt[6] * px + mt[7] * py + mt[8] * pz;
          const ex = mt[0] * dx + mt[1] * dy + mt[2] * dz, ey = mt[3] * dx + mt[4] * dy + mt[5] * dz, ez = mt[6] * dx + mt[7] * dy + mt[8] * dz;
          blocked = hitsDoor(F, sph, lx, ly, lz, ex, ey, ez);
        }
        if (!blocked) { if (f[k] & 1) { sideN++; if (out) out.push(k); } if (f[k] & 2) wideN++; }
      }
      const res = { side: sideN / RAYS.total, wide: wideN / RAYS.total };
      if (out) {
        const step = Math.max(1, out.length / sample), seg = [];
        for (let q = 0; q < out.length && seg.length < 6 * sample; q += step) {
          const k = out[Math.floor(q)], oo = [o[3 * k], o[3 * k + 1], o[3 * k + 2]], dd = [d[3 * k], d[3 * k + 1], d[3 * k + 2]];
          const lo = [-40, -40, -75], hi = [40, 40, 62];
          let t = Infinity;
          for (let i = 0; i < 3; i++) if (Math.abs(dd[i]) > 1e-9) { const tt = ((dd[i] > 0 ? hi[i] : lo[i]) - oo[i]) / dd[i]; if (tt > 0 && tt < t) t = tt; }
          seg.push(oo[0], oo[1], oo[2], oo[0] + t * dd[0], oo[1] + t * dd[1], oo[2] + t * dd[2]);
        }
        res.seg = seg;
      }
      return res;
    }

    // ------------------------------------------------------------ the beam on a wall far away
    // Each lens face is a disc of radius lensR at z0, every point of it sending the lens's beam (a gaussian of sigma deg
    // about the axis) in every direction; the hood's window (radius winR, faceDz in front of the lens) and the doors cut
    // it. For each direction on an n x n grid spanning +-fov deg, each LED's share of its face that still sees out,
    // times the beam, times cos^3 for a flat wall: Float32 RGB, row 0 at the top, columns as seen from behind the lamp
    // (looking along the beam, +x is on the left).
    function beam(ps, top, side, o) {
      const F = framePieces(ps), sph = sphereOf(ps);
      const inv = [0, 1, 2, 3].map((k) => {
        const { m, c } = pose(k, angleOf(k, top, side));
        return { mt: [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]], c };
      });
      const N = o.n, h = Math.tan(o.fov * RAD), S = o.samples, out = new Float32Array(3 * N * N), sig = o.sigma * RAD;
      const sp = [];
      for (let i = 0; i < S; i++) { const rr = Math.sqrt((i + 0.5) / S), a = i * 2.399963229728653; sp.push([rr * Math.cos(a), rr * Math.sin(a)]); }
      for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
        const u = -((((i + 0.5) / N) * 2 - 1) * h), v = (1 - ((j + 0.5) / N) * 2) * h;
        const l = Math.hypot(u, v, 1), dx = u / l, dy = v / l, dz = 1 / l;
        const th = Math.acos(dz), prof = Math.exp((-th * th) / (2 * sig * sig)) * dz * dz * dz;
        if (prof < 2e-3) continue;
        const hs = Math.sin(i * 12.9898 + j * 78.233) * 43758.5453, rot = (hs - Math.floor(hs)) * 2 * Math.PI;
        const cr = Math.cos(rot), sr = Math.sin(rot);
        for (const [lx, ly, ch] of o.leds) {
          let pass = 0;
          for (const [px, py] of sp) {
            const qx = lx + o.lensR * (px * cr - py * sr), qy = ly + o.lensR * (px * sr + py * cr);
            const wx = qx + (o.faceDz * dx) / dz - lx, wy = qy + (o.faceDz * dy) / dz - ly;
            if (wx * wx + wy * wy > o.winR * o.winR) continue;
            let blocked = false;
            for (let k = 0; k < 4 && !blocked; k++) {
              const { mt, c } = inv[k];
              const px0 = qx - c[0], py0 = qy - c[1], pz0 = o.z0 - c[2];
              blocked = hitsDoor(F, sph, mt[0] * px0 + mt[1] * py0 + mt[2] * pz0, mt[3] * px0 + mt[4] * py0 + mt[5] * pz0, mt[6] * px0 + mt[7] * py0 + mt[8] * pz0,
                mt[0] * dx + mt[1] * dy + mt[2] * dz, mt[3] * dx + mt[4] * dy + mt[5] * dz, mt[6] * dx + mt[7] * dy + mt[8] * dz);
            }
            if (!blocked) pass++;
          }
          out[3 * (j * N + i) + ch] = (prof * pass) / S;
        }
      }
      return out;
    }

    // ------------------------------------------------------------ what a shape allows
    function summary(p) {
      const ps = pieces(p);
      const clear = (t, s) => collide(ps, t, s).length === 0;
      const scanDown = (f) => { let a = 90; if (!f(90)) return null; while (a > 0 && f(a - 1)) a--; return a; };
      const all = scanDown((a) => clear(a, a));
      const pair = scanDown((a) => clear(a, 90));
      let flat = null;                                   // with one pair flat, the other pair's lowest angle (down from 90)
      if (pair === 0) { flat = 90; if (!clear(0, 90)) flat = null; else while (flat > 0 && clear(0, flat - 1)) flat--; }
      // why the pair stops: only its own tips meeting (a closed roof), or a neighbour
      const tipsOnly = (hits) => hits.length > 0 && hits.every(([i, j]) => (i + j) % 2 === 0);
      const pairTips = pair !== null && pair > 0 ? tipsOnly(collide(ps, pair - 1, 90)) : false;
      return { all, pair, flat, pairTips, at90: clear(90, 90) };
    }
    // every step deg for both pairs: "x" where neighbours collide, "t" where only a pair's own tips meet
    function grid(p, step) {
      const ps = pieces(p), out = {};
      for (let t = 0; t <= 180; t += step) for (let s = 0; s <= 180; s += step) {
        const h = collide(ps, t, s);
        if (h.length) out[t + "," + s] = h.every(([i, j]) => (i + j) % 2 === 0) ? "t" : "x";
      }
      return out;
    }
    return { K, zb, shape, pieces, pose, collide, light, beam, setRays, summary, grid, hinge };
  }

  // decode the page's spill5.bin (see spill_rays.py)
  function decodeRays(buf, meta) {
    const dv = new DataView(buf.buffer || buf, buf.byteOffset || 0);
    const points = [];
    for (let i = 0; i < meta.points; i++) points.push([dv.getInt16(4 * i, true) / 100, dv.getInt16(4 * i + 2, true) / 100]);
    const base = 4 * meta.points, rays = [];
    for (let k = 0; k < meta.kept; k++) {
      const q = base + 10 * k;
      rays.push({ i: dv.getUint16(q, true), d: [dv.getInt16(q + 2, true), dv.getInt16(q + 4, true), dv.getInt16(q + 6, true)], f: dv.getUint8(q + 8) });
    }
    return { points, rays };
  }

  // the beam image as RGBA bytes: each LED's light in its own channel, 1 - exp(-k I), slightly lifted
  function tone(img, n, k) {
    const out = new Uint8ClampedArray(4 * n * n), kk = k || 2.6;
    for (let p = 0; p < n * n; p++) {
      for (let c = 0; c < 3; c++) out[4 * p + c] = 255 * Math.pow(1 - Math.exp(-kk * img[3 * p + c]), 0.8);
      out[4 * p + 3] = 255;
    }
    return out;
  }

  const api = { make, decodeRays, tone };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.DOOR5 = api;
})(typeof self !== "undefined" ? self : this);
