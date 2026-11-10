# Radiance — Quality and Release Assurance

## Product surface

The homepage and direct Light Room are identical self-contained HTML applications. GitHub Pages publishes only those pages and the necessary Pages build marker. No unrelated applications or navigation paths are part of the active release.

## Verification gates

- SHA-256 source manifest and exact Content Security Policy hashes
- Six geometric forms, six palettes, pattern/pace/glow controls
- All-form linear continuity: equal full-cycle row spacing, persistent low-intensity carrier lines, sampled coverage checks across motion phases
- Pause/Resume, fullscreen, hidden controls, keyboard restoration and motion preferences
- Hidden-tab pausing and offline single-file operation
- Passing source CI, identical homepage/Light Room and GitHub Pages deployment

## Important limitations

Browser render quality, actual frame-rate, photosensitivity safety and device temperatures require physical browser/display testing. The project is a visual environment, not a medical device. Any therapeutic claims need separate rigorous study.

The optional `_headers` source file applies only on supporting hosts; it does not demonstrate that GitHub Pages sends those response headers.
