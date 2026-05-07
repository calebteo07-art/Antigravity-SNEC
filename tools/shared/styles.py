"""SNEC AI — Design system: CSS injection + HTML component helpers."""

ACCENT  = "#00CEB8"
GREEN   = "#00E676"
GOLD    = "#FFB300"
SUCCESS = "#00E676"
DANGER  = "#FF3D57"
INFO    = "#2979FF"

SNEC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════════════ */
:root {
  --bg:          #020B1A;
  --bg-surface:  #05122A;
  --bg-card:     #081629;
  --bg-raised:   #0C1E38;

  --glass-bg:     rgba(8, 22, 42, 0.62);
  --glass-bg-hi:  rgba(12, 28, 52, 0.72);
  --glass-border: rgba(255,255,255,0.07);
  --glass-hi:     rgba(255,255,255,0.05);

  --border:      rgba(255,255,255,0.05);
  --border-mid:  rgba(255,255,255,0.09);
  --border-hi:   rgba(255,255,255,0.14);

  --accent:      #00CEB8;
  --accent-10:   rgba(0,206,184,.10);
  --accent-20:   rgba(0,206,184,.20);
  --accent-glow: rgba(0,206,184,.30);
  --accent-hi:   #00E8D2;

  --green:       #00E676;
  --green-10:    rgba(0,230,118,.10);
  --green-20:    rgba(0,230,118,.20);
  --green-glow:  rgba(0,230,118,.28);

  --gold:        #FFB300;
  --gold-10:     rgba(255,179,0,.10);
  --gold-20:     rgba(255,179,0,.20);
  --gold-glow:   rgba(255,179,0,.28);

  --ok:          #00E676;
  --warn:        #FFB300;
  --danger:      #FF3D57;
  --blue:        #2979FF;
  --purple:      #AB47BC;

  --txt:         #E5F2FF;
  --txt-2:       #6A9AC4;
  --txt-3:       #2E5C8A;

  --display:     'Chakra Petch', 'Rajdhani', sans-serif;
  --sans:        'Plus Jakarta Sans', system-ui, sans-serif;
  --mono:        'JetBrains Mono', monospace;

  --r:   8px;
  --r2: 14px;
  --r3: 20px;
  --r4: 28px;

  --sh-xs: 0 1px 3px rgba(0,0,0,.22);
  --sh-sm: 0 2px 8px rgba(0,0,0,.32), 0 1px 2px rgba(0,0,0,.22);
  --sh:    0 6px 22px rgba(0,0,0,.42), 0 2px 6px rgba(0,0,0,.26);
  --sh2:   0 12px 40px rgba(0,0,0,.52), 0 4px 12px rgba(0,0,0,.30);

  --ring-card:       0 0 0 1px var(--border);
  --ring-card-hover: 0 0 0 1px rgba(0,206,184,.24), 0 0 28px rgba(0,206,184,.08);
  --ring-focus:      0 0 0 3px rgba(0,206,184,.20);
}

/* ═══════════════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════════════ */
@keyframes fadeUp {
  from { opacity:0; transform:translateY(12px) }
  to   { opacity:1; transform:translateY(0) }
}
@keyframes card-flip-in {
  0%   { transform: perspective(800px) rotateY(-90deg); opacity:0 }
  100% { transform: perspective(800px) rotateY(0deg); opacity:1 }
}
@keyframes xp-surge {
  0%   { transform: scale(.4) translateY(16px); opacity:0 }
  60%  { transform: scale(1.12) translateY(-4px); opacity:1 }
  100% { transform: scale(1) translateY(0); opacity:1 }
}
@keyframes xp-glow {
  0%,100% { box-shadow: 0 0 22px var(--accent-glow), 0 0 0 1px var(--accent-20) }
  50%      { box-shadow: 0 0 50px var(--accent-glow), 0 0 70px rgba(0,206,184,.06), 0 0 0 1px var(--accent-20) }
}
@keyframes particle-rise {
  0%   { transform: translateY(0) translateX(0) scale(1); opacity:.9 }
  100% { transform: translateY(-80px) translateX(var(--pdx,0px)) scale(0); opacity:0 }
}
@keyframes breathe {
  0%,100% { box-shadow: 0 0 18px var(--accent-glow) }
  50%      { box-shadow: 0 0 38px var(--accent-glow), 0 0 55px rgba(0,206,184,.06) }
}
@keyframes btn-shine {
  0%       { left:-80%; opacity:0 }
  20%      { opacity:1 }
  45%      { left:140% }
  46%,100% { left:-80%; opacity:0 }
}
@keyframes badge-pop {
  0%   { transform: scale(0) rotate(-10deg); opacity:0 }
  70%  { transform: scale(1.14) rotate(3deg); opacity:1 }
  100% { transform: scale(1) rotate(0deg); opacity:1 }
}
@keyframes scan {
  0%   { left:-80% }
  100% { left:130% }
}

