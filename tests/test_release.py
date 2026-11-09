import base64
import hashlib
import json
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
        actual.discard('.github/workflows/verify.yml')
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
        self.assertIn('prefers-reduced-motion:reduce',html)

    def test_json_formats(self):
        for path in ROOT.rglob('*.json'):
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding='utf-8'))
        for path in ROOT.rglob('*.webmanifest'):
            json.loads(path.read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
