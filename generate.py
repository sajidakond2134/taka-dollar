#!/usr/bin/env python3
"""টাকা-ডলার কনভার্টার: স্ট্যাটিক সাইট জেনারেটর।

চালানোর নিয়ম:  python generate.py
ফলাফল:        public/ ফোল্ডারে পুরো সাইট (Cloudflare Pages-এ এই ফোল্ডার ডিপ্লয় হবে)

সাইট চালুর আগে নিচের ৩টি সেটিং বদলে নিন।
"""
import html
import json
import os
import shutil
import urllib.request
from datetime import date

# ======================= সেটিং (এগুলো বদলান) =======================
SITE_URL = os.environ.get("SITE_URL", "https://YOUR-SITE.pages.dev").rstrip("/")
SITE_NAME = "টাকা রেট"
CONTACT_EMAIL = "your-email@example.com"
# ===================================================================

OUT = "public"
HISTORY_FILE = "rates.json"
API = "https://open.er-api.com/v6/latest/USD"

# কোড: (বাংলা নাম, ইংরেজি নাম)
CURRENCIES = {
    "USD": ("ডলার", "US Dollar"),
    "SAR": ("সৌদি রিয়াল", "Saudi Riyal"),
    "AED": ("দিরহাম", "UAE Dirham"),
    "EUR": ("ইউরো", "Euro"),
    "GBP": ("পাউন্ড", "British Pound"),
    "INR": ("ভারতীয় রুপি", "Indian Rupee"),
    "MYR": ("মালয়েশিয়ান রিঙ্গিত", "Malaysian Ringgit"),
}
AMOUNTS = [1, 10, 50, 100, 500, 1000]

# API একদম না পেলে এবং আগের কোনো ডেটাও না থাকলে এই আনুমানিক রেট ব্যবহার হবে
FALLBACK = {"USD": 122.0, "SAR": 32.5, "AED": 33.2, "EUR": 142.0,
            "GBP": 163.0, "INR": 1.4, "MYR": 27.5}

BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn(value):
    return str(value).translate(BN)


def fmt(n):
    """সংখ্যা -> বাংলা অঙ্ক, কমা সহ, ২ দশমিক"""
    return bn(f"{n:,.2f}")


def fmt_int(n):
    return bn(f"{n:,}")


def esc(s):
    return html.escape(str(s), quote=True)


# ------------------------- রেট লোড -------------------------
def load_rates():
    """ফেরত দেয়: (history dict, today_key, from_api)"""
    today = date.today().isoformat()
    history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                history = json.load(f).get("history", {})
        except Exception:
            history = {}

    from_api = False
    try:
        req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        if data.get("result") != "success":
            raise ValueError("API result not success")
        rates = data["rates"]
        history[today] = {c: rates["BDT"] / rates[c] for c in CURRENCIES}
        from_api = True
    except Exception as e:
        print("সতর্কতা: API থেকে রেট আনা যায়নি:", e)
        if not history:
            history[today] = dict(FALLBACK)

    # শেষ ১৪ দিনের ডেটা রাখি
    keys = sorted(history)[-14:]
    history = {k: history[k] for k in keys}
    if from_api:  # আনুমানিক ডেটা কখনো ইতিহাসে সংরক্ষণ করি না
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": history}, f, ensure_ascii=False, indent=1)
    return history, from_api