/* ═══════════════════════════════════════════════════
   APP SHELL
═══════════════════════════════════════════════════ */
.stApp {
  background:
    radial-gradient(circle at 1px 1px, rgba(0,206,184,.024) 1px, transparent 0),
    radial-gradient(ellipse 90% 55% at 10% -12%, rgba(0,206,184,.10) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 95% 108%, rgba(0,230,118,.06) 0%, transparent 55%),
    radial-gradient(ellipse 50% 38% at 50% 128%, rgba(255,179,0,.04) 0%, transparent 55%),
    radial-gradient(ellipse 42% 35% at 112% 50%, rgba(41,121,255,.04) 0%, transparent 60%),
    #020B1A !important;
  background-size: 22px 22px, 100% 100%, 100% 100%, 100% 100%, 100% 100% !important;
  font-family: var(--sans) !important;
  color: var(--txt) !important;
}

::-webkit-scrollbar          { width:4px; height:4px }
::-webkit-scrollbar-track    { background:transparent }
::-webkit-scrollbar-thumb    { background:rgba(0,206,184,.2); border-radius:4px }
::-webkit-scrollbar-thumb:hover { background:rgba(0,206,184,.4) }

#MainMenu, footer { display:none !important }
header[data-testid="stHeader"] {
  background: rgba(2,11,26,.88) !important;
  backdrop-filter: blur(22px) saturate(160%) !important;
  -webkit-backdrop-filter: blur(22px) saturate(160%) !important;
  border-bottom: 1px solid rgba(0,206,184,.10) !important;
}
.stDeployButton { display:none !important }

/* ═══════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: rgba(2,10,26,.93) !important;
  backdrop-filter: blur(28px) !important;
  -webkit-backdrop-filter: blur(28px) !important;
  border-right: 1px solid rgba(0,206,184,.08) !important;
}
[data-testid="stSidebar"] > div:first-child { background:transparent !important }
[data-testid="stSidebar"]::after {
  content:''; position:absolute; top:0; left:0;
  width:2px; height:100%;
  background: linear-gradient(180deg, var(--accent) 0%, var(--green) 45%, transparent 80%);
  opacity:.7; pointer-events:none;
}
[data-testid="stSidebarContent"] .stMarkdown p {
  color:var(--txt-3) !important; font-size:.77rem !important;
}
[data-testid="stSidebar"] .stButton > button {
  background:transparent !important; color:var(--txt-3) !important;
  border:1px solid transparent !important; border-radius:var(--r) !important;
  font-family:var(--sans) !important; font-size:.8rem !important;
  font-weight:500 !important; letter-spacing:.01em !important;
  transition:all .2s !important; box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background:rgba(0,206,184,.06) !important; color:var(--accent) !important;
  border-color:rgba(0,206,184,.14) !important; transform:none !important;
  box-shadow:0 0 14px rgba(0,206,184,.08) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background:rgba(0,206,184,.10) !important; color:var(--accent) !important;
  border-color:rgba(0,206,184,.22) !important; font-weight:600 !important;
  box-shadow:inset 0 0 18px rgba(0,206,184,.05) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background:rgba(0,206,184,.16) !important; transform:none !important;
}

/* ═══════════════════════════════════════════════════
   MAIN CONTAINER
═══════════════════════════════════════════════════ */
.main .block-container {
  padding:2.25rem 2.75rem !important;
  max-width:1180px !important;
}
.main .block-container > div > div {
  animation: fadeUp .35s ease both;
}

/* ═══════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════ */
h1 {
  font-family:var(--display) !important;
  font-size:2.1rem !important; font-weight:700 !important;
  color:var(--txt) !important; letter-spacing:.04em !important;
  line-height:1.1 !important; margin-bottom:.1rem !important;
  text-transform:uppercase !important;
  text-shadow:0 0 40px rgba(0,206,184,.14);
}
h2 {
  font-family:var(--display) !important;
  font-size:1.45rem !important; font-weight:600 !important;
  color:var(--txt) !important; letter-spacing:.03em !important;
  line-height:1.2 !important; text-transform:uppercase !important;
}
h3 {
  font-family:var(--display) !important;
  font-size:.68rem !important; font-weight:700 !important;
  color:var(--txt-3) !important; text-transform:uppercase !important;
  letter-spacing:.14em !important;
}
p, li { color:var(--txt-2) !important; font-size:.88rem !important; line-height:1.72 !important }
strong { color:var(--txt) !important }
code {
  font-family:var(--mono) !important;
  background:rgba(0,206,184,.08) !important; color:var(--accent) !important;
  padding:2px 7px !important; border-radius:5px !important; font-size:.82em !important;
  border:1px solid rgba(0,206,184,.16) !important;
}
a { color:var(--accent) !important; text-decoration:none !important }
a:hover { text-decoration:underline !important; text-underline-offset:3px !important }
[data-testid="stCaptionContainer"] p, .stCaption { color:var(--txt-3) !important; font-size:.72rem !important }
hr { border:none !important; border-top:1px solid var(--border) !important; margin:1.5rem 0 !important }

