"""SNEC AI — Design system: CSS injection + HTML component helpers.

Inject once at the top of app.py:
    from tools.shared.styles import SNEC_CSS, ph, stat_card, topic_bar, section_label, badge
    st.markdown(SNEC_CSS, unsafe_allow_html=True)
"""

# ─── Design tokens (mirrored in CSS :root) ─────────────────────────────────────
ACCENT   = "#06D6C0"
GOLD     = "#F59E0B"
SUCCESS  = "#10B981"
DANGER   = "#EF4444"
INFO     = "#3B82F6"

# ─── Full CSS ──────────────────────────────────────────────────────────────────
SNEC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════════
   TOKENS
═══════════════════════════════════════════════════ */
:root {
  /* ── Surfaces ── */
  --bg:          #06080F;
  --bg-surface:  #0B0F1C;
  --bg-card:     #0F1624;
  --bg-raised:   #141D2E;

  /* ── Borders — 3-tier precision system ── */
  --border:      rgba(255,255,255,0.05);
  --border-mid:  rgba(255,255,255,0.09);
  --border-hi:   rgba(255,255,255,0.14);

  /* ── Accent — teal, kept as brand identity ── */
  --accent:      #06D6C0;
  --accent-10:   rgba(6,214,192,.10);
  --accent-20:   rgba(6,214,192,.20);
  --accent-glow: rgba(6,214,192,.22);

  /* ── Semantic ── */
  --gold:        #F59E0B;
  --gold-10:     rgba(245,158,11,.10);
  --gold-20:     rgba(245,158,11,.20);
  --ok:          #10B981;
  --warn:        #F59E0B;
  --danger:      #EF4444;
  --blue:        #3B82F6;

  /* ── Text hierarchy ── */
  --txt:         #EBF0FF;
  --txt-2:       #7A96C2;
  --txt-3:       #3A5075;

  /* ── Fonts ── */
  --serif:       'DM Serif Display', Georgia, serif;
  --sans:        'Instrument Sans', system-ui, sans-serif;
  --mono:        'JetBrains Mono', monospace;

  /* ── Radii ── */
  --r:   8px;
  --r2: 14px;
  --r3: 20px;

  /* ── Shadow system (Stripe-philosophy: soft, layered, never harsh) ── */
  --sh-xs:  0 1px 2px rgba(0,0,0,0.08);
  --sh-sm:  0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
  --sh:     0 4px 8px rgba(0,0,0,0.18), 0 1px 3px rgba(0,0,0,0.12);
  --sh2:    0 8px 24px rgba(0,0,0,0.28), 0 2px 6px rgba(0,0,0,0.16);
  --sh3:    0 16px 48px rgba(0,0,0,0.38), 0 4px 12px rgba(0,0,0,0.2);

  /* ── Card ring glows ── */
  --ring-card:       0 0 0 1px var(--border);
  --ring-card-hover: 0 0 0 1px rgba(6,214,192,0.22), 0 0 18px rgba(6,214,192,0.07);
  --ring-focus:      0 0 0 3px rgba(6,214,192,0.18);
}

/* ═══════════════════════════════════════════════════
   APP SHELL
═══════════════════════════════════════════════════ */
.stApp {
  background:
    /* dot-grid texture */
    radial-gradient(circle, rgba(255,255,255,0.035) 1px, transparent 1px),
    /* ambient gradient mesh */
    radial-gradient(ellipse 90% 40% at 50% -8%, rgba(6,214,192,.06) 0%, transparent 60%),
    radial-gradient(ellipse 55% 35% at 92% 88%, rgba(59,130,246,.03) 0%, transparent 55%),
    var(--bg) !important;
  background-size: 28px 28px, 100% 100%, 100% 100%, 100% 100% !important;
  font-family: var(--sans) !important;
  color: var(--txt) !important;
}

::-webkit-scrollbar          { width:5px; height:5px }
::-webkit-scrollbar-track    { background: var(--bg-surface) }
::-webkit-scrollbar-thumb    { background: var(--border-hi); border-radius:3px }
::-webkit-scrollbar-thumb:hover { background: var(--txt-3) }

/* hide Streamlit chrome */
#MainMenu, footer { display:none !important }
header[data-testid="stHeader"] {
  background: rgba(7,9,15,.8) !important;
  backdrop-filter: blur(14px) !important;
  border-bottom: 1px solid var(--border) !important;
}
.stDeployButton { display:none !important }

