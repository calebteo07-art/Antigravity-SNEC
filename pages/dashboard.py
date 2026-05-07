import json
from collections import defaultdict
from datetime import date

import streamlit as st
import streamlit.components.v1 as components
from pages._shared import _gsheets
from tools.shared.styles import ph, section_label, stat_card, topic_bar, start_item

_EYE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{background:transparent;overflow:hidden}
  body{display:flex;justify-content:center;align-items:center;height:300px}
  canvas{display:block;cursor:crosshair}
  #tip{
    position:fixed;background:rgba(2,11,26,.92);border:1px solid rgba(0,206,184,.35);
    color:#00CEB8;font-family:'Courier New',monospace;font-size:11px;font-weight:700;
    padding:5px 12px;border-radius:6px;pointer-events:none;opacity:0;
    transition:opacity .15s;z-index:999;white-space:nowrap;letter-spacing:.06em;
  }
</style>
</head>
<body>
<canvas id="c" width="280" height="280"></canvas>
<div id="tip"></div>
<script>
var TOPICS=__TOPICS__;
var canvas=document.getElementById('c'),ctx=canvas.getContext('2d'),tip=document.getElementById('tip');
var W=280,H=280,CX=140,CY=140;
var OR=122,IR=56,PR=44;
var t=0,hi=-1;
var segs=TOPICS&&TOPICS.length>0?TOPICS:[
  {name:'Retina',mastery:.75},{name:'Macula',mastery:.5},{name:'Cornea',mastery:.62},
  {name:'Glaucoma',mastery:.3},{name:'Lens',mastery:.8},{name:'Neuro',mastery:.45}
];
var N=segs.length,SA=(Math.PI*2)/N;

function mc(m,a){
  if(m>.7)return'rgba(0,206,184,'+a+')';
  if(m>.45)return'rgba(255,179,0,'+a+')';
  return'rgba(255,61,87,'+a+')';
}
function mg(m){return m>.7?'#00CEB8':m>.45?'#FFB300':'#FF3D57'}