/* ═══════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════ */
.stButton > button {
  background:var(--glass-bg) !important; color:var(--txt-2) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r) !important;
  font-family:var(--sans) !important; font-size:.83rem !important;
  font-weight:500 !important; letter-spacing:.01em !important;
  padding:.45rem 1.1rem !important; transition:all .2s ease !important;
  backdrop-filter:blur(8px) !important;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-xs) !important;
  position:relative !important; overflow:hidden !important;
}
.stButton > button:hover {
  background:rgba(0,206,184,.08) !important; color:var(--txt) !important;
  border-color:rgba(0,206,184,.20) !important; transform:translateY(-1px) !important;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-sm), 0 0 18px rgba(0,206,184,.08) !important;
}
.stButton > button[kind="primary"] {
  background:linear-gradient(135deg, #00E8D5 0%, #00CEB8 55%, #009E8A 100%) !important;
  color:#020B1A !important; border:none !important;
  font-family:var(--display) !important; font-size:.77rem !important;
  font-weight:700 !important; letter-spacing:.07em !important;
  text-transform:uppercase !important;
  box-shadow:0 0 0 1px rgba(0,206,184,.38),
             0 4px 22px rgba(0,206,184,.28),
             0 0 44px rgba(0,206,184,.08),
             inset 0 1px 0 rgba(255,255,255,.22) !important;
}
.stButton > button[kind="primary"]::before {
  content:''; position:absolute; top:-50%; left:-80%;
  width:35%; height:200%; background:rgba(255,255,255,.2);
  transform:skewX(-25deg);
  animation:btn-shine 3.5s ease-in-out infinite;
}
.stButton > button[kind="primary"]:hover {
  background:linear-gradient(135deg, #00FFEC 0%, #00E8D5 55%, #00CEB8 100%) !important;
  color:#020B1A !important; transform:translateY(-2px) !important;
  box-shadow:0 0 0 1px rgba(0,206,184,.45),
             0 6px 30px rgba(0,206,184,.40),
             0 0 60px rgba(0,206,184,.12),
             inset 0 1px 0 rgba(255,255,255,.28) !important;
}

/* ═══════════════════════════════════════════════════
   FORM INPUTS
═══════════════════════════════════════════════════ */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
  color:var(--txt-3) !important; font-size:.68rem !important;
  font-weight:700 !important; text-transform:uppercase !important;
  letter-spacing:.11em !important; font-family:var(--display) !important;
}
.stCheckbox label { color:var(--txt-2) !important; font-size:.84rem !important }
.stCheckbox label span[data-baseweb="checkbox"] {
  background:var(--bg-raised) !important; border-color:var(--border-hi) !important;
}
.stTextInput > div > div, .stTextArea > div > div {
  background:var(--glass-bg) !important; backdrop-filter:blur(12px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r) !important;
  transition:border-color .2s, box-shadow .2s !important;
  box-shadow:inset 0 1px 5px rgba(0,0,0,.22) !important;
}
.stTextInput > div > div:focus-within, .stTextArea > div > div:focus-within {
  border-color:rgba(0,206,184,.42) !important;
  box-shadow:var(--ring-focus), inset 0 1px 5px rgba(0,0,0,.10) !important;
}
.stTextInput input, .stTextArea textarea {
  background:transparent !important; color:var(--txt) !important;
  font-family:var(--sans) !important; caret-color:var(--accent) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:var(--txt-3) !important }
.stSelectbox > div > div {
  background:var(--glass-bg) !important; backdrop-filter:blur(12px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r) !important;
  color:var(--txt) !important;
}
.stSelectbox > div > div:focus-within {
  border-color:rgba(0,206,184,.42) !important; box-shadow:var(--ring-focus) !important;
}
.stNumberInput > div > div {
  background:var(--glass-bg) !important; backdrop-filter:blur(12px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r) !important;
}
.stNumberInput input {
  background:transparent !important; color:var(--txt) !important;
  font-family:var(--mono) !important;
}
[data-testid="stChatInput"] {
  background:var(--glass-bg) !important; backdrop-filter:blur(16px) !important;
  border:1px solid rgba(0,206,184,.12) !important; border-radius:var(--r2) !important;
  transition:border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color:rgba(0,206,184,.36) !important;
  box-shadow:var(--ring-focus), 0 0 26px rgba(0,206,184,.12) !important;
}
[data-testid="stChatInput"] textarea {
  background:transparent !important; color:var(--txt) !important;
  font-family:var(--sans) !important;
}
[data-testid="stChatInput"] button { background:var(--accent) !important; border-radius:var(--r) !important }

/* ═══════════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════════ */
[data-testid="metric-container"] {
  background:var(--glass-bg) !important;
  backdrop-filter:blur(22px) saturate(140%) !important;
  -webkit-backdrop-filter:blur(22px) saturate(140%) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r2) !important;
  padding:1.1rem 1.4rem !important; position:relative !important; overflow:hidden !important;
  transition:border-color .25s, box-shadow .25s !important;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-sm) !important;
}
[data-testid="metric-container"]::before {
  content:''; position:absolute; top:0; left:0; width:3px; height:100%;
  background:linear-gradient(180deg,var(--accent),transparent);
}
[data-testid="metric-container"]::after {
  content:''; position:absolute; top:0; left:0; width:100%; height:1px;
  background:linear-gradient(90deg,var(--accent-10),transparent,var(--accent-10));
}
[data-testid="metric-container"]:hover {
  border-color:rgba(0,206,184,.22) !important;
  box-shadow:var(--ring-card-hover), inset 0 1px 0 var(--glass-hi), var(--sh) !important;
}
[data-testid="stMetricLabel"] {
  color:var(--txt-3) !important; font-family:var(--display) !important;
  font-size:.62rem !important; font-weight:700 !important;
  text-transform:uppercase !important; letter-spacing:.13em !important;
}
[data-testid="stMetricValue"] {
  color:var(--txt) !important; font-family:var(--display) !important;
  font-size:1.85rem !important; font-weight:700 !important;
}
[data-testid="stMetricDelta"] { font-size:.73rem !important }

