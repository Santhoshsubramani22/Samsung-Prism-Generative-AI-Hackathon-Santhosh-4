async function load(){
  const res=await fetch("/api/state");
  const state=await res.json();
  const events=state.telemetry||[];
  const total=events.length;
  document.getElementById("cards").innerHTML=[
    ["Session",state.session_id],
    ["Answer Versions",state.answer_version],
    ["Citations",state.citations.length],
    ["Evidence Chunks",state.retrieved_evidence.length],
    ["Telemetry Events",total],
    ["Intents",state.detected_intents.length]
  ].map(x=>`<div class="card">${x[0]}<strong>${x[1]}</strong></div>`).join("");

  document.getElementById("events").innerHTML=events.slice().reverse().map(e =>
    `<div class="event"><b>${e.timestamp}</b><br>${e.event} — v${e.version}</div>`
  ).join("") || "<div class='event'>No session events yet. Open Chat first.</div>";
}
load();
setInterval(load,3000);