/* ═══════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: var(--bg-surface) !important;
}
[data-testid="stSidebar"]::after {
  content:'';
  position:absolute; top:0; left:0;
  width:2px; height:100%;
  background: linear-gradient(180deg, var(--accent) 0%, transparent 70%);
  pointer-events:none;
}
[data-testid="stSidebarContent"] .stMarkdown p {
  color: var(--txt-3) !important;
  font-size: .8rem !important;
}

/* sidebar nav buttons — secondary = inactive */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--txt-2) !important;
  border: 1px solid transparent !important;
  border-radius: var(--r) !important;
  font-size: .82rem !important;
  font-weight: 500 !important;
  letter-spacing: .01em !important;
  transition: all .15s !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg-raised) !important;
  color: var(--txt) !important;
  border-color: var(--border-mid) !important;
  transform: none !important;
  box-shadow: none !important;
}
/* active page */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--accent-10) !important;
  color: var(--accent) !important;
  border-color: var(--accent-20) !important;
  font-weight: 600 !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: var(--accent-20) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ═══════════════════════════════════════════════════
   MAIN CONTAINER
═══════════════════════════════════════════════════ */
.main .block-container {
  padding: 2.25rem 2.75rem !important;
  max-width: 1180px !important;
}

/* fade-in on page load */
.main .block-container > div > div {
  animation: fadeUp .3s ease both;
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(10px) }
  to   { opacity:1; transform:translateY(0) }
}

/* ═══════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════ */
h1 {
  font-family: var(--serif) !important;
  font-size: 2.25rem !important;
  font-weight: 400 !important;
  color: var(--txt) !important;
  letter-spacing: -.03em !important;
  line-height: 1.12 !important;
  margin-bottom: .1rem !important;
}
h2 {
  font-family: var(--serif) !important;
  font-size: 1.55rem !important;
  font-weight: 400 !important;
  color: var(--txt) !important;
  letter-spacing: -.02em !important;
  line-height: 1.2 !important;
}
h3 {
  font-family: var(--sans) !important;
  font-size: .72rem !important;
  font-weight: 700 !important;
  color: var(--txt-3) !important;
  text-transform: uppercase !important;
  letter-spacing: .13em !important;
}
p, li { color: var(--txt-2) !important; font-size: .88rem !important; line-height: 1.72 !important }
strong { color: var(--txt) !important }
code {
  font-family: var(--mono) !important;
  background: var(--bg-raised) !important;
  color: var(--accent) !important;
  padding: 2px 7px !important;
  border-radius: 5px !important;
  font-size: .82em !important;
  border: 1px solid var(--border-mid) !important;
}
a { color: var(--accent) !important; text-decoration: none !important }
a:hover { text-decoration: underline !important; text-underline-offset: 3px !important }
[data-testid="stCaptionContainer"] p,
.stCaption { color: var(--txt-3) !important; font-size: .74rem !important }
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important }

/* ═══════════════════════════════════════════════════
   BUTTONS (global)
═══════════════════════════════════════════════════ */
.stButton > button {
  background: var(--bg-raised) !important;
  color: var(--txt-2) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--r) !important;
  font-family: var(--sans) !important;
  font-size: .84rem !important;
  font-weight: 500 !important;
  letter-spacing: .01em !important;
  padding: .45rem 1.1rem !important;
  transition: all .15s ease !important;
  /* Stripe-style: inset highlight + soft drop shadow */
  box-shadow: var(--sh-xs), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}
.stButton > button:hover {
  background: var(--bg-card) !important;
  color: var(--txt) !important;
  border-color: var(--border-hi) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--sh), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(145deg, #08EDD5 0%, var(--accent) 50%, #04B0A2 100%) !important;
  color: #060C18 !important;
  border: none !important;
  font-weight: 700 !important;
  /* Layered: drop shadow + glow */
  box-shadow: var(--sh-sm), 0 0 0 1px rgba(6,214,192,0.3), 0 4px 14px var(--accent-glow),
              inset 0 1px 0 rgba(255,255,255,0.18) !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(145deg, #12FFE8 0%, #08EDD5 50%, var(--accent) 100%) !important;
  color: #060C18 !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--sh), 0 0 0 1px rgba(6,214,192,0.35), 0 6px 22px var(--accent-glow),
              inset 0 1px 0 rgba(255,255,255,0.22) !important;
}

/* ═══════════════════════════════════════════════════
   FORM INPUTS
═══════════════════════════════════════════════════ */
/* labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
  color: var(--txt-3) !important;
  font-size: .72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: .09em !important;
}
.stCheckbox label { color: var(--txt-2) !important; font-size: .85rem !important }
.stCheckbox label span[data-baseweb="checkbox"] {
  background: var(--bg-raised) !important;
  border-color: var(--border-hi) !important;
}

/* text input wrapper */
.stTextInput > div > div,
.stTextArea > div > div {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--r) !important;
  transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: var(--ring-focus) !important;
}
.stTextInput input, .stTextArea textarea {
  background: transparent !important;
  color: var(--txt) !important;
  font-family: var(--sans) !important;
  caret-color: var(--accent) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color: var(--txt-3) !important }