function draw(T){
  ctx.clearRect(0,0,W,H);
  var g;
  // ambient halo
  g=ctx.createRadialGradient(CX,CY,0,CX,CY,148);
  g.addColorStop(0,'rgba(0,206,184,.05)');g.addColorStop(1,'transparent');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  // sclera outer ring glow
  g=ctx.createRadialGradient(CX,CY,OR+2,CX,CY,OR+20);
  g.addColorStop(0,'rgba(0,206,184,.09)');g.addColorStop(1,'transparent');
  ctx.beginPath();ctx.arc(CX,CY,OR+18,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  // sclera
  g=ctx.createRadialGradient(CX-20,CY-20,0,CX,CY,OR);
  g.addColorStop(0,'rgba(205,225,248,.88)');
  g.addColorStop(.65,'rgba(170,198,228,.82)');
  g.addColorStop(1,'rgba(140,172,208,.74)');
  ctx.beginPath();ctx.arc(CX,CY,OR,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  // iris segments
  var ro=T*.00025;
  segs.forEach(function(s,i){
    var a0=i*SA-Math.PI/2+ro,a1=a0+SA-.05,m=s.mastery||.5;
    var isH=i===hi,ba=.52+m*.38+(isH?.16:0)+Math.sin(T*.022+i*.8)*.04;
    ctx.beginPath();
    ctx.arc(CX,CY,OR-2,a0,a1);
    ctx.arc(CX,CY,IR+2,a1,a0,true);
    ctx.closePath();
    g=ctx.createRadialGradient(CX,CY,IR,CX,CY,OR);
    g.addColorStop(0,mc(m,ba*.55));
    g.addColorStop(.42,mc(m,ba));
    g.addColorStop(1,mc(m,ba*.68));
    ctx.fillStyle=g;ctx.fill();
    if(isH||m>.62){
      ctx.strokeStyle=mc(m,.72);ctx.lineWidth=isH?2.5:1;
      ctx.save();ctx.shadowColor=mg(m);ctx.shadowBlur=isH?22:8;ctx.stroke();ctx.restore();
    }
    // radial fiber lines
    for(var l=0;l<3;l++){
      var la=a0+(l+.5)*(SA/3);
      ctx.beginPath();
      ctx.moveTo(CX+IR*Math.cos(la),CY+IR*Math.sin(la));
      ctx.lineTo(CX+OR*Math.cos(la),CY+OR*Math.sin(la));
      ctx.strokeStyle=mc(m,.05+m*.05);ctx.lineWidth=.4;ctx.stroke();
    }
  });
  // limbal rings
  ctx.beginPath();ctx.arc(CX,CY,OR-1,0,Math.PI*2);
  ctx.strokeStyle='rgba(3,12,28,.88)';ctx.lineWidth=5;ctx.stroke();
  ctx.beginPath();ctx.arc(CX,CY,IR+1,0,Math.PI*2);
  ctx.strokeStyle='rgba(3,12,28,.92)';ctx.lineWidth=5;ctx.stroke();
  // pupil
  var pp=Math.sin(T*.016)*2.2,pr=PR+pp;
  g=ctx.createRadialGradient(CX-7,CY-7,0,CX,CY,pr);
  g.addColorStop(0,'#0C1C30');g.addColorStop(.6,'#040A12');g.addColorStop(1,'#020408');
  ctx.beginPath();ctx.arc(CX,CY,pr,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  // inner bio-glow
  var iga=.26+Math.sin(T*.022)*.09;
  g=ctx.createRadialGradient(CX,CY,PR-3,CX,CY,IR+7);
  g.addColorStop(0,'rgba(0,206,184,'+(iga*.55)+')');
  g.addColorStop(.5,'rgba(0,206,184,'+iga+')');
  g.addColorStop(1,'transparent');
  ctx.beginPath();ctx.arc(CX,CY,IR+5,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  // specular highlight
  ctx.beginPath();ctx.ellipse(CX+12,CY-14,11,7,-Math.PI/6,0,Math.PI*2);
  g=ctx.createRadialGradient(CX+12,CY-14,0,CX+12,CY-14,11);
  g.addColorStop(0,'rgba(228,244,255,.93)');g.addColorStop(.6,'rgba(195,220,248,.52)');g.addColorStop(1,'transparent');
  ctx.fillStyle=g;ctx.fill();
  // secondary reflex
  ctx.beginPath();ctx.ellipse(CX-17,CY+10,3.5,2.2,Math.PI/4,0,Math.PI*2);
  ctx.fillStyle='rgba(0,206,184,.28)';ctx.fill();
  // outer indicator dots
  segs.forEach(function(s,i){
    var m=s.mastery||.5,ma=i*SA-Math.PI/2+ro+SA/2;
    var dr=OR+12,dx=CX+dr*Math.cos(ma),dy=CY+dr*Math.sin(ma);
    ctx.beginPath();ctx.arc(dx,dy,2+m*2.5,0,Math.PI*2);
    ctx.fillStyle=mc(m,.62+m*.28);ctx.fill();
    if(m>.6){
      ctx.beginPath();ctx.arc(dx,dy,5+m*2,0,Math.PI*2);
      ctx.fillStyle=mc(m,.12);ctx.fill();
    }
  });
  // hover % label
  if(hi>=0){
    var s=segs[hi],m=s.mastery||.5;
    var ma=hi*SA-Math.PI/2+ro+SA/2,lr=(IR+OR)/2;
    ctx.save();
    ctx.font='bold 10px "Courier New"';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillStyle=mg(m);ctx.shadowColor=mg(m);ctx.shadowBlur=10;
    ctx.fillText(Math.round(m*100)+'%',CX+lr*Math.cos(ma),CY+lr*Math.sin(ma));
    ctx.restore();
  }
}

canvas.addEventListener('mousemove',function(e){
  var r=canvas.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
  var dx=mx-CX,dy=my-CY,d=Math.sqrt(dx*dx+dy*dy);
  var ro=t*.00025;
  var ang=(Math.atan2(dy,dx)+Math.PI/2-ro+Math.PI*100)%(Math.PI*2);
  if(d>=IR&&d<=OR){
    hi=Math.floor(ang/SA)%N;
    var s=segs[hi],m=s.mastery||.5;
    tip.textContent=s.name.toUpperCase()+' · '+Math.round(m*100)+'%';
    tip.style.opacity='1';
    tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY-30)+'px';
  }else{hi=-1;tip.style.opacity='0';}
});
canvas.addEventListener('mouseleave',function(){hi=-1;tip.style.opacity='0';});

function loop(){t++;draw(t);requestAnimationFrame(loop);}
loop();
</script>
</body>
</html>"""


def _eye_html(topics_data: list) -> str:
    return _EYE_TEMPLATE.replace("__TOPICS__", json.dumps(topics_data))


def render() -> None:
    name = st.session_state.student_name
    st.markdown(ph("Dashboard", f"Welcome back, {name}."), unsafe_allow_html=True)

    with st.expander("System Status", expanded=False):
        from tools.shared.health_monitor import (
            check_anthropic, check_google_sheets,
            check_google_drive, check_tmp_dir,
        )
        checks = [check_anthropic(), check_google_sheets(), check_google_drive(), check_tmp_dir()]
        _status_icons = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴", "INFO": "🔵"}
        hcols = st.columns(len(checks))
        for col, (status, sname, detail) in zip(hcols, checks):
            col.metric(sname, f"{_status_icons.get(status, '⚪')} {status}", help=detail)

    get_rows, _, __ = _gsheets()
    sid = st.session_state.student_id

    try:
        sessions = get_rows("snec_sessions",      {"student_id": sid})
        cards    = get_rows("snec_flashcards",    {"student_id": sid})
        cases    = get_rows("snec_case_results",  {"student_id": sid})
        images   = get_rows("snec_image_results", {"student_id": sid})

        today     = date.today().isoformat()
        due_cards = [c for c in cards if not c.get("next_due_date") or c["next_due_date"] <= today]
        due_txt   = f"{len(due_cards)} due today" if due_cards else "all caught up"

        # Build topic mastery data for eye model
        topics_for_eye = []
        if cards:
            topic_ef: dict = defaultdict(list)
            for c in cards:
                try:
                    ef = float(c.get("easiness_factor", 2.5))
                except (ValueError, TypeError):
                    ef = 2.5
                topic_ef[c.get("topic_tag", "unknown")].append(ef)

            topic_avg = {t: sum(v) / len(v) for t, v in topic_ef.items()}
            for topic_name, avg_ef in topic_avg.items():
                mastery = min(1.0, max(0.0, (avg_ef - 1.3) / (3.0 - 1.3)))
                topics_for_eye.append({"name": topic_name.capitalize(), "mastery": round(mastery, 2)})

        # Eye model — centered in a narrow column
        _, eye_col, _ = st.columns([1, 2, 1])
        with eye_col:
            components.html(_eye_html(topics_for_eye), height=300, scrolling=False)

        st.markdown(section_label("Activity Overview"), unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(stat_card("Chatbot Sessions", str(len(sessions)),
                                  "total Q&A sessions", "c-teal"), unsafe_allow_html=True)
        with s2:
            st.markdown(stat_card("Flash-cards", str(len(cards)),
                                  due_txt, "c-gold"), unsafe_allow_html=True)
        with s3:
            st.markdown(stat_card("Cases Attempted", str(len(cases)),
                                  "clinical simulations", "c-ok"), unsafe_allow_html=True)
        with s4:
            st.markdown(stat_card("Image Quizzes", str(len(images)),
                                  "retinal images reviewed", "c-blue"), unsafe_allow_html=True)

        if due_cards:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            c_info, c_btn = st.columns([5, 1])
            with c_info:
                st.info(f"📚 {len(due_cards)} flash-card(s) are due for review today.")
            with c_btn:
                if st.button("Review now →", type="primary", use_container_width=True):
                    st.switch_page("pages/flashcards.py")

        if cards:
            sorted_topics = sorted(topic_avg.items(), key=lambda x: x[1])
            st.markdown(section_label("Flash-card Mastery by Topic"), unsafe_allow_html=True)
            t_left, t_right = st.columns(2)
            half = (len(sorted_topics) + 1) // 2
            for i, (t, ef) in enumerate(sorted_topics):
                col = t_left if i < half else t_right
                with col:
                    st.markdown(topic_bar(t, ef), unsafe_allow_html=True)

        if not sessions and not cards and not cases:
            st.markdown(section_label("Getting Started"), unsafe_allow_html=True)
            st.markdown(start_item(1, "Ask your first question",
                "Open Chatbot Tutor and ask anything about ophthalmology."), unsafe_allow_html=True)
            st.markdown(start_item(2, "Review your flash-cards",
                "Cards are auto-generated from every session you complete."), unsafe_allow_html=True)
            st.markdown(start_item(3, "Simulate a clinical case",
                "Interview an AI patient, request investigations, make your diagnosis."),
                unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not load study data: {e}")


render()
