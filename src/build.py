#!/usr/bin/env python3
"""Build index.html from the fragments in src/.

Edit src/head.html (styles) and src/body.html (markup + logic), then run this.
Never edit index.html directly -- it is generated and will be overwritten.
"""
import pathlib, json, re
sc = pathlib.Path(__file__).parent
repo = sc.parent
head=(sc/"head.html").read_text(); body=(sc/"body.html").read_text()
logos=(sc/"logos_data.json").read_text(); colors=(sc/"colors.json").read_text().replace("\n","")
# anon key is public by design (read-only under RLS); it already ships in index.html
anon=re.search(r'SUPABASE_ANON="([^"]+)"', (repo/"index.html").read_text()).group(1)
data=json.load(open(sc/"matchup_data.json"))
meta={t:{"city":v["city"],"name":v["name"]} for t,v in data.items()}
fontlink=re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis[^>]+>',head).group(0)
styles="\n".join(re.findall(r'<style>.*?</style>',head,re.S))
mk=body.index("<script>")
markup, script = body[:mk], body[mk+len("<script>"):body.rindex("</script>")]

# ---- live page (GitHub Pages): fetches Supabase ----
live_script = script.replace(
  'const NAMES = Object.fromEntries(Object.entries(DATA).map(([k,v])=>[k, v.city+" "+v.name]));',
  'const NAMES = Object.fromEntries(Object.entries(DATA).map(([k,v])=>[k, META[k].city+" "+META[k].name]));'
).replace('DATA[t].name.toLowerCase()','META[t].name.toLowerCase()')

COLS = ("team,side,games,attempts,rushing_yards,ypc,rushing_tds,first_downs,long_run,dvoa,succ_pct,"
        "epa_att,aybco,ayaco,stf_pct,exp_pct,crt_pct,aryoe,ply_gm,rush_pct,yd_ply,pt_gm,drv_gm,sec_ply,scraped_on")

live = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Run Game Matchup</title>
<meta name="description" content="NFL rushing offense vs rushing defense, live from FTN data.">
{fontlink}
<style>:root{{color-scheme:light dark}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{styles}
<style>
#boot{{padding:60px 0;text-align:center;color:var(--muted);font-family:"Public Sans",system-ui,sans-serif}}
#boot b{{display:block;font-family:"Archivo",system-ui,sans-serif;font-size:19px;color:var(--ink);margin-bottom:7px}}
#boot code{{font-size:12.5px;color:var(--faint)}}
</style>
</head>
<body>
<div id="boot"><b>Loading team data…</b><span>reading the latest snapshot from Supabase</span></div>
<div id="app" hidden>
{markup}</div>
<script>
const LOGOS={logos};
const COLORS={colors};
const META={json.dumps(meta,separators=(',',':'))};
const SUPABASE_URL="https://mfliuasrygxkembqmrkr.supabase.co";
const SUPABASE_ANON="{anon}";   // anon key: read-only, enforced by row-level security

async function loadData(){{
  const r=await fetch(`${{SUPABASE_URL}}/rest/v1/nfl_rushing_latest?select={COLS}`,
    {{headers:{{apikey:SUPABASE_ANON,Authorization:"Bearer "+SUPABASE_ANON}}}});
  if(!r.ok) throw new Error("Supabase returned "+r.status);
  const rows=await r.json();
  if(!rows.length) throw new Error("no rows returned");
  const out={{}};
  for(const x of rows){{ (out[x.team] ??= {{}})[x.side]=x; }}
  const bad=Object.entries(out).filter(([,v])=>!v.offense||!v.defense).map(([k])=>k);
  if(bad.length) throw new Error("incomplete data for "+bad.join(", "));
  return out;
}}

(async function boot(){{
  let DATA;
  try{{ DATA=await loadData(); }}
  catch(err){{
    document.getElementById("boot").innerHTML =
      `<b>Couldn't load the data.</b><span>${{err.message}}</span><br>`+
      `<code>The scraper runs Sun, Tue and Wed. If this persists, check the Actions tab.</code>`;
    return;
  }}
  document.getElementById("boot").hidden=true;
  document.getElementById("app").hidden=false;
{live_script}
}})();
</script>
</body>
</html>
"""
(repo/"index.html").write_text(live)

print(f"index.html rebuilt: {len(live)//1024} KB")