/* select */
.stSelectbox > div > div {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--r) !important;
  color: var(--txt) !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: var(--ring-focus) !important;
}

/* number input */
.stNumberInput > div > div {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--r) !important;
}
.stNumberInput input {
  background: transparent !important;
  color: var(--txt) !important;
  font-family: var(--mono) !important;
}

/* chat input */
[data-testid="stChatInput"] {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--r2) !important;
  transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: var(--ring-focus), 0 0 16px var(--accent-glow) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--txt) !important;
  font-family: var(--sans) !important;
}
[data-testid="stChatInput"] button { background: var(--accent) !important; border-radius: var(--r) !important }

/* ═══════════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════════ */
[data-testid="metric-container"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  padding: 1.1rem 1.4rem !important;
  position: relative !important;
  overflow: hidden !important;
  transition: border-color .2s, box-shadow .2s !important;
  box-shadow: var(--sh-xs) !important;
}
[data-testid="metric-container"]::before {
  content:'';
  position:absolute; top:0; left:0;
  width:3px; height:100%;
  background: linear-gradient(180deg, var(--accent), transparent);
}
[data-testid="metric-container"]:hover {
  border-color: rgba(6,214,192,0.22) !important;
  box-shadow: var(--ring-card-hover), var(--sh) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--txt-3) !important;
  font-size: .68rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: .1em !important;
}
[data-testid="stMetricValue"] {
  color: var(--txt) !important;
  font-family: var(--serif) !important;
  font-size: 1.9rem !important;
}
[data-testid="stMetricDelta"] { font-size: .75rem !important }

