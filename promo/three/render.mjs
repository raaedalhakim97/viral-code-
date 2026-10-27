// render.mjs — deterministic three.js -> mp4.
//   node render.mjs scene_euler.js out.mp4 [width height]
// Serves the scene over a local http server, drives it frame by frame in
// headless Chromium (software WebGL), reads each frame off the canvas and
// pipes it to ffmpeg. Time is an argument, not a clock, so frame N is always
// the same image and the video is exactly duration*fps frames.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { chromium } from 'playwright-core';

const [sceneFile, outFile, w = '1080', h = '1920', fStart = '0', fEnd = ''] = process.argv.slice(2);
const STILLS = process.env.STILLS ? process.env.STILLS.split(',').map(Number) : null;   // seconds -> PNGs
const W = +w, H = +h;
const root = path.dirname(new URL(import.meta.url).pathname);
const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json' };

const html = `<!doctype html><meta charset=utf-8>
<style>html,body{margin:0;background:#000}canvas{display:block}</style>
<script type="importmap">{"imports":{
 "three":"/node_modules/three/build/three.module.js",
 "three/addons/":"/node_modules/three/examples/jsm/"}}</script>
<canvas id=c></canvas>
<script type=module>
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
const mod = await import('/${path.basename(sceneFile)}');
const W=${W}, H=${H};
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, preserveDrawingBuffer:true});
renderer.setPixelRatio(1); renderer.setSize(W,H,false);
const s = mod.buildAsync ? await mod.buildAsync(THREE, W, H) : mod.build(THREE, W, H);   // async: scenes that load assets
if (s.shadows) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; }
const composer = new EffectComposer(renderer);
composer.setSize(W,H);
composer.addPass(new RenderPass(s.scene, s.camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W,H), 0.5, s.bloomRadius ?? 0.4, s.bloomThreshold ?? 0.25);
composer.addPass(bloom);
composer.addPass(new OutputPass());
window.__info = { fps: mod.FPS, duration: mod.DURATION };
window.__frame = (t, png) => { s.update(t); if (s.bloom !== undefined) bloom.strength = s.bloom; composer.render();
  if (s.hud) { renderer.autoClear = false; renderer.clearDepth(); renderer.render(s.hud, s.hudCam); renderer.autoClear = true; }
  return png ? canvas.toDataURL('image/png').slice(22) : canvas.toDataURL('image/jpeg', 0.95).slice(23); };
window.__facts = s.facts || null;
window.__ready = true;
</script>`;

const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  if (u === '/' || u === '/index.html') { res.writeHead(200, { 'content-type': 'text/html' }); return res.end(html); }
  const f = path.join(root, u);
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--use-angle=swiftshader', '--use-gl=angle', '--enable-unsafe-swiftshader',
         '--ignore-gpu-blocklist', '--enable-webgl'],
});
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', (e) => { console.error('PAGE ERROR:', e.message); });
page.on('console', (m) => { if (m.type() === 'error') console.error('console:', m.text()); });
await page.goto(`http://localhost:${port}/`);
await page.waitForFunction('window.__ready === true', null, { timeout: 120000 });
const { fps, duration } = await page.evaluate('window.__info');
const facts = await page.evaluate('window.__facts'); if (facts) console.log('FACTS', JSON.stringify(facts));
const frames = Math.round(fps * duration);
if (STILLS) {
  fs.mkdirSync(outFile, { recursive: true });
  for (const st of STILLS) { const b64 = await page.evaluate(([tt]) => window.__frame(tt, true), [st]);
    fs.writeFileSync(path.join(outFile, `t${String(st).padStart(6, '0')}.png`), Buffer.from(b64, 'base64')); console.log('still', st); }
  await browser.close(); server.close(); process.exit(0);
}
const f0 = +fStart, f1 = fEnd === '' ? frames : +fEnd;

const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', outFile],
  { stdio: ['pipe', 'inherit', 'inherit'] });

const t0 = Date.now();
for (let i = f0; i < f1; i++) {
  const b64 = await page.evaluate((t) => window.__frame(t), i / fps);
  if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % 30 === 0) console.log(`frame ${i}/${f1}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close(); server.close();
console.log(`done ${f1 - f0} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${outFile}`);
