import base64
import hashlib
import json
import math
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]

class ReleaseTest(unittest.TestCase):
    def test_manifest(self):
        manifest=(ROOT/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines()
        scanned=set()
        for row in manifest:
            m=re.fullmatch(r'([0-9a-f]{64})  ([^\n]+)',row)
            self.assertIsNotNone(m,row)
            digest,path=m.groups()
            self.assertNotIn(path,scanned)
            scanned.add(path)
            self.assertTrue((ROOT/path).is_file(),path)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts}
        actual.discard('MANIFEST.sha256')
        actual={p for p in actual if '__pycache__' not in p}
        self.assertEqual(actual,scanned)

    def test_no_stale_cross_repo_readme(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        for disallowed in ('other repositor','private original','private history','rebirth', 'portfolio showcase'):
            self.assertNotIn(disallowed,readme.lower())

    def test_static_html_local_links(self):
        for path in ROOT.rglob('*.html'):
            text=path.read_text(encoding='utf-8')
            self.assertNotRegex(text,r'<script[^>]+src=[\"\']https?://')
            for link in re.findall(r'(?:src|href)=[\"\']([^\"\']+)[\"\']',text):
                if link.startswith(('data:','#','mailto:','tel:')) or urlparse(link).scheme or link.startswith('//'):
                    continue
                link=unquote(link.split('?',1)[0].split('#',1)[0])
                if not link or link.startswith('/'):
                    continue
                self.assertTrue((path.parent/link).is_file(),f'{path.name}: {link}')

    def test_inline_csp_hashes(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        meta=re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>',html)
        self.assertIsNotNone(meta,'Missing browser CSP')
        headers=(ROOT/'_headers').read_text(encoding='utf-8')
        for element,directive in (('style','style-src'),('script','script-src')):
            blocks=re.findall(fr'<{element}>(.*?)</{element}>',html,re.S)
            self.assertEqual(len(blocks),1,f'Exactly one inline {element} expected')
            digest=base64.b64encode(hashlib.sha256(blocks[0].encode('utf-8')).digest()).decode('ascii')
            policy=f"{directive} 'sha256-{digest}'"
            self.assertIn(policy,meta.group(0),f'Browser CSP stale for {element}')
            self.assertIn(policy,headers,f'Host CSP stale for {element}')

    def test_light_room_csp(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        meta=re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>',html)
        self.assertIsNotNone(meta,'Light Room missing CSP')
        self.assertIn("connect-src 'none'",meta.group(0))
        for element,directive in (('style','style-src'),('script','script-src')):
            blocks=re.findall(fr'<{element}>(.*?)</{element}>',html,re.S)
            self.assertEqual(len(blocks),1,f'Exactly one {element} block required')
            digest=base64.b64encode(hashlib.sha256(blocks[0].encode('utf-8')).digest()).decode('ascii')
            self.assertIn(f"{directive} 'sha256-{digest}'",meta.group(0))
        self.assertIn('download="Radiance-Light-Room.html"',html)
        self.assertIn('id="offline-download"',html)
        self.assertIn("document.getElementById('offline-download').hidden=true",html)
        self.assertIn('prefers-reduced-motion:reduce',html)


    def test_light_pattern_controls(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        self.assertIn('data-pattern="linear" aria-pressed="true"',html)
        self.assertIn('data-color="spectrum" aria-pressed="true"',html)
        self.assertIn("color='spectrum'",html)
        self.assertIn("spectrum:['#23dcff'",html)
        self.assertIn('data-pattern="organic" aria-pressed="false"',html)
        self.assertIn("pattern='linear'",html)
        self.assertIn("room.classList.add('pattern-linear')",html)
        self.assertIn("pattern==='linear'",html)
        self.assertIn('prefers-reduced-motion:reduce',html)
        self.assertIn('syncField(allowed)',html)

    def test_speed_and_geometry(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        self.assertIn('data-speed="surge" aria-pressed="true"',html)
        self.assertIn("speed==='surge'?65",html)
        self.assertIn("speed==='surge'?4.25",html)
        self.assertIn('speed-surge.moving',html)
        self.assertIn('prefers-reduced-motion:reduce',html)
        self.assertIn('syncField(allowed)',html)
        section=html.split('<g class="scene" id="scene-bloom">')[1].split('<g class="scene" id="scene-prism">')[0]
        circles=re.findall(r'<circle[^>]+>',section)
        seed=[tag for tag in circles if 'r="110"' in tag]
        self.assertEqual(len(seed),7)
        self.assertAlmostEqual(360-264.737,110*math.sqrt(3)/2,places=2)
        self.assertAlmostEqual(455.263-360,110*math.sqrt(3)/2,places=2)
        self.assertIn('title="Seed of Life',html)


    def test_light_room_polished_release(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        self.assertIn('<small>LIGHT ROOM</small>',html)
        self.assertNotIn('SILENT BY DESIGN',html)
        self.assertNotIn('ORIGINAL VISUAL ART',html)
        self.assertIn('id="restore-ui"',html)
        self.assertIn('fullBtn.disabled=true',html)
        self.assertIn('Fullscreen unavailable',html)
        self.assertIn('data-speed="surge"',html)
        self.assertIn('data-color="spectrum"',html)
        self.assertIn('data-pattern="organic"',html)
        self.assertIn('document.addEventListener(\'visibilitychange\',updateMotion)',html)


    def test_balanced_controls_and_immersive_restore(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('class="dock-row"'),2)
        self.assertIn('class="dock-actions"',html)
        self.assertNotIn('class="dock-bottom"',html)
        self.assertIn('>Linear</button>',html)
        self.assertIn('>Waves</button>',html)
        self.assertNotIn('data-speed="drift"',html)
        self.assertIn('data-power="radiant" aria-pressed="true"',html)
        self.assertIn('data-speed="surge" aria-pressed="true"',html)
        self.assertIn("power='radiant'",html)
        self.assertIn("speed='surge'",html)
        self.assertIn('room.quiet-mode .minimize{display:block;opacity:0',html)
        self.assertIn('room.addEventListener(\'pointermove\',revealQuiet)',html)
        self.assertIn('restoreButton.addEventListener(\'focus\',revealQuiet)',html)
        self.assertIn("window.setTimeout(hideQuietAffordance,1800)",html)
        self.assertIn("if(e.key==='Escape'",html)

    def test_precise_additional_geometry(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        form=[re.search(r'data-scene="([^"]+)"',t).group(1)
              for t in re.findall(r'<button[^>]*data-scene="[^"]+"[^>]*>',html)]
        self.assertEqual(form,['pyramid','halo','bloom','flower','cube','prism'])
        flower=html.split('<g class="scene" id="scene-flower">')[1].split('<g class="scene" id="scene-cube">')[0]
        self.assertEqual(len(re.findall(r'<circle[^>]*r="81"',flower)),19)
        centers=[]
        for tag in re.findall(r'<circle[^>]*r="81"[^>]*>',flower):
            centers.append((float(re.search(r'cx="([^"]+)"',tag).group(1)),
                            float(re.search(r'cy="([^"]+)"',tag).group(1))))
        self.assertEqual(len(set(centers)),19)
        self.assertIn((360,270),centers)
        self.assertAlmostEqual(min(math.dist(centers[0],p) for p in centers[1:]),81,places=2)
        for field in ('field-flower','field-cube-top','field-cube-left','field-cube-right'):
            self.assertIn('id="'+field+'"',html)
        for clip in ('flower-field-area','cube-top-area','cube-left-area','cube-right-area'):
            self.assertIn('id="'+clip+'"',html)


    def test_flow_hierarchy_and_pace_presets(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        second=html.split('class="dock-row"')[2].split('class="dock-actions"')[0]
        self.assertLess(second.index('>Pattern</span>'),second.index('>Pace</span>'))
        self.assertLess(second.index('>Pace</span>'),second.index('>Glow</span>'))
        self.assertIn('>Linear</button>',second)
        self.assertIn('>Waves</button>',second)
        self.assertIn("speed==='surge'?4.25:speed==='vivid'?2.4:1.45",html)
        self.assertIn('surface-down 7s linear infinite',html)
        self.assertIn('.room.speed-vivid.moving .stream-left .stream-tracks{animation-duration:4.3s}',html)
        self.assertIn('.room.speed-surge.moving .stream-left .stream-tracks{animation-duration:2.6s}',html)
        self.assertIn('room.speed-surge.moving .flower-geometry{animation-duration:25s}',html)
        self.assertIn("speed='surge'",html)
        self.assertIn("power='radiant'",html)


    def test_public_entry_and_no_legacy_navigation(self):
        home=(ROOT/'index.html').read_bytes()
        room=(ROOT/'light-room.html').read_bytes()
        self.assertEqual(home,room,'Both URLs must open the full Light Room')
        html=home.decode('utf-8')
        self.assertIn('<h1>Stay in the Glow</h1>',html)
        self.assertIn('<title>Radiance — Light Room</title>',html)
        self.assertNotIn('http-equiv="refresh"',html)
        self.assertNotIn('id="back-studio"',html)
        self.assertNotIn('<p class="help"',html)
        self.assertNotIn('<p class="subtitle"',html)
        self.assertIn('id="offline-download"',html)
        self.assertIn('<meta property="og:title" content="Radiance — Light Room">',html)

    def test_public_source_inventory(self):
        expected={'index.html','light-room.html','README.md','QUALITY.md',
                  '_headers','MANIFEST.sha256','tests/test_release.py',
                  'tests/browser-smoke.cjs','.github/workflows/verify.yml'}
        files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
               if p.is_file() and '__pycache__' not in p.parts
               and '.git' not in p.parts}
        self.assertEqual(files,expected)

    def test_light_room_has_no_network_calls(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
        for forbidden in ('fetch(', 'XMLHttpRequest', 'WebSocket(', 'sendBeacon(', 'serviceWorker.register'):
            self.assertNotIn(forbidden,script)
        self.assertIn('prefers-reduced-motion:reduce',html)
        self.assertIn('visibilitychange',html)


    def test_continuous_linear_signal_for_every_form(self):
        html=(ROOT/'light-room.html').read_text(encoding='utf-8')
        self.assertIn('var spacing=690/paths.length;',html)
        self.assertIn('var fieldPaths={},fieldCarriers={}',html)
        self.assertIn('for(var band=0;band<3;band++)',html)
        self.assertIn('for(var q=0;q<34;q++)',html)
        self.assertIn(".room.pattern-linear .light-carrier",html)
        self.assertIn(".room.pattern-organic .light-carrier{opacity:0}",html)
        self.assertNotIn('var offset=i*13.2+',html)
        for total,low,high,minimum in [
            (52,74,423,20),(52,77,463,23),(52,56,484,22),
            (40,34,506,23),(30,132,310,6),(30,221,470,8)]:
            spacing=690/total
            for phase in range(0,690,5):
                visible=sum(low<=((i*spacing+phase)%690)-92<=high
                            for i in range(total))
                self.assertGreaterEqual(visible,minimum,
                    f'{total} rows cover [{low},{high}] at phase {phase}')


    def test_public_first_impression_metadata(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('<h1>Stay in the Glow</h1>'),1)
        self.assertIn('<meta name="viewport"',html)
        self.assertIn('<meta name="description"',html)
        self.assertIn('<meta property="og:title" content="Radiance — Light Room">',html)
        self.assertIn('<meta property="og:description"',html)
        self.assertIn('<link rel="canonical" href="https://luckygithub777.github.io/radiance-light-and-form/">',html)
        self.assertNotIn('http-equiv="refresh"',html)
        self.assertNotIn('studio.html',html.lower())
        self.assertEqual(html,(ROOT/'light-room.html').read_text(encoding='utf-8'))


    def test_first_paint_and_public_privacy(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('--hue-a:#f2bb63;--hue-b:#6ddafd;',html)
        self.assertIn('class="room power-radiant palette-spectrum pattern-linear speed-surge"',html)
        self.assertIn('var scene=\'pyramid\',color=\'spectrum\',power=\'radiant\',motion=true,speed=\'surge\',pattern=\'linear\'',html)
        self.assertIn('<meta name="referrer" content="no-referrer">',html)
        self.assertNotIn('<script src=',html)
        self.assertNotIn('<link rel="stylesheet" href=',html)
        self.assertEqual(html,(ROOT/'light-room.html').read_text(encoding='utf-8'))
        for name in ('README.md','QUALITY.md','index.html','light-room.html'):
            contents=(ROOT/name).read_text(encoding='utf-8')
            self.assertNotRegex(contents,r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
            self.assertNotRegex(contents,r'(?i)github_pat_[a-z0-9_]{30,}|ghp_[a-z0-9]{25,}|AKIA[0-9A-Z]{16}|-----BEGIN PRIVATE KEY-----')
            self.assertNotIn('studio.html',contents.lower())

    def test_json_formats(self):
        for path in ROOT.rglob('*.json'):
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding='utf-8'))
        for path in ROOT.rglob('*.webmanifest'):
            json.loads(path.read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
