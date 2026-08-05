#!/usr/bin/env python3
"""Regenerates index.html (Modularity showcase style, tabbed by region) from manifest.json.
Run from the repo root: python3 generate_index.py
"""
import json
from collections import OrderedDict

with open("manifest.json") as f:
    sites = json.load(f)

# Group sites by region, preserving first-seen region order.
REGION_LABELS = {
    "Wallenpaupack": "Wallenpaupack Area",
    "DelawareValley": "Delaware Valley",
    "HudsonValley": "Hudson Valley",
    "Erie": "Erie Area",
}
REGION_ORDER = ["Wallenpaupack", "DelawareValley", "HudsonValley", "Erie"]

by_region = OrderedDict()
for s in sites:
    region = s.get("region") or "Wallenpaupack"
    by_region.setdefault(region, []).append(s)

# Always show every known region, even ones with zero sites yet, in a stable order;
# append any unexpected regions found in the data after.
ordered_regions = list(REGION_ORDER)
ordered_regions += [r for r in by_region if r not in REGION_ORDER]

def card_html(s):
    search_blob = f"{s['name']} {s['category']} {s['location']}".lower()
    return f'''        <a class="card" href="{s['slug']}/" data-search="{search_blob}">
          <span class="card-tag">{s['category']}</span>
          <h3>{s['name']}</h3>
          <span class="card-loc">{s['location']}</span>
          <span class="card-cta">View Demo <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 7H12M12 7L7.5 2.5M12 7L7.5 11.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        </a>
'''

# "Latest" is a synthetic pseudo-region, always shown first and active by
# default, drawn from whichever sites carry the most recent "added" date.
# Every manifest entry a daily prospecting run appends should include an
# "added": "YYYY-MM-DD" field (in addition to slug/name/location/category/
# region) precisely so this tab keeps working without manual upkeep; entries
# from before this convention existed simply have no "added" field and are
# never eligible to appear here.
dated_sites = [s for s in sites if s.get("added")]
latest_sites = []
if dated_sites:
    latest_date = max(s["added"] for s in dated_sites)
    latest_sites = [s for s in dated_sites if s["added"] == latest_date]
    latest_sites = list(reversed(latest_sites))

tab_defs = []
if latest_sites:
    tab_defs.append(("Latest", "Latest", latest_sites))
for region in ordered_regions:
    # Newest-added first: manifest.json entries are appended in build order,
    # so reversing shows the most recently built sites at the top of every view.
    region_sites = list(reversed(by_region.get(region, [])))
    label = REGION_LABELS.get(region, region)
    tab_defs.append((region, label, region_sites))

tab_buttons = ""
tab_panels = ""
for i, (tab_key, label, region_sites) in enumerate(tab_defs):
    active_btn = " active" if i == 0 else ""
    active_panel = " active" if i == 0 else ""
    tab_buttons += f'''        <button class="tab-btn{active_btn}" data-tab="{tab_key}" role="tab" aria-selected="{"true" if i == 0 else "false"}">
          {label} <span class="tab-count">{len(region_sites)}</span>
        </button>
'''
    if region_sites:
        cards = "".join(card_html(s) for s in region_sites)
    else:
        cards = f'''        <div class="empty-state">
          <p>No demo sites in {label} yet, check back soon.</p>
        </div>
'''
    tab_panels += f'''      <div class="grid tab-panel{active_panel}" data-panel="{tab_key}" role="tabpanel">
{cards}      </div>
'''