/* ═══════════════════════════════════════════════════
   PROGRESS
═══════════════════════════════════════════════════ */
.stProgress > div {
  background: var(--bg-raised) !important;
  border-radius: 99px !important;
  height: 6px !important;
}
.stProgress > div > div {
  background: linear-gradient(90deg, var(--accent), #04C4B2) !important;
  border-radius: 99px !important;
  height: 100% !important;
  box-shadow: 0 0 10px var(--accent-glow) !important;
  transition: width .6s cubic-bezier(.4,0,.2,1) !important;
}
/* progress label text */
[data-testid="stProgressLabel"] {
  color: var(--txt-3) !important;
  font-size: .72rem !important;
  font-family: var(--mono) !important;
}

/* ═══════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════ */
.stAlert {
  border-radius: var(--r) !important;
  border-left-width: 3px !important;
}
.stInfo {
  background: rgba(59,130,246,.07) !important;
  border-color: var(--blue) !important;
}
.stInfo p { color: #93C5FD !important }
.stSuccess {
  background: rgba(16,185,129,.07) !important;
  border-color: var(--ok) !important;
}
.stSuccess p { color: #6EE7B7 !important }
.stWarning {
  background: rgba(245,158,11,.07) !important;
  border-color: var(--warn) !important;
}
.stWarning p { color: #FCD34D !important }
.stError {
  background: rgba(239,68,68,.07) !important;
  border-color: var(--danger) !important;
}
.stError p { color: #FCA5A5 !important }

/* ═══════════════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  margin-bottom: .6rem !important;
  transition: border-color .2s !important;
}
[data-testid="stChatMessage"]:hover { border-color: var(--border-mid) !important }
[data-testid="stChatMessageContent"] p {
  color: var(--txt-2) !important;
  font-size: .88rem !important;
  line-height: 1.7 !important;
}

/* ═══════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  background: var(--bg-card) !important;
  color: var(--txt-2) !important;
  font-size: .84rem !important;
  font-weight: 500 !important;
  padding: .7rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
  background: var(--bg-raised) !important;
  color: var(--txt) !important;
}
.streamlit-expanderContent {
  background: var(--bg-surface) !important;
  border-top: 1px solid var(--border) !important;
}

/* ═══════════════════════════════════════════════════
   BORDER CONTAINERS  (st.container(border=True))
═══════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  box-shadow: var(--sh-xs) !important;
  transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(6,214,192,0.2) !important;
  box-shadow: var(--ring-card-hover), var(--sh) !important;
}

/* ═══════════════════════════════════════════════════
   TABLES
═══════════════════════════════════════════════════ */
thead tr th {
  background: var(--bg-raised) !important;
  color: var(--txt-3) !important;
  font-size: .68rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: .08em !important;
}
tbody tr td {
  background: var(--bg-card) !important;
  color: var(--txt-2) !important;
  border-color: var(--border) !important;
  font-size: .84rem !important;
}
tbody tr:hover td { background: var(--bg-raised) !important }

/* ═══════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════ */
.stSpinner > div { border-color: var(--accent) transparent transparent transparent !important }

/* ═══════════════════════════════════════════════════
   IMAGE
═══════════════════════════════════════════════════ */
.stImage img { border-radius: var(--r) !important; border: 1px solid var(--border) !important }

/* ═══════════════════════════════════════════════════
   CUSTOM SNEC COMPONENTS  (injected via st.markdown)
═══════════════════════════════════════════════════ */

/* — Wordmark / sidebar logo ——————————— */
.snec-wordmark {
  display: flex; align-items: center; gap: .6rem;
  padding: .5rem .25rem 1rem;
  user-select: none;
}
.snec-wordmark-icon {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent) 0%, #04A99B 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem; flex-shrink: 0;
  box-shadow: 0 0 14px var(--accent-glow);
}
.snec-wordmark-text { line-height: 1.15 }
.snec-wordmark-name {
  font-family: var(--serif); font-size: .95rem;
  color: var(--txt); letter-spacing: -.01em;
}
.snec-wordmark-sub {
  font-size: .62rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: .1em; color: var(--txt-3);
}

/* — User chip ——————————————————————— */
.snec-user-chip {
  display: flex; align-items: center; gap: .55rem;
  padding: .55rem .75rem;
  background: var(--accent-10);
  border: 1px solid var(--accent-20);
  border-radius: var(--r); margin-bottom: .75rem;
}
.snec-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #04A99B);
  display: flex; align-items: center; justify-content: center;
  font-size: .7rem; font-weight: 700; color: #070B18; flex-shrink: 0;
}
.snec-user-name { font-size: .8rem; font-weight: 600; color: var(--accent); overflow:hidden; text-overflow:ellipsis; white-space:nowrap }

/* — Section label ————————————————— */
.snec-label {
  font-size: .66rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .12em;
  color: var(--txt-3);
  display: flex; align-items: center; gap: .6rem;
  margin: 1.4rem 0 .8rem;
}
.snec-label::after { content:''; flex:1; height:1px; background: var(--border) }

/* — Page header ——————————————————— */
.snec-ph { margin-bottom: 1.6rem }
.snec-ph h1 {
  font-family: var(--serif) !important;
  font-size: 2.1rem !important; font-weight: 400 !important;
  color: var(--txt) !important; letter-spacing: -.025em !important;
  line-height: 1.15 !important; margin: 0 0 .2rem !important;
}
.snec-ph-sub {
  font-size: .8rem; color: var(--txt-3); line-height: 1.5;
  max-width: 620px;
}

/* — Stat card —————————————————————— */
.snec-stat {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--r2); padding: 1.1rem 1.4rem;
  position: relative; overflow: hidden;
  box-shadow: var(--sh-xs);
  transition: border-color .2s, box-shadow .2s;
}
.snec-stat:hover { border-color: rgba(6,214,192,0.2); box-shadow: var(--ring-card-hover), var(--sh) }
.snec-stat::before { content:''; position:absolute; top:0; left:0; width:3px; height:100% }
.snec-stat.c-teal::before  { background: var(--accent) }
.snec-stat.c-gold::before  { background: var(--gold) }
.snec-stat.c-ok::before    { background: var(--ok) }
.snec-stat.c-blue::before  { background: var(--blue) }
.snec-stat-lbl { font-size:.64rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--txt-3); margin-bottom:.35rem }
.snec-stat-val { font-family:var(--serif); font-size:2.1rem; color:var(--txt); line-height:1 }
.snec-stat-sub { font-size:.72rem; color:var(--txt-3); margin-top:.25rem }

/* — Topic performance bar ————————— */
.snec-topic { margin-bottom:.6rem }
.snec-topic-hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:.25rem }
.snec-topic-name { font-size:.8rem; font-weight:500; color:var(--txt-2); text-transform:capitalize }
.snec-topic-score { font-size:.7rem; font-family:var(--mono); color:var(--txt-3) }
.snec-topic-track { background:var(--bg-raised); border-radius:99px; height:5px; overflow:hidden }
.snec-topic-fill  { height:100%; border-radius:99px; transition:width .7s cubic-bezier(.4,0,.2,1) }

