# Radiance — Quality and Release Assurance

## Product surface

The homepage and direct Light Room are identical self-contained HTML applications. GitHub Pages publishes only those pages and the necessary Pages build marker. No unrelated applications or navigation paths are part of the active release.

## Verification gates

- SHA-256 source manifest and exact Content Security Policy hashes
- Six geometric forms, six palettes, pattern/pace/glow controls
- All-form linear continuity: equal full-cycle row spacing, persistent low-intensity carrier lines, sampled coverage checks across motion phases
- Pause/Resume, fullscreen, hidden controls, keyboard restoration and motion preferences
- Hidden-tab pausing and offline single-file operation
- Passing checks on pull requests, verified `main`, identical homepage/Light Room and a successful GitHub Pages deployment

## Important limitations

Browser render quality, actual frame-rate, photosensitivity safety and device temperatures require physical browser/display testing. The project is a visual environment, not a medical device. Any therapeutic claims need separate rigorous study.

The optional `_headers` source file applies only on supporting hosts; it does not demonstrate that GitHub Pages sends those response headers.

## Release operation

The runtime has no backend, database, third-party scripts, scheduled jobs or package dependencies. The verification workflow runs on pull requests, on changes to `main`, or on demand, with read-only repository permissions and a pinned checkout action.

The current public website is published from the `gh-pages` branch. After a source change passes verification, production still requires publishing the two **identical** HTML files (`index.html` and `light-room.html`) plus `.nojekyll` to that branch and checking the resulting Pages deployment. Do not treat passing source CI as automatic publication. This existing branch publishing method is intentionally preserved until a separately verified migration to GitHub Actions publishing is authorized.

The public URL could not be directly rendered or HTTP-crawled from the audit environment; deployment status and repository-file parity do not substitute for a physical browser test. GitHub branch protection is enabled on `main`, but the exact required checks and administrator-bypass settings could not be read with the present integration.
