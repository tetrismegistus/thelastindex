"""
artgal.py — Pelican plugin that generates a gallery page from images/artgal/.

Drop this file in your plugins/ directory and add 'artgal' to PLUGINS in pelicanconf.py.

Config options (pelicanconf.py):
    ARTGAL_DIR = 'artgal'           # subdirectory under content/images/
    ARTGAL_SAVE_AS = 'gallery.html' # output path
    ARTGAL_TITLE = 'Gallery'        # page <title> / h1
"""

import os
import json
import logging
from pathlib import Path

from pelican import signals

try:
    from PIL import Image as PilImage

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

logger = logging.getLogger(__name__)

# Shared state populated during generate_gallery
_all_images = []  # list of dicts: {url, w, h, alt}
_artgal_dir = "artgal"
_siteurl = ""

GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link href='http://fonts.googleapis.com/css?family=Open+Sans:400,600' rel='stylesheet' type='text/css'/>
  <link href='http://fonts.googleapis.com/css?family=Merriweather:300' rel='stylesheet' type='text/css'/>
  <link rel="stylesheet" type="text/css" href="/theme/css/icons.css"/>
  <link rel="stylesheet" type="text/css" href="/theme/css/styles.css"/>
  <style>
    /* ── Gallery grid ── */
    .artgal-grid {{
      column-count: 3;
      column-gap: 6px;
      padding: 0;
      margin: 0;
    }}
    @media (max-width: 900px)  {{ .artgal-grid {{ column-count: 2; }} }}
    @media (max-width: 500px)  {{ .artgal-grid {{ column-count: 1; }} }}

    .artgal-item {{
      break-inside: avoid;
      margin-bottom: 6px;
      cursor: pointer;
    }}

    /* aspect-ratio set inline per image — browser reserves space before load */
    .artgal-item img {{
      display: block;
      width: 100%;
      height: auto;
      opacity: 0;
      transition: opacity 0.4s ease;
      max-width: 100% !important;
      margin: 0 !important;
    }}

    .artgal-item img.loaded {{
      opacity: 1;
    }}

    /* ── Dialog lightbox ── */
    body.lightbox-open {{
      overflow: hidden;
      position: fixed;
      width: 100%;
    }}

    dialog.artgal-lightbox {{
      border: none;
      background: rgba(0,0,0,0.92);
      padding: 0;
      max-width: 100vw;
      max-height: 100vh;
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    dialog.artgal-lightbox::backdrop {{
      background: rgba(0,0,0,0.85);
    }}

    dialog.artgal-lightbox img {{
      max-width: 95vw;
      max-height: 95vh;
      object-fit: contain;
      display: block;
      margin: 0 !important;
      aspect-ratio: unset !important;
    }}

    /* hide img when src is empty — prevents broken image flash on close */
    dialog.artgal-lightbox img:not([src]),
    dialog.artgal-lightbox img[src=""] {{
      display: none;
    }}

    dialog.artgal-lightbox .close-btn {{
      position: fixed;
      top: 1rem;
      right: 1.2rem;
      background: none;
      border: none;
      color: #fff;
      font-size: 2rem;
      cursor: pointer;
      line-height: 1;
      opacity: 0.7;
      padding: 0.5rem;
    }}
    dialog.artgal-lightbox .close-btn:hover {{ opacity: 1; }}
  </style>
</head>
<body>
  <header class="siteheader">
    <div class="sitebanner">
      <h1><a class="sitetitle nodec" href="/">{siteurl_title}</a></h1>
    </div>
  </header>

  <section class="content">
    <h2 style="max-width:800px;margin:1em auto 0.5em auto;font-family:Merriweather;font-weight:300;">{title}</h2>
    <div class="artgal-grid">
{image_items}
    </div>
  </section>

  <dialog class="artgal-lightbox" id="artgal-dialog">
    <button class="close-btn" id="artgal-close" aria-label="Close">&times;</button>
    <img id="artgal-lightbox-img" src="" alt=""/>
  </dialog>

  <script>
    // Fade in each image as it loads
    document.querySelectorAll('.artgal-item img').forEach(function(img) {{
      if (img.complete) {{
        img.classList.add('loaded');
      }} else {{
        img.addEventListener('load', function() {{ img.classList.add('loaded'); }});
      }}
    }});

    var dialog = document.getElementById('artgal-dialog');
    var lbImg  = document.getElementById('artgal-lightbox-img');

    function openLightbox(src, alt) {{
      lbImg.src = src;
      lbImg.alt = alt;
      document.body.classList.add('lightbox-open');
      dialog.showModal();
    }}
    

    dialog.addEventListener('close', function() {{
      lbImg.src = '';
      dialog.style.display = '';
    }});

    // Escape key is handled natively by <dialog> but we need to clean up body class
    dialog.addEventListener('cancel', function() {{
      document.body.classList.remove('lightbox-open');
    }});

    document.querySelectorAll('.artgal-item').forEach(function(item) {{
      item.addEventListener('click', function() {{
        openLightbox(item.dataset.full, item.dataset.alt);
      }});
    }});

    document.getElementById('artgal-close').addEventListener('click', closeLightbox);

    // Click backdrop to close
    dialog.addEventListener('click', function(e) {{
      if (e.target === dialog) {{
        closeLightbox();
      }}
    }});

    // Deep link: open image from URL hash on page load
    function openFromHash() {{
      var hash = window.location.hash.slice(1);
      if (!hash) return;
      var item = document.querySelector('.artgal-item[data-full*="' + hash + '"]');
      if (item) openLightbox(item.dataset.full, item.dataset.alt);
    }}

    // Update hash when opening/closing
    var _origOpen = openLightbox;
    openLightbox = function(src, alt) {{
      var filename = src.split('/').pop();
      history.replaceState(null, '', '#' + filename);
      _origOpen(src, alt);
    }};

    function closeLightbox() {{
      history.replaceState(null, '', ' ');
      dialog.style.display = 'none';
      dialog.close();
      document.body.classList.remove('lightbox-open');
    }}

    window.addEventListener('load', openFromHash);
  </script>
</body>
</html>"""

ITEM_TEMPLATE = '      <div class="artgal-item" data-full="{url}" data-alt="{alt}"><img src="{url}" alt="{alt}" width="{w}" height="{h}" style="aspect-ratio:{w}/{h}" loading="lazy"/></div>'
ITEM_TEMPLATE_NODIM = '      <div class="artgal-item" data-full="{url}" data-alt="{alt}"><img src="{url}" alt="{alt}" loading="lazy"/></div>'


def get_dimensions(path):
    """Return (width, height) for an image using Pillow, or (0, 0) on failure."""
    if not HAS_PILLOW:
        return 0, 0
    try:
        with PilImage.open(path) as im:
            return im.size  # (width, height)
    except Exception as e:
        logger.warning("artgal: could not read dimensions for %s: %s", path, e)
        return 0, 0


def generate_gallery(generator):
    settings = generator.settings

    artgal_dir = settings.get("ARTGAL_DIR", "artgal")
    save_as = settings.get("ARTGAL_SAVE_AS", "gallery.html")
    title = settings.get("ARTGAL_TITLE", "Gallery")
    siteurl = settings.get("SITEURL", "")
    sitename = settings.get("SITENAME", "Home")
    content_path = settings.get("PATH", "content")

    candidates = [
        os.path.join(content_path, "images", artgal_dir),
        os.path.join(content_path, artgal_dir),
    ]
    img_dir = None
    for c in candidates:
        if os.path.isdir(c):
            img_dir = c
            break

    if img_dir is None:
        logger.warning("artgal: could not find image directory for %s", artgal_dir)
        return

    exts = {".webp", ".jpg", ".jpeg", ".png", ".gif"}
    paths = sorted(p for p in Path(img_dir).iterdir() if p.suffix.lower() in exts)

    if not paths:
        logger.warning("artgal: no images found in %s", img_dir)
        return

    if HAS_PILLOW:
        logger.info("artgal: reading dimensions for %d images...", len(paths))
    else:
        logger.warning("artgal: Pillow not available, skipping dimension reads")

    image_data = []
    for p in paths:
        w, h = get_dimensions(str(p))
        url = "{}/images/{}/{}".format(siteurl, artgal_dir, p.name)
        alt = p.stem.replace("_", " ").replace("-", " ")
        image_data.append({"url": url, "w": w, "h": h, "alt": alt})

    # Store for context injection
    global _all_images, _artgal_dir, _siteurl
    _all_images = image_data
    _artgal_dir = artgal_dir
    _siteurl = siteurl

    items = []
    for d in image_data:
        if d["w"] and d["h"]:
            items.append(ITEM_TEMPLATE.format(**d))
        else:
            items.append(ITEM_TEMPLATE_NODIM.format(**d))

    html = GALLERY_TEMPLATE.format(
        title=title,
        siteurl_title=sitename,
        image_items="\n".join(items),
    )

    output_path = settings.get("OUTPUT_PATH", "output")
    out_file = os.path.join(output_path, save_as)
    if os.path.dirname(out_file):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("artgal: wrote gallery to %s", out_file)


def add_sample_to_context(generator):
    """Inject artgal_all JSON string and gallery URL into generator context."""
    if not _all_images:
        return
    generator.context["artgal_all"] = json.dumps([d["url"] for d in _all_images])
    generator.context["artgal_url"] = "{}/gallery.html".format(_siteurl)


def register():
    signals.article_generator_finalized.connect(generate_gallery)
    signals.article_generator_finalized.connect(add_sample_to_context)