/* — Badge pill ————————————————————— */
.snec-badge {
  display:inline-flex; align-items:center; gap:.3rem;
  padding:.22rem .6rem; border-radius:99px;
  font-size:.68rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase;
}
.snec-badge.bt { background:var(--accent-10); color:var(--accent); border:1px solid var(--accent-20) }
.snec-badge.bg { background:var(--gold-10);   color:var(--gold);   border:1px solid var(--gold-20) }
.snec-badge.bo { background:rgba(16,185,129,.1); color:#6EE7B7; border:1px solid rgba(16,185,129,.2) }
.snec-badge.bd { background:rgba(239,68,68,.1);  color:#FCA5A5; border:1px solid rgba(239,68,68,.2) }
.snec-badge.bm { background:var(--bg-raised); color:var(--txt-2); border:1px solid var(--border-mid) }

/* — Flashcard ————————————————————— */
.snec-card {
  background: var(--bg-card);
  border: 1px solid var(--border-mid);
  border-radius: var(--r3);
  padding: 2.5rem 2rem;
  min-height: 200px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; position: relative; overflow: hidden;
  box-shadow: var(--sh), inset 0 1px 0 rgba(255,255,255,0.04);
}
.snec-card::before {
  content:''; position:absolute; inset:-1px; border-radius: var(--r3);
  background: linear-gradient(135deg, rgba(6,214,192,.12) 0%, transparent 60%, rgba(59,130,246,.06) 100%);
  pointer-events:none;
}
.snec-card-topic {
  font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.12em;
  color:var(--accent); margin-bottom:1.2rem;
  display:flex; align-items:center; gap:.4rem;
}
.snec-card-topic::before, .snec-card-topic::after { content:''; width:20px; height:1px; background:rgba(6,214,192,.3) }
.snec-card-q {
  font-family: var(--serif); font-size: 1.45rem;
  color: var(--txt); line-height: 1.45; max-width: 580px;
}
.snec-card-a { font-size:.95rem; color:var(--txt-2); line-height:1.65; max-width:560px }
.snec-card-reveal {
  font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em;
  color:var(--txt-3); margin-top:1.5rem;
}

/* — Rating buttons ———————————————— */
.snec-ratings { display:flex; gap:.4rem; justify-content:center; flex-wrap:wrap; margin-top:1.2rem }

/* — Login hero ———————————————————— */
.snec-login-hero {
  padding: 3rem 2rem;
  display: flex; flex-direction: column;
  justify-content: center; min-height: 400px;
}
.snec-login-eyeball {
  font-size: 3.5rem; margin-bottom: 1.5rem;
  filter: drop-shadow(0 0 20px rgba(6,214,192,.4));
}
.snec-login-title {
  font-family: var(--serif);
  font-size: 2.6rem; font-weight: 400;
  color: var(--txt); letter-spacing: -.03em;
  line-height: 1.2; margin-bottom: .75rem;
}
.snec-login-title em { color: var(--accent); font-style: italic }
.snec-login-desc { font-size:.88rem; color:var(--txt-2); line-height:1.65; max-width:420px; margin-bottom:2rem }
.snec-feature-grid { display:grid; grid-template-columns:1fr 1fr; gap:.6rem }
.snec-feature-item {
  background: var(--bg-raised); border: 1px solid var(--border);
  border-radius: var(--r); padding: .65rem .85rem;
  display:flex; align-items:flex-start; gap:.55rem;
}
.snec-feature-icon { font-size:1rem; flex-shrink:0; margin-top:.05rem }
.snec-feature-name { font-size:.78rem; font-weight:600; color:var(--txt); margin-bottom:.1rem }
.snec-feature-desc { font-size:.7rem; color:var(--txt-3); line-height:1.4 }

/* — XP toast ——————————————————————— */
.snec-xp-toast {
  background: linear-gradient(135deg, var(--bg-raised), var(--bg-card));
  border: 1px solid var(--accent-20);
  border-radius: var(--r2); padding: 1.5rem 2rem; text-align: center;
  animation: xpGlow 2.5s ease-in-out infinite;
}
@keyframes xpGlow {
  0%,100% { box-shadow: 0 0 12px var(--accent-glow) }
  50%      { box-shadow: 0 0 28px var(--accent-glow) }
}
.snec-xp-amount { font-family:var(--serif); font-size:3.2rem; color:var(--accent); line-height:1 }
.snec-xp-label  { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.12em; color:var(--txt-3) }

/* — Domain score card ————————————— */
.snec-domain {
  background:var(--bg-card); border:1px solid var(--border);
  border-radius:var(--r2); padding:1rem 1.25rem; text-align:center;
  position:relative; overflow:hidden;
  box-shadow: var(--sh-xs);
  transition: border-color .2s, box-shadow .2s;
}
.snec-domain:hover { border-color: rgba(6,214,192,0.18); box-shadow: var(--ring-card-hover) }
.snec-domain-lbl { font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--txt-3); margin-bottom:.45rem }
.snec-domain-val { font-family:var(--serif); font-size:2rem; line-height:1; margin-bottom:.5rem }
.snec-domain-track { background:var(--bg-raised); border-radius:99px; height:4px; overflow:hidden }
.snec-domain-fill  { height:100%; border-radius:99px }

/* — Case hint bubble ————————————— */
.snec-hint {
  background: rgba(245,158,11,.07);
  border: 1px solid rgba(245,158,11,.2);
  border-radius: var(--r);
  padding: .6rem .9rem;
  font-size: .82rem; color: #FCD34D; line-height: 1.5;
  margin-bottom: .5rem;
  box-shadow: var(--sh-xs);
}

/* — Nav section divider —————————— */
.snec-nav-sep {
  font-size:.6rem; font-weight:700; text-transform:uppercase; letter-spacing:.12em;
  color:var(--txt-3); padding:.35rem .25rem .2rem;
}

/* — Getting started card —————————— */
.snec-start-item {
  display:flex; align-items:flex-start; gap:.75rem;
  padding: .85rem 1rem;
  background:var(--bg-raised); border:1px solid var(--border);
  border-radius:var(--r); margin-bottom:.45rem;
  transition: border-color .2s;
}
.snec-start-item:hover { border-color:var(--border-hi) }
.snec-start-num {
  width:22px; height:22px; border-radius:50%; flex-shrink:0;
  background:var(--accent-10); border:1px solid var(--accent-20);
  display:flex; align-items:center; justify-content:center;
  font-size:.68rem; font-weight:700; color:var(--accent); margin-top:.05rem;
}
.snec-start-title { font-size:.84rem; font-weight:600; color:var(--txt); margin-bottom:.15rem }
.snec-start-desc  { font-size:.75rem; color:var(--txt-3); line-height:1.45 }

/* — Progress bar (named) —————————— */
.snec-progress-wrap { margin-bottom:.2rem }
.snec-progress-meta {
  display:flex; justify-content:space-between; align-items:center;
  margin-bottom:.35rem;
}
.snec-progress-title { font-size:.8rem; font-weight:600; color:var(--txt-2) }
.snec-progress-right { font-size:.7rem; font-family:var(--mono); color:var(--txt-3) }
.snec-progress-track { background:var(--bg-raised); border-radius:99px; height:6px; overflow:hidden }
.snec-progress-fill  {
  height:100%; border-radius:99px;
  background:linear-gradient(90deg,var(--accent),#04C4B2);
  box-shadow:0 0 8px var(--accent-glow);
  transition:width .8s cubic-bezier(.4,0,.2,1);
}
</style>
"""

# ─── HTML component helpers ────────────────────────────────────────────────────

def ph(title: str, subtitle: str = "") -> str:
    """Page header."""
    sub = f'<div class="snec-ph-sub">{subtitle}</div>' if subtitle else ""
    return f'<div class="snec-ph"><h1>{title}</h1>{sub}</div>'


def section_label(text: str) -> str:
    return f'<div class="snec-label">{text}</div>'


def stat_card(label: str, value: str, sub: str = "", color: str = "c-teal") -> str:
    sub_html = f'<div class="snec-stat-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="snec-stat {color}">'
        f'  <div class="snec-stat-lbl">{label}</div>'
        f'  <div class="snec-stat-val">{value}</div>'
        f'  {sub_html}'
        f'</div>'
    )


def topic_bar(name: str, ef: float) -> str:
    pct = min(100, int((ef - 1.3) / (3.0 - 1.3) * 100))
    if pct >= 65:
        color, dot = "#10B981", "🟢"
    elif pct >= 35:
        color, dot = "#F59E0B", "🟡"
    else:
        color, dot = "#EF4444", "🔴"
    return (
        f'<div class="snec-topic">'
        f'  <div class="snec-topic-hdr">'
        f'    <span class="snec-topic-name">{dot} {name}</span>'
        f'    <span class="snec-topic-score">{ef:.2f} EF</span>'
        f'  </div>'
        f'  <div class="snec-topic-track">'
        f'    <div class="snec-topic-fill" style="width:{pct}%;background:{color}"></div>'
        f'  </div>'
        f'</div>'
    )


def badge(text: str, style: str = "bt") -> str:
    return f'<span class="snec-badge {style}">{text}</span>'


def user_chip(name: str) -> str:
    initials = "".join(p[0].upper() for p in name.split()[:2])
    return (
        f'<div class="snec-user-chip">'
        f'  <div class="snec-avatar">{initials}</div>'
        f'  <div class="snec-user-name">{name}</div>'
        f'</div>'
    )


def wordmark() -> str:
    return (
        '<div class="snec-wordmark">'
        '  <div class="snec-wordmark-icon">👁️</div>'
        '  <div class="snec-wordmark-text">'
        '    <div class="snec-wordmark-name">EyeQ</div>'
        '    <div class="snec-wordmark-sub">Ophthalmology Training</div>'
        '  </div>'
        '</div>'
    )


def xp_toast(xp: int) -> str:
    return (
        f'<div class="snec-xp-toast">'
        f'  <div class="snec-xp-amount">+{xp:,}</div>'
        f'  <div class="snec-xp-label">XP Earned</div>'
        f'</div>'
    )


def domain_card(label: str, icon: str, score: int) -> str:
    pct = score * 10
    if score >= 8:
        color, txt_color = "#10B981", "#6EE7B7"
    elif score >= 5:
        color, txt_color = "#F59E0B", "#FCD34D"
    else:
        color, txt_color = "#EF4444", "#FCA5A5"
    return (
        f'<div class="snec-domain">'
        f'  <div class="snec-domain-lbl">{icon} {label}</div>'
        f'  <div class="snec-domain-val" style="color:{txt_color}">{score}<span style="font-size:1rem;color:var(--txt-3)">/10</span></div>'
        f'  <div class="snec-domain-track">'
        f'    <div class="snec-domain-fill" style="width:{pct}%;background:{color}"></div>'
        f'  </div>'
        f'</div>'
    )


def flashcard_q(question: str, topic: str = "") -> str:
    topic_html = f'<div class="snec-card-topic">{topic}</div>' if topic else ""
    return (
        f'<div class="snec-card">'
        f'  {topic_html}'
        f'  <div class="snec-card-q">{question}</div>'
        f'  <div class="snec-card-reveal">↓ think before revealing ↓</div>'
        f'</div>'
    )


def flashcard_a(answer: str) -> str:
    return (
        f'<div class="snec-card" style="border-color:rgba(6,214,192,.3)">'
        f'  <div class="snec-card-a">{answer}</div>'
        f'</div>'
    )


def start_item(num: int, title: str, desc: str) -> str:
    return (
        f'<div class="snec-start-item">'
        f'  <div class="snec-start-num">{num}</div>'
        f'  <div>'
        f'    <div class="snec-start-title">{title}</div>'
        f'    <div class="snec-start-desc">{desc}</div>'
        f'  </div>'
        f'</div>'
    )


def named_progress(title: str, right: str, pct: float) -> str:
    w = int(min(100, max(0, pct * 100))  )
    return (
        f'<div class="snec-progress-wrap">'
        f'  <div class="snec-progress-meta">'
        f'    <span class="snec-progress-title">{title}</span>'
        f'    <span class="snec-progress-right">{right}</span>'
        f'  </div>'
        f'  <div class="snec-progress-track">'
        f'    <div class="snec-progress-fill" style="width:{w}%"></div>'
        f'  </div>'
        f'</div>'
    )
