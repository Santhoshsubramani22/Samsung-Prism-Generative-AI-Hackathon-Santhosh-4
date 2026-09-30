const $ = id => document.getElementById(id);

function escapeHtml(value){
  return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
}

function timeline(text){
  const d=document.createElement("div");
  d.textContent=new Date().toLocaleTimeString()+"  "+text;
  $("timeline").prepend(d);
}

async function sendQuery(text=null){
  const query=text ?? $("query").value.trim();
  if(!query) return;
  timeline("Transcript received: "+query);
  $("controller").textContent="PROCESSING";
  $("answer").textContent="";
  try{
    const res=await fetch("/api/stream",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({query})
    });
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    await consumeSSE(res);
  }catch(e){
    $("answer").textContent="Error: "+e.message;
    timeline("Stream error: "+e.message);
  }
}

async function consumeSSE(response){
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let accumulated = "";

  while(true){
    const {value, done} = await reader.read();
    if(done) break;
    buffer += decoder.decode(value, {stream:true});
    const messages = buffer.split("\n\n");
    buffer = messages.pop();

    for(const message of messages){
      const line = message.split("\n").find(x => x.startsWith("data: "));
      if(!line) continue;
      const raw = line.slice(6);
      if(raw === "[DONE]"){
        timeline("Stream completed");
        continue;
      }
      try{
        const event = JSON.parse(raw);
        handleStreamEvent(event, value => { accumulated = value; });
      }catch(err){
        console.warn("Invalid SSE event", raw, err);
      }
    }
  }
}

function handleStreamEvent(event, setAccumulated){
  if(event.controller){
    $("controller").textContent=event.controller;
  }

  if(event.type === "controller"){
    $("controller").textContent=event.value;
    timeline("Controller → "+event.value);
    return;
  }

  if(event.type === "retrieval"){
    timeline(`Retrieval → ${event.evidence_ids?.length || 0} evidence chunks`);
    if(event.refinement) timeline("Late constraint → targeted retrieval using original intent + new constraint");
    renderRetrieval(event.metrics || {});
    renderIntents(event.intents || []);
    return;
  }

  if(event.type === "answer_delta"){
    $("answer").textContent += event.text || "";
    return;
  }

  if(event.type === "answer_correction"){
    $("answer").textContent = event.text || "";
    timeline("Grounding verifier corrected the streamed answer");
    return;
  }

  if(event.type === "final"){
    if(event.answer !== undefined) $("answer").textContent=event.answer;
    render(event);
    if(event.grounding) timeline(`Grounding → ${event.grounding.grounded ? "verified" : "not verified"}`);
    if(event.answer_version) timeline("Answer v"+event.answer_version);
    if(event.latency_ms) timeline("End-to-end latency: "+event.latency_ms+" ms");
  }
}

function renderRetrieval(r){
  $("retrieval").innerHTML=Object.entries(r).map(([k,v]) =>
    `<div class="stat"><b>${escapeHtml(k)}</b><br>${escapeHtml(String(v))}</div>`
  ).join("");
}

function renderIntents(intents){
  $("intents").innerHTML=intents.map(i =>
    `<div class="intent"><b>${escapeHtml(i.id)}</b> — ${escapeHtml(i.intent)}<br>`+
    `${escapeHtml(i.query)}<br><small>Retrieval: ${escapeHtml(i.retrieval_query || i.query)}</small></div>`
  ).join("");
}

function render(data){
  $("controller").textContent=data.controller || $("controller").textContent || "WAIT";
  renderIntents(data.intents||[]);
  renderRetrieval(data.retrieval||{});
  $("answer").textContent=data.answer || "No answer.";
  $("citations").innerHTML=(data.citations||[]).map(c =>
    `<div class="citation">[${escapeHtml(c)}]</div>`
  ).join("");

  const evidence = data.evidence || [];
  $("evidence").innerHTML = evidence.length ? evidence.map(e => {
    const c = e.chunk || {};
    return `<details class="evidence-item"><summary>${escapeHtml(c.chunk_id || "Evidence")} — page ${escapeHtml(String(c.page || ""))}</summary><p>${escapeHtml(c.chunk_text || "")}</p></details>`;
  }).join("") : "<div>No evidence exposed for this response.</div>";

  if(data.refinement) timeline("State-preserving refinement completed");
  if(data.retrieval?.executed===false) timeline("Retrieval skipped — existing state reused");
}

async function simulate(){
  const queries=[
    "What is the reimbursement policy?",
    "The trip was international."
  ];
  for(const q of queries){
    $("query").value=q;
    await sendQuery(q);
    await new Promise(r=>setTimeout(r,700));
  }
}
