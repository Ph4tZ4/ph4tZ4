# Profile assets

The banners and motion strip are custom artwork for this profile. All images are
stored in this repository so the README does not depend on an image-generation API.

`profile-motion.gif` is a looping animation. The README's `<picture>` element uses
`profile-motion-still.png` when the viewer prefers reduced motion.

Regenerate the strip with `python3 tools/generate_profile_motion.py` using Pillow
and the macOS Arial font. The script checks the frame count, size, and motion.

Brand icon SVGs in `icons/` come from
[Simple Icons](https://github.com/simple-icons/simple-icons/tree/develop/icons),
retrieved on 2026-10-25, with brand colors applied locally. Their
[CC0 license](icons/LICENSE.md) is included. Brand names and logos belong to their
respective owners.

## GitHub graphs

`graphs/` contains generated SVG charts with no runtime dependency on an image
service. Regenerate with `python3 tools/generate_profile_graphs.py` (Python standard
library only). Run checks with `python3 -m unittest discover -s tests`.

- Language mix counts the primary language of each public repository owned by
  Ph4tZ4, excluding forks and repositories without a detected language. It does
  not measure lines of code or proficiency.
- Monthly activity and the heatmap use contributions visible on the public GitHub
  calendar, without authentication. Monthly activity shows the latest 12 calendar
  months; the current month is partial.
- The calendar HTML is not a versioned API. If it changes, generation fails and
  preserves the existing images rather than replacing them with incorrect data.
- `.github/workflows/profile-graphs.yml` refreshes charts daily after the workflow
  reaches `main`. It requires permission to push generated assets; branch
  protection may prevent updates. It uses no personal access token or secrets.
