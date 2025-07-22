/* 小工具：把 list[dict] 渲染为 <table> */
function renderTable(data){
  if(!Array.isArray(data)||data.length===0) return "<em>（空结果）</em>";
  const cols = Object.keys(data[0]);
  let html = "<table><thead><tr>";
  cols.forEach(c=>html += `<th>${c}</th>`);
  html += "</tr></thead><tbody>";
  data.forEach(row=>{
    html += "<tr>";
    cols.forEach(c=>html += `<td>${row[c]??""}</td>`);
    html += "</tr>";
  });
  html += "</tbody></table>";
  return html;
}

/* 主逻辑 */
async function submitQuery(){
  const btn     = document.getElementById("sendBtn");
  const query   = document.getElementById("nlInput").value.trim();
  const status  = document.getElementById("status");
  const sqlBox  = document.getElementById("sqlOutput");
  const dbBox   = document.getElementById("dbOutput");
  const panel   = document.getElementById("resultPanel");

  if(!query){alert("请输入问题");return}
  // Reset + loading UI
  btn.disabled = true; status.textContent="生成中…"; status.classList.add("loading");
  sqlBox.textContent = ""; dbBox.innerHTML=""; panel.classList.remove("hidden");

  try{
    const res = await fetch("http://localhost:5678/generate_sql",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({query})
    });
    const data = await res.json();
    if(res.ok){
      sqlBox.textContent = data.generated_sql || "(无 SQL)";
      dbBox.innerHTML    = renderTable(data.query_result);
      status.textContent = "✅ 完成";
    }else{
      sqlBox.textContent = "";
      dbBox.innerHTML    = `<span class="error">❌ ${data.error}</span>`;
      status.textContent = "❌ 失败";
    }
  }catch(err){
    sqlBox.textContent = "";
    dbBox.innerHTML    = `<span class="error">❌ 网络错误：${err}</span>`;
    status.textContent = "❌ 失败";
  }finally{
    btn.disabled=false; status.classList.remove("loading");
    setTimeout(()=>status.textContent="",2500);
  }
}