count = len(sites)

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Modularity Networks · Client Demo Gallery</title>
<meta name="description" content="A showcase of custom demo websites built by Modularity Networks for local businesses." />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/nevis">
<style>
  :root {{
    --bg: #06101c;
    --bg-soft: #0b1a2e;
    --accent: #3bb8e8;
    --text: rgba(255,255,255,0.92);
    --text-dim: rgba(255,255,255,0.55);
    --border: rgba(59,184,232,0.16);
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: "Inter", system-ui, sans-serif;
    position: relative;
    overflow-x: hidden;
  }}
  body::before {{
    content: "";
    position: fixed;
    inset: 0;
    background-image:
      radial-gradient(rgba(59,184,232,0.35) 1px, transparent 1px),
      radial-gradient(rgba(59,184,232,0.18) 1px, transparent 1px);
    background-size: 140px 140px, 90px 90px;
    background-position: 0 0, 45px 60px;
    opacity: 0.5;
    pointer-events: none;
    z-index: 0;
  }}
  a {{ color: inherit; text-decoration: none; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 0 1.5rem; position: relative; z-index: 1; }}

  header {{
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(6,16,28,0.88);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
  }}
  .nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.5rem;
    max-width: 1120px;
    margin: 0 auto;
  }}
  .brand {{ display: flex; align-items: center; gap: 0.65rem; }}
  .brand-mark {{
    width: 34px; height: 34px;
    border-radius: 50%;
    background: #fff;
    color: var(--bg);
    display: flex; align-items: center; justify-content: center;
    line-height: 1;
    padding-top: 0.1em;
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 900;
    font-size: 1.5rem;
  }}
  .brand-word {{
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    letter-spacing: 0.02em;
    font-size: 1.05rem;
    line-height: 1.1;
  }}
  .brand-word small {{
    display: block;
    font-size: 0.6rem;
    color: var(--accent);
    letter-spacing: 0.16em;
    font-weight: 600;
  }}
  .nav-cta {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--accent);
    color: var(--bg);
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
    padding: 0.55rem 1.1rem;
    border-radius: 100px;
  }}

  .hero {{ padding: 5rem 0 3.5rem; text-align: center; }}
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border: 1px solid var(--border);
    background: rgba(59,184,232,0.06);
    color: var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    padding: 0.4rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.75rem;
  }}
  .badge-dot {{
    width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 8px 1px var(--accent);
  }}
  h1 {{
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 900;
    text-transform: uppercase;
    line-height: 1.02;
    font-size: clamp(2.4rem, 6vw, 4.2rem);
    letter-spacing: 0.01em;
    margin: 0 0 1.4rem;
  }}
  h1 .accent {{ color: var(--accent); }}
  .hero p {{
    max-width: 560px;
    margin: 0 auto 2.25rem;
    color: var(--text-dim);
    font-size: 1.05rem;
    line-height: 1.6;
  }}
  .stats {{
    display: flex;
    justify-content: center;
    gap: clamp(1.5rem, 5vw, 3.5rem);
    flex-wrap: wrap;
  }}
  .stat-num {{
    display: block;
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 900;
    font-size: 1.9rem;
    color: var(--accent);
  }}
  .stat-label {{
    display: block;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 0.15rem;
  }}

  .showcase {{ padding: 1rem 0 6rem; }}
  .section-head {{ text-align: center; margin-bottom: 2.5rem; }}
  .eyebrow {{
    display: block;
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
    font-size: 0.8rem;
    margin-bottom: 0.75rem;
  }}
  .section-head h2 {{
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 900;
    text-transform: uppercase;
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    margin: 0 0 0.9rem;
  }}
  .section-head p {{
    color: var(--text-dim);
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
  }}

  /* ---------- Tabs ---------- */
  .tab-bar {{
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
  }}
  .tab-btn {{
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    letter-spacing: 0.03em;
    font-size: 0.92rem;
    color: var(--text-dim);
    background: rgba(11,26,46,0.85);
    border: 1px solid var(--border);
    padding: 0.65rem 1.3rem;
    border-radius: 100px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  }}
  .tab-btn:hover {{ color: var(--text); border-color: rgba(59,184,232,0.4); }}
  .tab-btn.active {{
    color: var(--bg);
    background: var(--accent);
    border-color: var(--accent);
  }}
  .tab-count {{
    font-family: "Inter", system-ui, sans-serif;
    font-weight: 600;
    font-size: 0.76rem;
    background: rgba(255,255,255,0.14);
    padding: 0.1rem 0.5rem;
    border-radius: 100px;
  }}
  .tab-btn.active .tab-count {{ background: rgba(6,16,28,0.18); }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.25rem;
  }}
  .grid.tab-panel:not(.active) {{ display: none; }}
  .empty-state {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 3.5rem 1rem;
    color: var(--text-dim);
    font-size: 0.98rem;
  }}

  /* ---------- Search ---------- */
  .search-bar {{
    position: relative;
    max-width: 480px;
    margin: 0 auto 1.75rem;
  }}
  .search-icon {{
    position: absolute;
    left: 1.15rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-dim);
    pointer-events: none;
  }}
  .search-input {{
    width: 100%;
    background: rgba(11,26,46,0.85);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 0.85rem 1.4rem 0.85rem 2.75rem;
    color: var(--text);
    font-family: "Inter", system-ui, sans-serif;
    font-size: 0.95rem;
    -webkit-appearance: none;
    appearance: none;
  }}
  .search-input::placeholder {{ color: var(--text-dim); }}
  .search-input:focus-visible {{
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }}
  .search-status {{
    text-align: center;
    color: var(--text-dim);
    font-size: 0.85rem;
    min-height: 1.2em;
    margin: 0 0 1.75rem;
  }}
  .showcase.searching .tab-bar {{ display: none; }}
  /* In search mode, every region's cards flow into ONE shared grid instead of
     each tab-panel keeping its own column tracks (which left ragged gaps
     whenever a panel had few matches). The wrapper becomes the real grid;
     each panel collapses to display:contents so its cards join it directly. */
  .showcase.searching .panels-wrap {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.25rem;
  }}
  .showcase.searching .grid.tab-panel {{
    display: contents;
  }}
  .card.is-hidden,
  .empty-state.is-hidden {{ display: none !important; }}
  .card {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    background: rgba(11,26,46,0.85);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.6rem 1.5rem;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
  }}
  .card:hover {{
    border-color: rgba(59,184,232,0.55);
    transform: translateY(-3px);
    box-shadow: 0 12px 30px -10px rgba(59,184,232,0.25);
  }}
  .card-tag {{
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent);
    background: rgba(59,184,232,0.1);
    border: 1px solid var(--border);
    padding: 0.3rem 0.65rem;
    border-radius: 100px;
    margin-bottom: 1rem;
  }}
  .card h3 {{
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    margin: 0 0 0.3rem;
    letter-spacing: 0.01em;
  }}
  .card-loc {{
    color: var(--text-dim);
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
  }}
  .card-cta {{
    margin-top: auto;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: "Nevis", "Barlow Condensed", "Arial Black", sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
    color: var(--text);
  }}
  .card-cta svg {{ color: var(--accent); }}

  footer {{
    border-top: 1px solid var(--border);
    padding: 2.5rem 0;
    text-align: center;
  }}
  footer p {{
    color: var(--text-dim);
    font-size: 0.85rem;
    margin: 0.3rem 0;
  }}
  footer a.footer-link {{ color: var(--accent); }}
