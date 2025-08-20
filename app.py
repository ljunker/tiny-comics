from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, abort, render_template_string, url_for

app = Flask(__name__)

# Where you’ll put your images (PNG/JPG/WebP). Name them in order, e.g.:
# 2025-08-01-first.png, 2025-08-05-bugfix.jpg ...
COMICS_DIR = Path("static/comics")

def list_comics():
    if not COMICS_DIR.exists():
        return []
    # Sort by filename (works great with date-prefix naming) and filter images
    imgs = [p for p in COMICS_DIR.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}]
    return sorted(imgs, key=lambda p: p.name)

def get_title(p: Path) -> str:
    base = p.stem
    # nice title from "YYYY-MM-DD-my-cool-joke" -> "My Cool Joke"
    parts = base.split("-", 3)
    name = parts[-1] if len(parts) >= 4 and parts[0].isdigit() else base
    return name.replace("-", " ").strip().title()

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title }} — Comics</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root { --fg:#111; --bg:#fafafa; --muted:#777; }
    @media (prefers-color-scheme: dark) {
      :root { --fg:#eee; --bg:#0e0f11; --muted:#9aa0a6; }
    }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif; color:var(--fg); background:var(--bg);}
    header, footer { max-width: 900px; margin: 16px auto; padding: 0 16px; }
    header h1 { margin: 12px 0 4px; font-size: 1.2rem; }
    header .sub { color: var(--muted); font-size: .95rem; }
    main { max-width: 900px; margin: 0 auto; padding: 0 16px 32px; }
    .comic { display:flex; justify-content:center; align-items:center; }
    .comic img { width:100%; height:auto; max-height: 85vh; object-fit: contain; border-radius: 8px; }
    nav { display:flex; justify-content:space-between; align-items:center; gap:8px; margin: 14px 0; }
    .btn {
      text-decoration:none; padding:8px 12px; border:1px solid var(--muted);
      border-radius:8px; color:var(--fg);
    }
    .btn[aria-disabled="true"] { opacity: .4; pointer-events:none; }
    .meta { color: var(--muted); font-size: .9rem; }
    .grid { display:grid; grid-template-columns: 1fr auto 1fr; align-items:center; gap:8px; }
    .center { text-align:center; }
    .sr { position:absolute; left:-10000px; }
  </style>
</head>
<body>
  <header>
    <h1>{{ title }}</h1>
    <div class="sub">{{ idx+1 }} / {{ total }}</div>
  </header>

  <main>
    <nav class="grid" aria-label="pagination top">
      <a class="btn" href="{{ prev_url }}" aria-disabled="{{ 'true' if prev_url is none else 'false' }}">← Prev</a>
      <div class="center">
        <a class="btn" href="{{ first_url }}" title="First">⏮</a>
        <a class="btn" href="{{ latest_url }}" title="Latest">⏭</a>
      </div>
      <a class="btn" href="{{ next_url }}" aria-disabled="{{ 'true' if next_url is none else 'false' }}">Next →</a>
    </nav>

    <div class="comic">
      <img src="{{ img_url }}" alt="{{ title }}">
    </div>

    <footer>
      <nav class="grid" aria-label="pagination bottom">
        <a class="btn" href="{{ prev_url }}" aria-disabled="{{ 'true' if prev_url is none else 'false' }}">← Prev</a>
        <div class="center">
          <a class="btn" href="{{ first_url }}" title="First">⏮</a>
          <a class="btn" href="{{ latest_url }}" title="Latest">⏭</a>
        </div>
        <a class="btn" href="{{ next_url }}" aria-disabled="{{ 'true' if next_url is none else 'false' }}">Next →</a>
      </nav>
      <div class="meta">File: {{ filename }}</div>
    </footer>
  </main>

  <script>
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' && {{ 'true' if prev_url else 'false' }}) { window.location = "{{ prev_url or '' }}"; }
      if (e.key === 'ArrowRight' && {{ 'true' if next_url else 'false' }}) { window.location = "{{ next_url or '' }}"; }
      if (e.key.toLowerCase() === 'l') { window.location = "{{ latest_url }}"; }
      if (e.key.toLowerCase() === 'f') { window.location = "{{ first_url }}"; }
    });

    // Basic mobile swipe (left/right)
    let sx = 0, sy = 0;
    window.addEventListener('touchstart', e => { sx = e.touches[0].clientX; sy = e.touches[0].clientY; });
    window.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - sx;
      const dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 40 && Math.abs(dy) < 40) {
        if (dx > 0 && {{ 'true' if prev_url else 'false' }}) window.location="{{ prev_url or '' }}";
        if (dx < 0 && {{ 'true' if next_url else 'false' }}) window.location="{{ next_url or '' }}";
      }
    });
  </script>
</body>
</html>
"""

def render_index(i: int):
    comics = list_comics()
    if not comics:
        return "<h1>No comics yet</h1><p>Put images into <code>static/comics/</code>.</p>"
    if i < 0 or i >= len(comics):
        abort(404)
    img = comics[i]
    ctx = {
        "idx": i,
        "total": len(comics),
        "filename": img.name,
        "title": get_title(img),
        "img_url": url_for("static", filename=f"comics/{img.name}"),
        "first_url": url_for("first"),
        "latest_url": url_for("latest"),
        "prev_url": url_for("by_index", i=i-1) if i > 0 else None,
        "next_url": url_for("by_index", i=i+1) if i < len(comics)-1 else None,
    }
    return render_template_string(TEMPLATE, **ctx)

@app.route("/")
def latest():
    comics = list_comics()
    if not comics:
        return "<h1>No comics yet</h1><p>Put images into <code>static/comics/</code>.</p>"
    return render_index(len(comics)-1)

@app.route("/first")
def first():
    return render_index(0)

@app.route("/c/<int:i>")
def by_index(i: int):
    return render_index(i)

# Optional: /r/5 redirects to a comic (nice for stable links in posts)
@app.route("/r/<int:i>")
def redirectable(i: int):
    return render_index(i)

if __name__ == "__main__":
    # Ensure folder exists on first run
    COMICS_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