# ------------------------- ডিজাইন -------------------------
CSS = """
:root{--bg:#f6f8f5;--card:#fff;--ink:#16231d;--mute:#5b6b63;--line:#dfe6e1;
--green:#006a4e;--green-d:#004d38;--red:#e0293d;--soft:#e7f2ec}
@media (prefers-color-scheme:dark){:root{--bg:#0f1713;--card:#17221c;--ink:#e8f0ec;
--mute:#9db0a6;--line:#27372f;--green:#3dbb91;--green-d:#2a9673;--soft:#1d2d25}}
*{box-sizing:border-box}
html{scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:"Hind Siliguri","Noto Sans Bengali","Kalpurush",system-ui,sans-serif;
font-size:17px;line-height:1.7}
a{color:var(--green)}
header{background:var(--green);color:#fff}
header .in{max-width:880px;margin:0 auto;padding:14px 16px;display:flex;
justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#fff;text-decoration:none}
.logo{font-size:1.25rem;font-weight:700}
nav a{margin-left:14px;font-size:.95rem;opacity:.92}
main{max-width:880px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:1.7rem;line-height:1.35;margin:.3em 0 .5em}
h2{font-size:1.25rem;margin:1.8em 0 .6em}
.answer{background:var(--green);color:#fff;border-radius:14px;padding:22px 20px;margin:12px 0}
.answer .big{font-size:2.1rem;font-weight:700;line-height:1.25}
.answer small{display:block;opacity:.85;font-size:.95rem;margin-top:6px}
.chg{display:inline-block;margin-top:10px;padding:2px 10px;border-radius:99px;
background:rgba(255,255,255,.18);font-size:.9rem}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.calc{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.calc input{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:8px;
width:150px;background:var(--bg);color:var(--ink)}
.calc output{font-size:1.2rem;font-weight:700;color:var(--green)}
.calc input:focus-visible,a:focus-visible{outline:3px solid var(--red);outline-offset:2px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
border-radius:12px;overflow:hidden}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line)}
th{background:var(--soft);font-weight:600}
tr:last-child td{border-bottom:0}
.scroll{overflow-x:auto}
.links{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}
.links a{display:block;padding:6px 12px;border:1px solid var(--line);border-radius:99px;
background:var(--card);text-decoration:none;font-size:.95rem}
.links a:hover{background:var(--soft)}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:10px 14px;margin:8px 0}
summary{cursor:pointer;font-weight:600}
.ad{min-height:0;margin:16px 0;text-align:center}
.note{color:var(--mute);font-size:.9rem}
footer{border-top:1px solid var(--line);padding:20px 16px;text-align:center;
color:var(--mute);font-size:.9rem}
footer a{margin:0 8px}
@media(max-width:520px){h1{font-size:1.45rem}.answer .big{font-size:1.7rem}}
"""

ADS_JS = """// ===== অ্যাড কোড বসানোর ফাইল =====
// amanahads.com (বা অন্য নেটওয়ার্ক) থেকে পাওয়া অ্যাড কোড নিচের ব্যাকটিকের (`) ভেতরে পেস্ট করুন।
// এক জায়গায় বদলালে সব পেজে বদলে যাবে। ফাঁকা থাকলে কোনো অ্যাড দেখাবে না।
var AD_TOP = ``;
var AD_BOTTOM = ``;

function putAd(id, code) {
  var el = document.getElementById(id);
  if (!el || !code.trim()) return;
  el.innerHTML = code;
  // innerHTML দিয়ে বসালে <script> চলে না, তাই নতুন করে বানিয়ে বসাই
  el.querySelectorAll("script").forEach(function (old) {
    var s = document.createElement("script");
    for (var i = 0; i < old.attributes.length; i++) {
      s.setAttribute(old.attributes[i].name, old.attributes[i].value);
    }
    s.text = old.text;
    old.parentNode.replaceChild(s, old);
  });
}
putAd("ad-top", AD_TOP);
putAd("ad-bottom", AD_BOTTOM);
"""