</style>
</head>
<body>

  <header>
    <div class="nav">
      <div class="brand">
        <span class="brand-mark">M</span>
        <span class="brand-word">MODULARITY<small>DEMO GALLERY</small></span>
      </div>
      <a class="nav-cta" href="https://modularityhosting.com/contact" target="_blank" rel="noopener">CONTACT US &rarr;</a>
    </div>
  </header>

  <main class="wrap">
    <section class="hero">
      <span class="badge"><span class="badge-dot"></span> Client Demo Gallery &middot; Modularity Networks</span>
      <h1>We Built You A Website.<br><span class="accent">Take A Look.</span></h1>
      <p>You didn't have one yet, so we put one together to show you what's possible. Free to preview, no obligation either way, if you like it, it's yours, just pay for hosting.</p>
      <div class="stats">
        <div class="stat"><span class="stat-num">{count}</span><span class="stat-label">Local Businesses</span></div>
        <div class="stat"><span class="stat-num">Free</span><span class="stat-label">To Preview</span></div>
        <div class="stat"><span class="stat-num">No</span><span class="stat-label">Obligation</span></div>
      </div>
    </section>

    <section class="showcase">
      <div class="section-head">
        <span class="eyebrow">The Work</span>
        <h2>Find Your Business.</h2>
        <p>Click any business below to see its live demo site, and let us know what you think.</p>
      </div>
      <div class="search-bar">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.6"/><path d="M11.2 11.2L14.5 14.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
        <input type="search" id="site-search" class="search-input" placeholder="Search all businesses by name, category, or town..." aria-label="Search all demo sites across every area" autocomplete="off">
      </div>
      <p class="search-status" id="search-status" aria-live="polite"></p>
      <div class="tab-bar" role="tablist">
{tab_buttons}      </div>
      <div class="panels-wrap">
{tab_panels}      </div>
    </section>
  </main>

  <footer>
    <p>Built by <a class="footer-link" href="https://modularitynet.com" target="_blank" rel="noopener">Modularity Networks</a></p>
    <p>info@modularitynet.com</p>
  </footer>

  <script>
    (function () {{
      var buttons = document.querySelectorAll('.tab-btn');
      var panels = document.querySelectorAll('.tab-panel');
      buttons.forEach(function (btn) {{
        btn.addEventListener('click', function () {{
          var target = btn.getAttribute('data-tab');
          buttons.forEach(function (b) {{
            var isActive = b === btn;
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-selected', isActive ? 'true' : 'false');
          }});
          panels.forEach(function (p) {{
            p.classList.toggle('active', p.getAttribute('data-panel') === target);
          }});
        }});
      }});

      var showcase = document.querySelector('.showcase');
      var searchInput = document.getElementById('site-search');
      var searchStatus = document.getElementById('search-status');
      var cards = document.querySelectorAll('.card');
      var emptyStates = document.querySelectorAll('.empty-state');

      searchInput.addEventListener('input', function () {{
        var query = searchInput.value.trim().toLowerCase();

        if (!query) {{
          showcase.classList.remove('searching');
          cards.forEach(function (c) {{ c.classList.remove('is-hidden'); }});
          emptyStates.forEach(function (e) {{ e.classList.remove('is-hidden'); }});
          searchStatus.textContent = '';
          return;
        }}

        showcase.classList.add('searching');
        emptyStates.forEach(function (e) {{ e.classList.add('is-hidden'); }});

        var matches = 0;
        cards.forEach(function (c) {{
          var hay = c.getAttribute('data-search') || '';
          var isMatch = hay.indexOf(query) !== -1;
          c.classList.toggle('is-hidden', !isMatch);
          if (isMatch) matches++;
        }});

        searchStatus.textContent = matches === 0
          ? 'No businesses found for "' + searchInput.value.trim() + '". Try a different name or town.'
          : matches + (matches === 1 ? ' business' : ' businesses') + ' found across all areas.';
      }});
    }})();
  </script>

</body>
</html>
'''

with open("index.html", "w") as f:
    f.write(html)

print(f"Regenerated index.html with {count} sites across {len(ordered_regions)} region(s)")