/* ═══════════════════════════════════════════════════
   PROGRESS
═══════════════════════════════════════════════════ */
.stProgress > div {
  background:rgba(0,206,184,.06) !important; border-radius:99px !important; height:5px !important;
}
.stProgress > div > div {
  background:linear-gradient(90deg,var(--accent),var(--green)) !important;
  border-radius:99px !important; height:100% !important;
  box-shadow:0 0 12px var(--accent-glow) !important;
  transition:width .7s cubic-bezier(.4,0,.2,1) !important;
}
[data-testid="stProgressLabel"] {
  color:var(--txt-3) !important; font-size:.7rem !important; font-family:var(--mono) !important;
}

/* ═══════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════ */
.stAlert { border-radius:var(--r) !important; border-left-width:3px !important; backdrop-filter:blur(12px) !important }
.stInfo    { background:rgba(41,121,255,.07) !important; border-color:var(--blue) !important }
.stInfo p  { color:#90CAF9 !important }
.stSuccess { background:rgba(0,230,118,.07) !important; border-color:var(--ok) !important }
.stSuccess p { color:#69F0AE !important }
.stWarning { background:rgba(255,179,0,.07) !important; border-color:var(--warn) !important }
.stWarning p { color:#FFD54F !important }
.stError   { background:rgba(255,61,87,.07) !important; border-color:var(--danger) !important }
.stError p { color:#EF9A9A !important }

/* ═══════════════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  background:var(--glass-bg) !important; backdrop-filter:blur(16px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r2) !important;
  margin-bottom:.6rem !important; transition:border-color .2s !important;
}
[data-testid="stChatMessage"]:hover { border-color:rgba(0,206,184,.12) !important }
[data-testid="stChatMessageContent"] p {
  color:var(--txt-2) !important; font-size:.88rem !important; line-height:1.72 !important;
}

/* ═══════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background:var(--glass-bg) !important; backdrop-filter:blur(16px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r) !important;
  overflow:hidden !important;
}
[data-testid="stExpander"] summary {
  background:transparent !important; color:var(--txt-2) !important;
  font-size:.83rem !important; font-weight:500 !important; padding:.7rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
  background:rgba(0,206,184,.05) !important; color:var(--txt) !important;
}
.streamlit-expanderContent {
  background:rgba(2,11,26,.4) !important; border-top:1px solid var(--glass-border) !important;
}

/* ═══════════════════════════════════════════════════
   BORDER CONTAINERS
═══════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--glass-bg) !important; backdrop-filter:blur(20px) !important;
  -webkit-backdrop-filter:blur(20px) !important;
  border:1px solid var(--glass-border) !important; border-radius:var(--r2) !important;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-sm) !important;
  transition:border-color .25s, box-shadow .25s !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color:rgba(0,206,184,.22) !important;
  box-shadow:var(--ring-card-hover), inset 0 1px 0 var(--glass-hi), var(--sh) !important;
}

/* ═══════════════════════════════════════════════════
   TABLES
═══════════════════════════════════════════════════ */
thead tr th {
  background:rgba(12,30,56,.82) !important; color:var(--txt-3) !important;
  font-family:var(--display) !important; font-size:.63rem !important;
  font-weight:700 !important; text-transform:uppercase !important; letter-spacing:.11em !important;
}
tbody tr td {
  background:var(--glass-bg) !important; color:var(--txt-2) !important;
  border-color:var(--border) !important; font-size:.83rem !important;
}
tbody tr:hover td { background:rgba(0,206,184,.04) !important }

/* ═══════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════ */
.stSpinner > div { border-color:var(--accent) transparent transparent transparent !important }
.stImage img {
  border-radius:var(--r) !important; border:1px solid var(--glass-border) !important;
  box-shadow:0 4px 22px rgba(0,0,0,.42) !important;
}

/* ═══════════════════════════════════════════════════
   SNEC CUSTOM COMPONENTS
═══════════════════════════════════════════════════ */

/* — Wordmark — */
.snec-wordmark {
  display:flex; align-items:center; gap:.65rem;
  padding:.5rem .25rem 1rem; user-select:none;
}
.snec-wordmark-icon {
  width:36px; height:36px; border-radius:50%;
  background:linear-gradient(135deg, #00E8D5 0%, var(--accent) 55%, #009E8A 100%);
  display:flex; align-items:center; justify-content:center;
  font-size:1.1rem; flex-shrink:0;
  animation:breathe 3.2s ease-in-out infinite;
}
.snec-wordmark-text { line-height:1.15 }
.snec-wordmark-name {
  font-family:var(--display); font-size:1rem; font-weight:700;
  color:var(--txt); letter-spacing:.07em; text-transform:uppercase;
}
.snec-wordmark-sub {
  font-size:.59rem; font-weight:600; text-transform:uppercase;
  letter-spacing:.11em; color:var(--txt-3);
}

/* — User chip — */
.snec-user-chip {
  display:flex; align-items:center; gap:.55rem;
  padding:.5rem .72rem; background:rgba(0,206,184,.08);
  backdrop-filter:blur(12px); border:1px solid rgba(0,206,184,.18);
  border-radius:var(--r); margin-bottom:.72rem;
}
.snec-avatar {
  width:28px; height:28px; border-radius:50%;
  background:linear-gradient(135deg, var(--accent), #009E8A);
  display:flex; align-items:center; justify-content:center;
  font-family:var(--display); font-size:.7rem; font-weight:700;
  color:#020B1A; flex-shrink:0; box-shadow:0 0 12px var(--accent-glow);
}
.snec-user-name {
  font-size:.79rem; font-weight:600; color:var(--accent);
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}

/* — Section label — */
.snec-label {
  font-family:var(--display); font-size:.61rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.15em; color:var(--txt-3);
  display:flex; align-items:center; gap:.6rem; margin:1.4rem 0 .8rem;
}
.snec-label::after {
  content:''; flex:1; height:1px;
  background:linear-gradient(90deg, var(--border), transparent);
}

/* — Page header — */
.snec-ph { margin-bottom:1.6rem }
.snec-ph h1 {
  font-family:var(--display) !important; font-size:2rem !important;
  font-weight:700 !important; color:var(--txt) !important;
  letter-spacing:.05em !important; line-height:1.1 !important;
  margin:0 0 .2rem !important; text-transform:uppercase !important;
  text-shadow:0 0 45px rgba(0,206,184,.14);
}
.snec-ph-sub { font-size:.8rem; color:var(--txt-3); line-height:1.55; max-width:620px }

/* — Stat card — */
.snec-stat {
  background:var(--glass-bg); backdrop-filter:blur(22px) saturate(140%);
  -webkit-backdrop-filter:blur(22px) saturate(140%);
  border:1px solid var(--glass-border); border-radius:var(--r2);
  padding:1.1rem 1.4rem; position:relative; overflow:hidden;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-sm);
  transition:border-color .25s, box-shadow .25s, transform .25s;
}
.snec-stat:hover {
  border-color:rgba(0,206,184,.22);
  box-shadow:var(--ring-card-hover), inset 0 1px 0 var(--glass-hi), var(--sh);
  transform:translateY(-2px);
}
.snec-stat::before { content:''; position:absolute; top:0; left:0; width:3px; height:100% }
.snec-stat::after  {
  content:''; position:absolute; top:0; left:0; width:100%; height:1px; opacity:.5;
}
.snec-stat.c-teal::before { background:var(--accent) }
.snec-stat.c-teal::after  { background:linear-gradient(90deg, rgba(0,206,184,.5), transparent) }
.snec-stat.c-gold::before { background:var(--gold) }
.snec-stat.c-gold::after  { background:linear-gradient(90deg, rgba(255,179,0,.5), transparent) }
.snec-stat.c-ok::before   { background:var(--ok) }
.snec-stat.c-ok::after    { background:linear-gradient(90deg, rgba(0,230,118,.5), transparent) }
.snec-stat.c-blue::before { background:var(--blue) }
.snec-stat.c-blue::after  { background:linear-gradient(90deg, rgba(41,121,255,.5), transparent) }
.snec-stat-lbl {
  font-family:var(--display); font-size:.61rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.13em; color:var(--txt-3); margin-bottom:.4rem;
}
.snec-stat-val {
  font-family:var(--display); font-size:2.25rem; font-weight:700;
  color:var(--txt); line-height:1;
}
.snec-stat-sub { font-size:.69rem; color:var(--txt-3); margin-top:.28rem }

/* — Topic bar — */
.snec-topic { margin-bottom:.65rem }
.snec-topic-hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:.28rem }
.snec-topic-name { font-size:.8rem; font-weight:500; color:var(--txt-2); text-transform:capitalize }
.snec-topic-score { font-size:.7rem; font-family:var(--mono); color:var(--txt-3) }
.snec-topic-track { background:rgba(0,206,184,.06); border-radius:99px; height:5px; overflow:hidden }
.snec-topic-fill  { height:100%; border-radius:99px; transition:width .8s cubic-bezier(.4,0,.2,1) }

/* — Badge pill — */
.snec-badge {
  display:inline-flex; align-items:center; gap:.3rem;
  padding:.22rem .65rem; border-radius:99px;
  font-family:var(--display); font-size:.62rem; font-weight:700;
  letter-spacing:.06em; text-transform:uppercase;
  animation:badge-pop .4s cubic-bezier(0.34,1.56,0.64,1) both;
}
.snec-badge.bt { background:rgba(0,206,184,.1); color:var(--accent); border:1px solid rgba(0,206,184,.22) }
.snec-badge.bg { background:rgba(255,179,0,.1);  color:var(--gold);   border:1px solid rgba(255,179,0,.22) }
.snec-badge.bo { background:rgba(0,230,118,.1);  color:var(--green);  border:1px solid rgba(0,230,118,.22) }
.snec-badge.bd { background:rgba(255,61,87,.1);  color:#FF8A9A;       border:1px solid rgba(255,61,87,.22) }
.snec-badge.bm { background:var(--glass-bg);     color:var(--txt-2);  border:1px solid var(--glass-border) }

/* — Flashcard — */
.snec-card {
  background:var(--glass-bg); backdrop-filter:blur(22px) saturate(150%);
  -webkit-backdrop-filter:blur(22px) saturate(150%);
  border:1px solid var(--glass-border); border-radius:var(--r3);
  padding:2.5rem 2rem; min-height:220px;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  text-align:center; position:relative; overflow:hidden;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh);
  animation:fadeUp .3s ease both;
}
.snec-card::before {
  content:''; position:absolute; inset:-1px; border-radius:var(--r3);
  background:
    radial-gradient(ellipse 60% 50% at 10% 0%, rgba(0,206,184,.11) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(41,121,255,.06) 0%, transparent 60%);
  pointer-events:none;
}
.snec-card-topic {
  font-family:var(--display); font-size:.61rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.15em; color:var(--accent);
  margin-bottom:1.2rem; display:flex; align-items:center; gap:.45rem;
}
.snec-card-topic::before, .snec-card-topic::after {
  content:''; width:22px; height:1px;
  background:linear-gradient(90deg, transparent, rgba(0,206,184,.4), transparent);
}
.snec-card-q {
  font-family:var(--display); font-size:1.3rem; font-weight:600;
  color:var(--txt); line-height:1.52; max-width:580px; letter-spacing:.01em;
}
.snec-card-a { font-size:.91rem; font-family:var(--sans); color:var(--txt-2); line-height:1.7; max-width:560px }
.snec-card-reveal {
  font-family:var(--display); font-size:.64rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.13em; color:var(--txt-3); margin-top:1.5rem;
}

/* Answer card — 3D flip-in */
.snec-card-answer {
  border-color:rgba(0,206,184,.24) !important;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh), 0 0 34px rgba(0,206,184,.06) !important;
  animation:card-flip-in .45s cubic-bezier(0.23,1,0.32,1) both !important;
}
.snec-card-answer::before {
  background:radial-gradient(ellipse 70% 60% at 50% 0%, rgba(0,206,184,.14) 0%, transparent 60%) !important;
}

/* — Login hero — */
.snec-login-hero {
  padding:3rem 2rem; display:flex; flex-direction:column;
  justify-content:center; min-height:440px;
}
.snec-login-eyeball {
  font-size:3.8rem; margin-bottom:1.5rem;
  filter:drop-shadow(0 0 28px rgba(0,206,184,.55));
  animation:breathe 3s ease-in-out infinite;
}
.snec-login-title {
  font-family:var(--display); font-size:2.4rem; font-weight:700;
  color:var(--txt); letter-spacing:.04em; line-height:1.15;
  margin-bottom:.75rem; text-transform:uppercase;
  text-shadow:0 0 60px rgba(0,206,184,.14);
}
.snec-login-title em { color:var(--accent); font-style:normal; text-shadow:0 0 30px var(--accent-glow) }
.snec-login-desc { font-size:.87rem; color:var(--txt-2); line-height:1.68; max-width:400px; margin-bottom:2rem }
.snec-feature-grid { display:grid; grid-template-columns:1fr 1fr; gap:.6rem }
.snec-feature-item {
  background:var(--glass-bg); backdrop-filter:blur(12px);
  border:1px solid var(--glass-border); border-radius:var(--r);
  padding:.7rem .9rem; display:flex; align-items:flex-start; gap:.55rem;
  transition:border-color .2s, transform .2s;
}
.snec-feature-item:hover { border-color:rgba(0,206,184,.20); transform:translateY(-1px) }
.snec-feature-icon { font-size:1.05rem; flex-shrink:0; margin-top:.05rem }
.snec-feature-name {
  font-family:var(--display); font-size:.73rem; font-weight:700;
  letter-spacing:.04em; text-transform:uppercase; color:var(--txt); margin-bottom:.1rem;
}
.snec-feature-desc { font-size:.68rem; color:var(--txt-3); line-height:1.46 }

/* — XP Toast — */
.snec-xp-toast {
  background:var(--glass-bg); backdrop-filter:blur(22px);
  border:1px solid rgba(0,206,184,.22); border-radius:var(--r2);
  padding:1.75rem 2.25rem; text-align:center; position:relative; overflow:visible;
  animation:xp-glow 2.8s ease-in-out infinite, fadeUp .4s ease both;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh);
}
.snec-xp-amount {
  font-family:var(--display); font-size:3.5rem; font-weight:700;
  color:var(--accent); line-height:1; letter-spacing:.05em;
  text-shadow:0 0 32px var(--accent-glow);
  animation:xp-surge .6s cubic-bezier(0.34,1.56,0.64,1) both;
}
.snec-xp-label {
  font-family:var(--display); font-size:.63rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.16em; color:var(--txt-3); margin-top:.3rem;
}
.snec-xp-particle { position:absolute; border-radius:50%; pointer-events:none; animation:particle-rise 1.2s ease-out forwards }
.snec-xp-p1 { left:12%; bottom:35%; width:8px; height:8px; background:var(--accent); --pdx:-28px; animation-delay:.05s }
.snec-xp-p2 { left:22%; bottom:42%; width:5px; height:5px; background:var(--gold);   --pdx:12px;  animation-delay:.13s }
.snec-xp-p3 { left:35%; bottom:28%; width:10px;height:10px;background:var(--green);  --pdx:-18px; animation-delay:.08s }
.snec-xp-p4 { left:50%; bottom:38%; width:7px; height:7px; background:var(--accent); --pdx:32px;  animation-delay:.16s }
.snec-xp-p5 { left:62%; bottom:30%; width:5px; height:5px; background:var(--gold);   --pdx:22px;  animation-delay:.04s }
.snec-xp-p6 { left:74%; bottom:42%; width:9px; height:9px; background:var(--green);  --pdx:-22px; animation-delay:.11s }
.snec-xp-p7 { left:84%; bottom:28%; width:6px; height:6px; background:var(--accent); --pdx:16px;  animation-delay:.07s }
.snec-xp-p8 { left:44%; bottom:48%; width:5px; height:5px; background:var(--gold);   --pdx:-12px; animation-delay:.19s }

/* — Domain score card — */
.snec-domain {
  background:var(--glass-bg); backdrop-filter:blur(20px) saturate(130%);
  -webkit-backdrop-filter:blur(20px) saturate(130%);
  border:1px solid var(--glass-border); border-radius:var(--r2);
  padding:1rem 1.25rem; text-align:center; position:relative; overflow:hidden;
  box-shadow:inset 0 1px 0 var(--glass-hi), var(--sh-sm);
  transition:border-color .25s, box-shadow .25s, transform .2s;
}
.snec-domain:hover {
  border-color:rgba(0,206,184,.22);
  box-shadow:var(--ring-card-hover), inset 0 1px 0 var(--glass-hi);
  transform:translateY(-2px);
}
.snec-domain-lbl {
  font-family:var(--display); font-size:.61rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.11em; color:var(--txt-3); margin-bottom:.5rem;
}
.snec-domain-val {
  font-family:var(--display); font-size:2rem; font-weight:700; line-height:1; margin-bottom:.55rem;
}
.snec-domain-track { background:rgba(0,206,184,.06); border-radius:99px; height:4px; overflow:hidden }
.snec-domain-fill  { height:100%; border-radius:99px; transition:width .85s cubic-bezier(.4,0,.2,1) }

/* — Case hint — */
.snec-hint {
  background:rgba(255,179,0,.06); backdrop-filter:blur(8px);
  border:1px solid rgba(255,179,0,.20); border-radius:var(--r);
  padding:.65rem .95rem; font-size:.82rem; color:#FFD54F; line-height:1.55;
  margin-bottom:.5rem; box-shadow:inset 0 0 22px rgba(255,179,0,.03);
}

/* — Nav sep — */
.snec-nav-sep {
  font-family:var(--display); font-size:.57rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.15em; color:var(--txt-3);
  padding:.35rem .25rem .2rem;
}

/* — Onboarding start item — */
.snec-start-item {
  display:flex; align-items:flex-start; gap:.75rem; padding:.9rem 1rem;
  background:var(--glass-bg); backdrop-filter:blur(12px);
  border:1px solid var(--glass-border); border-radius:var(--r);
  margin-bottom:.45rem; transition:border-color .2s, transform .2s;
}
.snec-start-item:hover { border-color:rgba(0,206,184,.20); transform:translateX(3px) }
.snec-start-num {
  width:24px; height:24px; border-radius:50%; flex-shrink:0;
  background:rgba(0,206,184,.1); border:1px solid rgba(0,206,184,.24);
  display:flex; align-items:center; justify-content:center;
  font-family:var(--display); font-size:.67rem; font-weight:700;
  color:var(--accent); margin-top:.05rem;
}
.snec-start-title {
  font-family:var(--display); font-size:.79rem; font-weight:700;
  letter-spacing:.03em; color:var(--txt); margin-bottom:.15rem; text-transform:uppercase;
}
.snec-start-desc { font-size:.74rem; color:var(--txt-3); line-height:1.5 }

/* — Named progress bar — */
.snec-progress-wrap { margin-bottom:.2rem }
.snec-progress-meta { display:flex; justify-content:space-between; align-items:center; margin-bottom:.35rem }
.snec-progress-title { font-size:.8rem; font-weight:600; color:var(--txt-2) }
.snec-progress-right { font-size:.7rem; font-family:var(--mono); color:var(--txt-3) }
.snec-progress-track { background:rgba(0,206,184,.06); border-radius:99px; height:6px; overflow:hidden }
.snec-progress-fill  {
  height:100%; border-radius:99px;
  background:linear-gradient(90deg, var(--accent), var(--green));
  box-shadow:0 0 10px var(--accent-glow);
  transition:width .9s cubic-bezier(.4,0,.2,1);
}
</style>
"""

# ─── HTML component helpers ────────────────────────────────────────────────────

def ph(title: str, subtitle: str = "") -> str:
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
        color, dot = "#00E676", "🟢"
    elif pct >= 35:
        color, dot = "#FFB300", "🟡"
    else:
        color, dot = "#FF3D57", "🔴"
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
    particles = "".join(
        f'<div class="snec-xp-particle snec-xp-p{i}"></div>'
        for i in range(1, 9)
    )
    return (
        f'<div class="snec-xp-toast">'
        f'  {particles}'
        f'  <div class="snec-xp-amount">+{xp:,}</div>'
        f'  <div class="snec-xp-label">XP Earned</div>'
        f'</div>'
    )


def domain_card(label: str, icon: str, score: int) -> str:
    pct = score * 10
    if score >= 8:
        color, txt_color = "#00E676", "#69F0AE"
    elif score >= 5:
        color, txt_color = "#FFB300", "#FFD54F"
    else:
        color, txt_color = "#FF3D57", "#EF9A9A"
    return (
        f'<div class="snec-domain">'
        f'  <div class="snec-domain-lbl">{icon} {label}</div>'
        f'  <div class="snec-domain-val" style="color:{txt_color}">'
        f'    {score}<span style="font-size:.95rem;color:var(--txt-3)">/10</span>'
        f'  </div>'
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
        f'  <div class="snec-card-reveal">— think before revealing —</div>'
        f'</div>'
    )


def flashcard_a(answer: str) -> str:
    return (
        f'<div class="snec-card snec-card-answer">'
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
    w = int(min(100, max(0, pct * 100)))
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