def page(path, title, desc, body, ld=None):
    url = SITE_URL + path
    ld_tag = ""
    if ld:
        ld_tag = '<script type="application/ld+json">%s</script>' % json.dumps(
            ld, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(url)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
{ld_tag}
</head>
<body>
<header><div class="in">
<a class="logo" href="/">{esc(SITE_NAME)}</a>
<nav><a href="/">সব রেট</a><a href="/about">আমাদের সম্পর্কে</a><a href="/contact">যোগাযোগ</a></nav>
</div></header>
<main>
{body}
</main>
<footer>
<p>এখানকার রেট তথ্যের জন্য। ব্যাংক বা মানি এক্সচেঞ্জের আসল রেট আলাদা হতে পারে।</p>
<p><a href="/about">আমাদের সম্পর্কে</a><a href="/contact">যোগাযোগ</a><a href="/privacy">প্রাইভেসি পলিসি</a></p>
<p><a href="https://www.exchangerate-api.com" rel="nofollow noopener">Rates By Exchange Rate API</a></p>
</footer>
<script src="/ads.js" defer></script>
</body>
</html>
"""


def slug(amount, code):
    return f"{amount}-{code.lower()}-to-bdt"


def hub_slug(code):
    return f"{code.lower()}-to-bdt"


def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


# ------------------------- পেজ বানানো -------------------------
def change_text(code, history, today):
    prev_days = [d for d in sorted(history) if d < today]
    if not prev_days:
        return ""
    prev = history[prev_days[-1]].get(code)
    cur = history[today][code]
    if not prev:
        return ""
    diff = cur - prev
    pct = diff / prev * 100
    if abs(pct) < 0.005:
        return '<span class="chg">আগের দিনের মতোই</span>'
    word = "বেড়েছে" if diff > 0 else "কমেছে"
    return (f'<span class="chg">আগের দিনের চেয়ে ১ {{}} এ {fmt(abs(diff))} টাকা {word} '
            f'({bn(f"{abs(pct):.2f}")}%)</span>')


def convert_page(code, amount, history, today):
    name = CURRENCIES[code][0]
    per = history[today][code]
    total = per * amount
    a = fmt_int(amount)
    title = f"{a} {name} কত টাকা? আজকের রেট ({bn(today)})"
    desc = (f"{a} {name} = {fmt(total)} টাকা। আজকের ({bn(today)}) এক্সচেঞ্জ রেটে "
            f"{name} থেকে বাংলাদেশি টাকায় হিসাব, ক্যালকুলেটর ও ছোট-বড় সব পরিমাণের তালিকা।")

    chg = change_text(code, history, today).replace("{}", esc(name))

    rows = "".join(
        f'<tr><td><a href="/{slug(x, code)}">{fmt_int(x)} {esc(name)}</a></td>'
        f'<td>{fmt(per * x)} টাকা</td></tr>' for x in AMOUNTS)

    taka_rows = "".join(
        f'<tr><td>{fmt_int(t)} টাকা</td><td>{fmt(t / per)} {esc(name)}</td></tr>'
        for t in (100, 500, 1000, 5000, 10000))

    same_amount = "".join(
        f'<li><a href="/{slug(amount, c)}">{a} {esc(CURRENCIES[c][0])} কত টাকা</a></li>'
        for c in CURRENCIES if c != code)
    same_cur = "".join(
        f'<li><a href="/{slug(x, code)}">{fmt_int(x)} {esc(name)} কত টাকা</a></li>'
        for x in AMOUNTS if x != amount)

    faqs = [
        (f"{a} {name} কত টাকা?",
         f"আজকের ({bn(today)}) রেট অনুযায়ী {a} {name} = {fmt(total)} টাকা।"),
        (f"১ {name} কত টাকা?",
         f"আজকের হিসাবে ১ {name} = {fmt(per)} টাকা।"),
        (f"১০০০ টাকায় কত {name} পাওয়া যায়?",
         f"আজকের রেটে ১,০০০ টাকায় প্রায় {fmt(1000 / per)} {name} পাওয়া যায়।"),
        ("রেট কত দিন পরপর আপডেট হয়?",
         "রেট প্রতিদিন স্বয়ংক্রিয়ভাবে আপডেট হয়। পাতার ওপরে আজকের তারিখ দেওয়া আছে।"),
        ("ব্যাংক বা মানি এক্সচেঞ্জে কি এই রেটেই পাব?",
         "সাধারণত না। এটা আন্তর্জাতিক মার্কেট রেটের কাছাকাছি একটি মান। ব্যাংক, মানি এক্সচেঞ্জ "
         "বা মোবাইল ওয়ালেট নিজেদের ফি ও মার্জিন যোগ করে, তাই টাকা পাঠানো বা কেনার আগে "
         "তাদের নিজস্ব রেট দেখে নিন।"),
    ]
    faq_html = "".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>" for q, ans in faqs)
    ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs],
    }

    body = f"""
<h1>{a} {esc(name)} কত টাকা?</h1>
<div class="answer">
<div class="big">{a} {esc(name)} = {fmt(total)} টাকা</div>
<small>১ {esc(name)} = {fmt(per)} টাকা &middot; আপডেট: {bn(today)}</small>
{chg}
</div>
<div id="ad-top" class="ad"></div>

<h2>নিজে হিসাব করুন</h2>
<div class="box calc">
<label for="amt">{esc(name)}:</label>
<input id="amt" type="number" inputmode="decimal" min="0" value="{amount}">
<span>=</span><output id="out" for="amt">{fmt(total)}</output><span>টাকা</span>
</div>
<script>
(function(){{var R={per};var i=document.getElementById("amt"),o=document.getElementById("out");
function u(){{var v=parseFloat(i.value);o.textContent=isNaN(v)?"০":(v*R).toLocaleString("bn-BD",{{minimumFractionDigits:2,maximumFractionDigits:2}});}}
i.addEventListener("input",u);}})();
</script>

<h2>{esc(name)} থেকে টাকার তালিকা</h2>
<div class="scroll"><table>
<tr><th>পরিমাণ</th><th>টাকা</th></tr>{rows}</table></div>

<h2>টাকা থেকে {esc(name)}</h2>
<div class="scroll"><table>
<tr><th>টাকা</th><th>{esc(name)}</th></tr>{taka_rows}</table></div>

<h2>সচরাচর জিজ্ঞাসা</h2>
{faq_html}

<div id="ad-bottom" class="ad"></div>

<h2>একই পরিমাণ, অন্য মুদ্রা</h2>
<ul class="links">{same_amount}</ul>
<h2>{esc(name)}-এর অন্য পরিমাণ</h2>
<ul class="links">{same_cur}</ul>
<p><a href="/{hub_slug(code)}">{esc(name)}-এর গত কয়েক দিনের রেট দেখুন</a></p>
"""
    write(f"{slug(amount, code)}.html",
          page("/" + slug(amount, code), title, desc, body, ld))


def hub_page(code, history, today):
    name = CURRENCIES[code][0]
    per = history[today][code]
    title = f"{name} থেকে টাকা: আজকের রেট ও গত কয়েক দিনের তালিকা"
    desc = f"আজ ১ {name} = {fmt(per)} টাকা। {name}-এর গত কয়েক দিনের রেট ও সব পরিমাণের হিসাব।"

    hist_rows = "".join(
        f"<tr><td>{bn(d)}</td><td>{fmt(history[d][code])} টাকা</td></tr>"
        for d in sorted(history, reverse=True)[:14] if code in history[d])
    amt_rows = "".join(
        f'<tr><td><a href="/{slug(x, code)}">{fmt_int(x)} {esc(name)}</a></td>'
        f'<td>{fmt(per * x)} টাকা</td></tr>' for x in AMOUNTS)
    chg = change_text(code, history, today).replace("{}", esc(name))

    body = f"""
<h1>{esc(name)} থেকে টাকা: আজকের রেট</h1>
<div class="answer">
<div class="big">১ {esc(name)} = {fmt(per)} টাকা</div>
<small>আপডেট: {bn(today)}</small>
{chg}
</div>
<div id="ad-top" class="ad"></div>
<h2>পরিমাণ অনুযায়ী</h2>
<div class="scroll"><table><tr><th>পরিমাণ</th><th>টাকা</th></tr>{amt_rows}</table></div>
<h2>গত কয়েক দিনের রেট</h2>
<div class="scroll"><table><tr><th>তারিখ</th><th>১ {esc(name)}</th></tr>{hist_rows}</table></div>
<div id="ad-bottom" class="ad"></div>
"""
    write(f"{hub_slug(code)}.html", page("/" + hub_slug(code), title, desc, body))


def index_page(history, today):
    rows = "".join(
        f'<tr><td><a href="/{hub_slug(c)}">{esc(CURRENCIES[c][0])}</a></td>'
        f'<td>{fmt(history[today][c])} টাকা</td>'
        f'<td><a href="/{slug(100, c)}">{fmt_int(100)} {esc(CURRENCIES[c][0])} কত টাকা</a></td></tr>'
        for c in CURRENCIES)
    popular = "".join(
        f'<li><a href="/{slug(x, c)}">{fmt_int(x)} {esc(CURRENCIES[c][0])} কত টাকা</a></li>'
        for c in ("USD", "SAR", "AED") for x in (100, 500, 1000))
    title = f"আজকের টাকার রেট: ডলার, রিয়াল, দিরহাম, ইউরো কত টাকা? ({bn(today)})"
    desc = "আজকের ডলার, সৌদি রিয়াল, দিরহাম, ইউরো, পাউন্ড, রুপি ও রিঙ্গিতের বিপরীতে বাংলাদেশি টাকার রেট ও ক্যালকুলেটর।"
    body = f"""
<h1>আজকের টাকার রেট</h1>
<p class="note">আপডেট: {bn(today)}। প্রতিদিন স্বয়ংক্রিয়ভাবে নতুন হয়।</p>
<div id="ad-top" class="ad"></div>
<div class="scroll"><table>
<tr><th>মুদ্রা</th><th>১ একক</th><th>জনপ্রিয় হিসাব</th></tr>{rows}</table></div>
<h2>বেশি খোঁজা হিসাব</h2>
<ul class="links">{popular}</ul>
<div id="ad-bottom" class="ad"></div>
"""
    write("index.html", page("/", title, desc, body))


def static_pages():
    write("about.html", page("/about", f"আমাদের সম্পর্কে | {SITE_NAME}",
                             f"{SITE_NAME} কী এবং রেট কোথা থেকে আসে।", f"""
<h1>আমাদের সম্পর্কে</h1>
<p>{esc(SITE_NAME)} একটি বিনামূল্যের মুদ্রা রূপান্তরের সাইট। এখানে ডলার, সৌদি রিয়াল, দিরহাম, ইউরো,
পাউন্ড, ভারতীয় রুপি ও মালয়েশিয়ান রিঙ্গিতের বিপরীতে বাংলাদেশি টাকার রেট পাবেন।</p>
<h2>রেট কোথা থেকে আসে</h2>
<p>রেট আসে <a href="https://www.exchangerate-api.com" rel="nofollow noopener">Exchange Rate API</a> থেকে
এবং প্রতিদিন স্বয়ংক্রিয়ভাবে আপডেট হয়। এগুলো আন্তর্জাতিক মার্কেটের কাছাকাছি মান।</p>
<h2>সতর্কতা</h2>
<p>ব্যাংক, মানি এক্সচেঞ্জ ও রেমিট্যান্স সেবা নিজেদের ফি ও মার্জিন যোগ করে, তাই তাদের আসল রেট
এখানকার চেয়ে আলাদা হতে পারে। আর্থিক লেনদেনের আগে নিজের ব্যাংক বা সেবাদাতার রেট দেখে নিন।</p>
"""))
    write("contact.html", page("/contact", f"যোগাযোগ | {SITE_NAME}",
                               "ভুল বা পরামর্শ জানাতে যোগাযোগ করুন।", f"""
<h1>যোগাযোগ</h1>
<p>ভুল তথ্য, পরামর্শ বা অন্য যেকোনো বিষয়ে ইমেইল করুন:</p>
<p><a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a></p>
"""))
    write("privacy.html", page("/privacy", f"প্রাইভেসি পলিসি | {SITE_NAME}",
                               "আমরা কী তথ্য সংগ্রহ করি এবং কীভাবে ব্যবহার করি।", f"""
<h1>প্রাইভেসি পলিসি</h1>
<p>{esc(SITE_NAME)} আপনার নাম, ফোন নম্বর বা ইমেইলের মতো ব্যক্তিগত তথ্য চায় না। ক্যালকুলেটরে যা লেখেন
তা শুধু আপনার ব্রাউজারেই থাকে।</p>
<h2>বিজ্ঞাপন ও কুকিজ</h2>
<p>এই সাইটে তৃতীয় পক্ষের বিজ্ঞাপন নেটওয়ার্ক (যেমন amanahads.com বা Google AdSense) বিজ্ঞাপন দেখাতে পারে।
তারা বিজ্ঞাপন দেখানো ও পরিমাপের জন্য কুকিজ বা অনুরূপ প্রযুক্তি ব্যবহার করতে পারে। এসব নেটওয়ার্কের
নিজস্ব প্রাইভেসি পলিসি প্রযোজ্য। ব্রাউজারের সেটিংস থেকে কুকিজ বন্ধ করা যায়।</p>
<h2>অ্যানালিটিক্স</h2>
<p>সাইটের ব্যবহার বুঝতে আমরা অ্যানালিটিক্স টুল ব্যবহার করতে পারি, যা বেনামে পেজ ভিজিটের তথ্য রাখে।</p>
<h2>তৃতীয় পক্ষের লিংক</h2>
<p>এই সাইটের লিংকে অন্য সাইটে গেলে সেগুলোর নীতির দায় আমাদের নয়।</p>
<h2>যোগাযোগ</h2>
<p>প্রশ্ন থাকলে <a href="/contact">যোগাযোগ</a> পেজ দেখুন।</p>
"""))


def seo_files(urls, today):
    items = "".join(
        f"<url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>'
          f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def main():
    history, from_api = load_rates()
    today = max(history)

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    urls = ["/", "/about", "/contact", "/privacy"]
    index_page(history, today)
    static_pages()
    for code in CURRENCIES:
        hub_page(code, history, today)
        urls.append("/" + hub_slug(code))
        for amount in AMOUNTS:
            convert_page(code, amount, history, today)
            urls.append("/" + slug(amount, code))

    # ads.js: আগের বসানো অ্যাড কোড যেন মুছে না যায়, তাই রুটের ads.js থাকলে সেটা কপি হয়
    if os.path.exists("ads.js"):
        shutil.copy("ads.js", os.path.join(OUT, "ads.js"))
    else:
        with open("ads.js", "w", encoding="utf-8") as f:
            f.write(ADS_JS)
        shutil.copy("ads.js", os.path.join(OUT, "ads.js"))

    seo_files(urls, today)
    print(f"সম্পন্ন: {len(urls)}টি পেজ, তারিখ {today}, API থেকে নতুন রেট: {from_api}")


if __name__ == "__main__":
    main()
