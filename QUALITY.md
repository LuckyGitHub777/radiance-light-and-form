# Radiance — Release verification

## Experience contract
The public root `/` serves the full Light Room directly: `index.html` and `light-room.html` are byte-identical, with no redirect or Studio landing page. The original Studio remains separately accessible at `studio.html`. The Light Room is a self-contained offline-capable HTML file, with no tracking or server-side runtime.

## Automated release gates
1. Python tests: manifest and asset integrity, route/link validity, browser and HTTP CSP hashes, colors, controls, geometry, reduced motion and offline behavior.
2. Node smoke: six forms, all control families, Pause/Resume, fullscreen supported and unsupported, hidden controls/reveal/fade/Escape, inactive-tab pausing, reduced motion, HTTPS and local file use.
3. Verified `main` commit, source-to-Pages blob equality, and successful GitHub Pages deployment.

## Limits before claiming full physical validation
- Test the exact public URL in a real signed-out desktop and mobile browser.
- Observe performance, frame pacing, temperature and memory on supported hardware, especially older laptops.
- Measure actual frame-by-frame photosensitive flashing thresholds; the absence of intentional strobes is not equivalent to certification.
- Assess perceived well-being with neutral, voluntary user observations and document any discomfort.
- Compare to permitted TLS videos frame by frame; screenshots alone cannot establish the same speed or colors.

## Scientific scope
Browser animation cannot verify or reproduce multiscreen photonic collisions, scalar fields or medical treatment effects. Clinically studied light-based therapies depend on measurable illumination, wavelength and exposure protocols. Radiance may provide enjoyment, reflection or perceived relaxation; clinical efficacy needs separate controlled research.
