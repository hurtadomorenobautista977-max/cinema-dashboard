(function(){
"use strict";
const API_URL="https://ccjykdpjprjaocglypij.supabase.co";
const API_KEY="sb_publishable_zie2dN-eYkhdACw1-7mHTQ_xR0tHw-u";
const BASE=window.CINEMA_MODEL;
let db=null,actor=null,role=null,model=deep(BASE),cinemas=[],records=[],currentId=null,answers={},context={metro:"unknown",amenities:{}};
let modelVersion=1,dirty=false,busy=false,tab="evaluate",axis="access",priorRecord=null;
const E=id=>document.getElementById(id);
function deep(x){return JSON.parse(JSON.stringify(x));}
function h(x){return String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function fmt(x){return Number(x).toLocaleString("fa-IR",{minimumFractionDigits:2,maximumFractionDigits:2});}
function count(x){return Number(x).toLocaleString("fa-IR");}
function number(x){return Math.max(0,Math.min(5,Number(x)||0));}
function hasScore(a){return a&&a.score!==null&&a.score!==undefined&&a.score!==""&&Number.isFinite(Number(a.score));}
function recordFor(id,version){return records.find(x=>Number(x.cinema_id)===Number(id)&&Number(x.model_version)===Number(version));}
function message(str,type="info"){const x=E("toast");x.textContent=str;x.className="toast show "+type;clearTimeout(message.timeout);message.timeout=setTimeout(()=>x.classList.remove("show"),5000);}
function changed(v=true){dirty=v;E("saveMarker").textContent=v?"تغییرات ذخیره‌نشده":"ذخیره‌شده";E("saveMarker").className=v?"marker warn":"marker";}
function findQuestion(id){for(const s of model.sections)for(const g of s.groups)for(const q of g.questions)if(q.id===id)return {q,g,s};return null;}
function activeRule(q,g,s){
 if(g.mode==="reference"||q.tag==="reference")return {yes:false,why:"ارجاع بدون امتیاز؛ قبلاً در محور ایمنی محاسبه شده است."};
 const own=answers["parking_info_t2_1"]||answers["parking_own"];
 if(q.tag==="parkingAlternative"&&hasScore(own)&&!own.na&&Number(own.score)>=Number(model.policy.parkingThreshold))return {yes:false,why:"پارکینگ اختصاصی یا مشترک کفایت دارد؛ مسیر جایگزین نمره را کاهش نمی‌دهد."};
 if((q.tag==="metro"||q.id==="access_info_metro")&&context.metro==="no")return {yes:false,why:"نبود مترو در این شهر، نامرتبط است؛ به‌جای صفر از محاسبه کنار گذاشته شده است."};
 if(s.mode==="bonus"&&context.amenities[g.id]!=="yes")return {yes:false,why:context.amenities[g.id]==="no"?"این امکان وجود ندارد؛ امتیاز پایه کاهش نمی‌یابد.":"برای دریافت امتیاز تشویقی، وجود این امکان را تأیید کنید."};
 return {yes:true,why:""};
}
function mean(items){let w=0,n=0;for(const [score,weight] of items){if(score!==null&&Number.isFinite(score)&&Number(weight)>0){w+=Number(weight);n+=Number(score)*Number(weight);}}return w?n/w:null;}
function calculate(){
 const categories=[],ignored=[],risk=[],missing=[],byItem=[];
 let required=0,completed=0,baseWeighted=0,baseWeight=0;
 for(const s of model.sections){
  const groupResults=[];
  for(const g of s.groups){
   const rows=[],qResults=[];
   for(const q of g.questions){
    const a=answers[q.id]||{},rule=activeRule(q,g,s);
    const manual=!!a.na;
    const excluded=!rule.yes||manual;
    const why=!rule.yes?rule.why:manual?(a.note?"توضیح کارشناس: "+a.note:"نامرتبط بدون دلیل معتبر"):"";
    const score=!excluded&&hasScore(a)?number(a.score):null;
    if(excluded)ignored.push({id:q.id,name:q.name,group:g.name,why});
    if(!excluded&&s.mode!=="bonus"&&q.required!==false){
     required++;
     if(score!==null)completed++;
     else missing.push({id:q.id,name:q.name,group:g.name});
    }
    if(score!==null){
     rows.push([score,Number(q.weight)||1]);
     if(q.tag==="critical"&&score<=Number(model.policy.criticalFloor))risk.push({id:q.id,name:q.name,group:g.name,score});
    }
    const entry={id:q.id,name:q.name,score,excluded,why,critical:q.tag==="critical"};
    qResults.push(entry);byItem.push(entry);
   }
   let score=mean(rows);
   if(g.mode==="parking"){
    const primary=qResults.find(q=>q.id==="parking_info_t2_1"||q.id==="parking_own");
    const alternative=qResults.filter(q=>q.id!==primary?.id&&q.score!==null).map(q=>[q.score,1]);
    const alternativesScore=mean(alternative);
    const own=primary?.score??null;
    score=own===null?alternativesScore:alternativesScore===null?own:Math.max(own,alternativesScore);
   }
   if(s.mode==="bonus"&&qResults.some(q=>q.id==="amenities_3_3"&&q.score!==null&&q.score<=Number(model.policy.criticalFloor)))score=0;
   groupResults.push({id:g.id,name:g.name,score,items:qResults,mode:g.mode});
  }
  const score=mean(groupResults.filter(g=>g.mode!=="reference").map(g=>[g.score,1]));
  categories.push({id:s.id,name:s.name,weight:Number(s.weight)||0,score,bonus:s.mode==="bonus",groups:groupResults});
  if(s.mode!=="bonus"&&score!==null){baseWeighted+=score*Number(s.weight);baseWeight+=Number(s.weight);}
 }
 const raw=baseWeight>0?baseWeighted/baseWeight:null;
 const bonuses=categories.filter(s=>s.bonus).flatMap(s=>s.groups).filter(g=>g.mode!=="reference");
 const bonus=bonuses.length?Number(model.policy.bonusCap)*bonuses.reduce((a,g)=>a+(g.score===null?0:g.score/5),0)/bonuses.length:0;
 const before=raw===null?null:Math.min(5,raw+bonus);
 const score=before===null?null:risk.length?Math.min(before,Number(model.policy.criticalCap)):before;
 const coverage=required?completed/required:0;
 return {categories,ignored,risk,missing,required,completed,coverage,raw,bonus,before,score,ready:coverage>=Number(model.policy.minCoverage)&&required>0,byItem};
}
function ratingOptions(value){
 let str='<option value="">ارزیابی نشده</option>';
 for(let i=0;i<=20;i++){const v=i/4;str+='<option value="'+v+'" '+(value!==null&&value!==undefined&&value!==""&&Number(value)===v?"selected":"")+'>'+String(v).replace(".","٫")+' از ۵</option>';}
 return str;
}
function optionsChecklist(rubric){
 if(!rubric)return "";
 if(typeof rubric==="string"){
  const clean=String(rubric).replace(/\s*(?=امتیاز\s*[۰۱۲۳۴۵0-5])/g,"<span class='rb-break'></span>");
  return '<div class="rubric-list">'+h(clean).replace(/&lt;span class=&#39;rb-break&#39;&gt;&lt;\/span&gt;/g,"<div style='height:4px'></div>")+'</div>';
 }
 if(typeof rubric==="object")return '<div class="rubric-list">'+[5,4,3,2,1,0].map(i=>'<div><b>'+count(i)+': </b>'+h(rubric[i]??rubric[String(i)]??"")+'</div>').join("")+'</div>';
 return "";
}
function renderSelector(){
 E("cinemaSelect").innerHTML='<option value="">یک سینما انتخاب کنید</option>'+cinemas.map(c=>'<option value="'+c.id+'">'+h(c.name)+" — "+h(c.city||c.province||"")+'</option>').join("");
 if(currentId)E("cinemaSelect").value=String(currentId);
 E("modelVersion").textContent="نسخه "+count(modelVersion)+" / سند کامل";
 E("policyOwnerBtn").classList.toggle("hidden",role!=="owner");
}
function renderNav(){
 const a=calculate();
 E("sectionsNav").innerHTML=model.sections.map(s=>{
  const cat=a.categories.find(c=>c.id===s.id);
  const items=cat.groups.flatMap(g=>g.items),need=items.filter(x=>!x.excluded&&s.mode!=="bonus"),done=need.filter(x=>x.score!==null);
  return '<button class="section-link '+(axis===s.id?"active":"")+'" data-section="'+h(s.id)+'"><span class="section-link-title">'+h(s.name)+'</span><span class="section-link-foot"><span>'+(s.mode==="bonus"?"امتیاز تشویقی":count(done.length)+" / "+count(need.length)+" پاسخ")+'</span><strong>'+(cat.score===null?"—":fmt(cat.score))+'</strong></span><span class="section-progress"><span style="width:'+(need.length?done.length/need.length*100:0)+'%"></span></span></button>';
 }).join("");
}
function renderGroups(){
 if(tab!=="evaluate")return;
 const section=model.sections.find(s=>s.id===axis)||model.sections[0];const a=calculate(),cat=a.categories.find(c=>c.id===section.id);
 E("pageMainTitle").textContent=section.name;
 E("pageMainNote").textContent=section.mode==="bonus"?"این امکانات جداگانه و تشویقی‌اند. نبود آن‌ها از امتیاز کیفیت پایه کم نمی‌کند.":"سؤال‌های هر زیرشاخص از سند مبنا آمده‌اند؛ معیار نامرتبط را با دلیل کنار بگذارید و صفر را برای ضعف واقعی ثبت کنید.";
 E("evaluatePane").classList.remove("hidden");E("reportPane").classList.add("hidden");
 E("groupsWrap").innerHTML=section.groups.map((g,index)=>{
  const res=cat.groups.find(x=>x.id===g.id);
  const bonus=section.mode==="bonus";
  const available=String(context.amenities[g.id]||"unknown");
  const amenityUI=bonus?'<div class="availability"><label>وضعیت وجود این امکان</label><select class="amenity-select" data-group="'+h(g.id)+'"><option value="unknown" '+(available==="unknown"?"selected":"")+'>هنوز بررسی نشده</option><option value="yes" '+(available==="yes"?"selected":"")+'>موجود است</option><option value="no" '+(available==="no"?"selected":"")+'>وجود ندارد (بدون جریمه)</option></select></div>':"";
  const parkUI=g.mode==="parking"?'<p class="rule-hint"><b>اولویت و جایگزینی:</b> اگر پارکینگ خود سینما '+h(model.policy.parkingThreshold)+' یا بالاتر بگیرد، وضعیت پارکینگ اطراف در امتیاز این زیرشاخص اثری ندارد. در غیر این صورت، بهترین امتیاز بین پارکینگ سینما و میانگین جایگزین‌های اطراف ملاک است. داده‌های جایگزین قبلی پاک نمی‌شوند.</p>':"";
  const notes=g.sourceInfo?.length?'<details class="rubric" style="margin-bottom:14px"><summary>جزئیات پشتیبان سند و موارد هم‌پوشان ('+count(g.sourceInfo.length)+')</summary><div class="rubric-list">'+g.sourceInfo.map(x=>'<div style="padding:8px 0;border-top:1px solid #edf1f0"><b>'+h(x.title)+'</b><div>'+h(x.method||"")+'</div>'+(x.id==="access_info_metro"&&context.metro==="no"?'<span style="color:#19836f">نامرتبط به دلیل نبود مترو</span>':"")+'</div>').join("")+'</div></details>':"";
  const qHtml=g.mode==="reference"?'<p class="reference-note">برای جلوگیری از دوباره‌شماری، موارد این زیرشاخص فقط در محور ایمنی امتیاز می‌گیرند. جزئیات ردیف‌ها در سند اصلی باقی مانده‌اند.</p>':
   g.questions.map((q,i)=>{
    const answer=answers[q.id]||{},rule=activeRule(q,g,section);
    const exclude=!rule.yes||!!answer.na;
    const crit=q.tag==="critical";
    const qvalue=answer.na?null:answer.score;
    const desc=q.method?'<div class="detail-row"><b>نحوه بررسی: </b>'+h(q.method)+'</div>':"";
    const rubric=q.rubric?'<details class="rubric"><summary>معیار امتیازدهی ۰ تا ۵ بر اساس سند</summary>'+optionsChecklist(q.rubric)+'</details>':"";
    return '<div class="question '+(exclude?"question-off":"")+'" data-qid="'+h(q.id)+'"><div class="question-top"><div class="question-caption"><span class="question-count">'+count(i+1)+'</span><span>'+h(q.name)+'</span>'+(crit?'<span class="risk-tag">حساس</span>':"")+'</div><div class="question-actions"><label>امتیاز <select class="score-select" data-question="'+h(q.id)+'" '+(exclude?"disabled":"")+'>'+ratingOptions(qvalue)+'</select></label></div></div>'+(rule.yes?'<div class="q-footer"><label class="na-control"><input class="na-toggle" data-question="'+h(q.id)+'" type="checkbox" '+(answer.na?"checked":"")+' '+(q.tag==="primary"?"disabled":"")+'>نامرتبط (N/A)</label><input class="na-note '+(answer.na?"":"hidden")+'" data-question="'+h(q.id)+'" type="text" placeholder="دلیل دقیق نامرتبط بودن..." value="'+h(answer.note||"")+'"></div>':'<div class="excluded-info">مستثنا: '+h(rule.why)+'</div>')+desc+rubric+'</div>';
   }).join("");
  return '<article class="group-card" id="group-'+h(g.id)+'"><div class="group-head"><div><span class="eyebrow">زیرشاخص '+count(index+1)+'</span><h3>'+h(g.name)+'</h3></div><div class="group-score">'+(res.score===null?"—":fmt(res.score))+' <small>/ ۵</small></div></div>'+amenityUI+parkUI+qHtml+notes+'</article>';
 }).join("");
}
function renderSummary(){
 const a=calculate();const cv=Math.round(a.coverage*100);
 E("scoreNumber").textContent=a.score===null?"—":fmt(a.score);
 E("scoreCaption").textContent=a.ready?(a.risk.length?"ارزیابی کامل با هشدار ایمنی":"پاسخ‌ها کامل؛ قابل ارائه"):"امتیاز موقت؛ هنوز همه معیارها بررسی نشده‌اند";
 E("scoreStatus").textContent=a.ready?(a.risk.length?"خطر جدی ثبت شده":"قابل ارائه"):"در حال تکمیل";
 E("scoreStatus").className="status-pill "+(a.ready&&a.risk.length?"bad":a.ready?"good":"muted");
 E("scoreRing").style.setProperty("--p",Math.max(0,Math.round((a.score||0)*20))+"%");
 E("coverageNumber").textContent=count(cv)+"٪";
 E("coverageBar").style.width=cv+"%";
 E("coveredCount").textContent=count(a.completed)+" از "+count(a.required)+" معیار اصلی";
 E("rawScore").textContent=a.raw===null?"—":fmt(a.raw);
 E("bonusScore").textContent="+"+fmt(a.bonus);
 E("capAlert").classList.toggle("hidden",!a.risk.length);
 E("capAlertText").textContent=a.risk.length?count(a.risk.length)+" مورد حساس نمره "+model.policy.criticalFloor+" یا کمتر دارد؛ سقف نمایش امتیاز "+model.policy.criticalCap+" اعمال می‌شود.":"";
 E("saveDraft").disabled=busy||!currentId;
 E("saveComplete").disabled=busy||!currentId||!a.ready;
 E("scoreCategories").innerHTML=a.categories.filter(x=>!x.bonus).map(x=>'<div class="compact-row"><span>'+h(x.name)+'</span><b>'+(x.score===null?"—":fmt(x.score))+'</b><span class="mini-bar"><i style="width:'+((x.score||0)*20)+'%"></i></span></div>').join("");
}
function renderAudit(){
 const a=calculate();
 E("auditCounts").innerHTML='<span>'+count(a.ignored.length)+' استثنا</span><span>'+count(a.missing.length)+' ناقص</span><span>'+count(a.risk.length)+' هشدار ایمنی</span>';
 E("auditList").innerHTML=[
  ...a.risk.map(x=>'<div class="audit-line audit-danger"><b>خطر حساس</b><span>'+h(x.name)+'</span><strong>'+fmt(x.score)+'</strong></div>'),
  ...a.ignored.slice(0,70).map(x=>'<div class="audit-line"><b>استثنا</b><span>'+h(x.name)+": "+h(x.why)+'</span></div>'),
  ...a.missing.slice(0,35).map(x=>'<div class="audit-line audit-pending"><b>ناقص</b><span>'+h(x.name)+'</span></div>')
 ].join("")||'<p class="quiet">استثنا یا هشدار فعالی وجود ندارد.</p>';
}
function report(){
 const a=calculate(),c=cinemas.find(c=>c.id===currentId);
 tab="report";E("evaluateLink").classList.remove("active");E("reportLink").classList.add("active");
 E("evaluatePane").classList.add("hidden");E("reportPane").classList.remove("hidden");
 E("pageMainTitle").textContent="گزارش ارزیابی "+(c?.name||"");
 E("pageMainNote").textContent="امتیاز پایه، پاداش، شرط ایمنی و فهرست کامل استثناها، به‌صورت قابل ردیابی.";
 E("reportCards").innerHTML=[
 ["امتیاز پایه",a.raw===null?"—":fmt(a.raw)],
 ["امتیاز تشویقی","+"+fmt(a.bonus)],
 ["امتیاز نهایی مشروط",a.score===null?"—":fmt(a.score)],
 ["پوشش معیارها",count(Math.round(a.coverage*100))+"٪"]
 ].map(([t,v])=>'<div class="report-stat"><span>'+h(t)+'</span><strong>'+h(v)+'</strong></div>').join("");
 E("reportCategories").innerHTML=a.categories.map(x=>'<div class="report-category"><div><b>'+h(x.name)+'</b><small>'+(x.bonus?"تشویقی (بدون کسر از پایه)":"وزن پیشنهادی "+count(Math.round(x.weight*100))+"٪")+'</small></div><strong>'+(x.score===null?"—":fmt(x.score))+'</strong><div class="report-bar"><i style="width:'+((x.score||0)*20)+'%"></i></div>'+x.groups.map(g=>'<div class="report-sub"><span>'+h(g.name)+'</span><b>'+(g.score===null?"—":fmt(g.score))+'</b></div>').join("")+'</div>').join("");
 const notes=(model.reviewNotes||[]).map(x=>'<p class="muted-text"><b>'+h(x.title)+":</b> "+h(x.detail)+'</p>').join("");
 E("reportAlerts").innerHTML='<h3>قواعد، هشدارها و ملاحظات سند</h3>'+a.risk.map(x=>'<p class="danger-text"><b>هشدار ایمنی: </b>'+h(x.name)+" — "+fmt(x.score)+'</p>').join("")+a.ignored.map(x=>'<p class="info-text"><b>نامرتبط/مستثنا: </b>'+h(x.name)+" — "+h(x.why)+'</p>').join("")+(a.missing.length?'<p class="muted-text">'+count(a.missing.length)+' معیار اصلی هنوز تکمیل نشده و نتیجه موقت است.</p>':"")+notes;
}
function listCinemas(){
 E("cinemaList").innerHTML=cinemas.map(c=>{
 const r=recordFor(c.id,modelVersion),x=r?.computed_results||{};
 return '<button class="cinema-item '+(c.id===currentId?"current":"")+'" data-cinema="'+c.id+'"><span>'+h(c.name)+'</span><small>'+(r?(r.status==="completed"?"ثبت نهایی":"پیش‌نویس"):"بدون ارزیابی")+'</small><b>'+(typeof x.score==="number"?fmt(x.score):"—")+'</b></button>';
 }).join("");
}
function chooseCinema(id,force=false){
 const num=id?Number(id):null;
 if(dirty&&!force&&num!==currentId&&!confirm("تغییرات ذخیره نشده‌اند. سینما را بدون ذخیره تغییر می‌دهید؟")){E("cinemaSelect").value=String(currentId||"");return;}
 currentId=num;
 const r=recordFor(num,modelVersion);priorRecord=records.find(x=>x.cinema_id===num&&x.model_version<modelVersion);
 answers=deep(r?.responses||{});context=Object.assign({metro:"unknown",amenities:{}},deep(r?.profile_snapshot||{}));if(!context.amenities)context.amenities={};
 E("metroState").value=context.metro||"unknown";
 changed(false);tab="evaluate";axis="location";
 E("evaluateLink").classList.add("active");E("reportLink").classList.remove("active");
 E("oldVersionPrompt").classList.toggle("hidden",!priorRecord||!!r);
 const c=cinemas.find(x=>x.id===currentId);
 E("selectedCinema").textContent=c?.name||"سینمایی انتخاب نشده";
 E("cinemaMeta").textContent=c?[c.province,c.city,count(c.halls||0)+" سالن",count(c.operational_seats||0)+" صندلی عملیاتی"].filter(Boolean).join(" | "):"";
 renderNav();renderGroups();renderSummary();renderAudit();listCinemas();
}
async function fetchRecords(){
 const {data,error}=await db.from("cinema_scoring_assessments").select("id,cinema_id,model_id,model_version,responses,profile_snapshot,computed_results,status,updated_at").eq("model_id",BASE.id).order("model_version",{ascending:false});
 if(error)throw error;records=data||[];listCinemas();
}
async function loadAll(){
 E("pageLoading").classList.remove("hidden");
 try{
  // مدل جامع تنها پس از احراز هویت از داده‌های محافظت‌شده دریافت می‌شود؛ در صورت خطا ارزیابی ناقص فعال نمی‌شود.
  model=await window.loadFullCinemaModel(db);
  const [m,c,r]=await Promise.all([
   db.from("cinema_scoring_model_overrides").select("*").eq("model_id",BASE.id).maybeSingle(),
   db.from("cinemas").select("id,name,province,city,address,halls,total_seats,operational_seats,daily_shows").order("name"),
   db.from("cinema_scoring_assessments").select("id,cinema_id,model_id,model_version,responses,profile_snapshot,computed_results,status,updated_at").eq("model_id",BASE.id).order("model_version",{ascending:false})
  ]);
  if(m.error||c.error||r.error)throw new Error(m.error?.message||c.error?.message||r.error?.message);
  modelVersion=Number(m.data?.version)||1;
  if(m.data?.definition){const d=m.data.definition;if(d.policy)Object.assign(model.policy,d.policy);for(const s of model.sections)if(d.weights&&d.weights[s.id]!==undefined)s.weight=Number(d.weights[s.id]);}
  model.version=modelVersion;cinemas=c.data||[];records=r.data||[];
  if(!currentId&&cinemas.length)currentId=cinemas[0].id;
  renderSelector();chooseCinema(currentId,true);E("pageLoading").classList.add("hidden");
 }catch(e){console.error(e);message("خطا در بارگذاری مدل یا اطلاعات: "+e.message,"error");E("pageLoading").classList.add("hidden");}
}
function setBusy(value){busy=value;E("saveDraft").textContent=value?"در حال ذخیره...":"ذخیره پیش‌نویس";E("saveComplete").textContent=value?"در حال ذخیره...":"نهایی‌کردن ارزیابی";renderSummary();}
async function save(status){
 if(busy||!currentId)return;
 const invalid=Object.entries(answers).filter(([id,a])=>a.na&&(!a.note||a.note.trim().length<8)&&findQuestion(id)&&activeRule(findQuestion(id).q,findQuestion(id).g,findQuestion(id).s).yes);
 if(invalid.length){message("برای نامرتبط بودن هر معیار، دلیل حداقل ۸ کاراکتری وارد کنید.","error");return;}
 const a=calculate();
 if(status==="completed"&&!a.ready){message("ارزیابی همه معیارهای اصلی مرتبط باید تکمیل شود.","error");return;}
 if(status==="completed"&&a.risk.length&&!confirm("این ارزیابی دارای هشدار ایمنی است و با همین وضعیت ثبت خواهد شد. ادامه می‌دهید؟"))return;
 setBusy(true);
 try{
  const now=new Date().toISOString();
  const payload={cinema_id:currentId,model_id:BASE.id,model_version:modelVersion,model_snapshot:model,responses:answers,profile_snapshot:context,
   computed_results:{score:a.score,raw:a.raw,bonus:a.bonus,coverage:a.coverage,risk:a.risk,exclusions:a.ignored,categoryScores:a.categories.map(x=>({id:x.id,score:x.score}))},
   status,updated_by:actor?.id,updated_at:now,completed_at:status==="completed"?now:null};
  const {error}=await db.from("cinema_scoring_assessments").upsert(payload,{onConflict:"cinema_id,model_id,model_version"});
  if(error)throw error;
  changed(false);message(status==="completed"?"ارزیابی کامل در پایگاه نسخه آزمایشی ثبت شد.":"پیش‌نویس در پایگاه نسخه آزمایشی ذخیره شد.","success");
  await fetchRecords();
 }catch(e){console.error(e);message("ذخیره انجام نشد: "+e.message,"error");}finally{setBusy(false);}
}
function showOwner(){
 if(role!=="owner")return;
 const pairs=[
  ["parkingThreshold","حد نصاب اولویت پارکینگ اختصاصی",0,5,.25],
  ["criticalFloor","آستانه نقص حساس ایمنی",0,5,.25],
  ["criticalCap","سقف نمره نهایی با نقص ایمنی",0,5,.01],
  ["bonusCap","سقف تشویقی امکانات جانبی",0,1,.05],
  ["minCoverage","حداقل پوشش لازم برای نهایی‌سازی",.1,1,.05]
 ];
 E("editPolicies").innerHTML=pairs.map(([id,label,min,max,step])=>'<label>'+h(label)+'<input id="policy-'+id+'" type="number" min="'+min+'" max="'+max+'" step="'+step+'" value="'+h(model.policy[id])+'"></label>').join("");
 E("editWeights").innerHTML=model.sections.filter(s=>s.mode!=="bonus").map(s=>'<label>'+h(s.name)+'<input class="weight-edit" data-axis="'+h(s.id)+'" type="number" min="0" max="1" step=".01" value="'+h(s.weight)+'"></label>').join("");
 E("ownerDialog").showModal();
}
async function saveOwner(){
 if(role!=="owner")return;
 const policy=deep(model.policy),weights={};let ok=true,sum=0;
 for(const key of Object.keys(policy)){
  const el=E("policy-"+key);if(!el)continue;const v=Number(el.value);
  if(!Number.isFinite(v)||v<Number(el.min)||v>Number(el.max))ok=false;
  policy[key]=v;
 }
 document.querySelectorAll(".weight-edit").forEach(el=>{const v=Number(el.value);if(!Number.isFinite(v)||v<0||v>1)ok=false;weights[el.dataset.axis]=v;sum+=v;});
 if(!ok||Math.abs(sum-1)>.001){message("حدها نامعتبرند یا جمع وزن‌های پایه دقیقاً برابر ۱ نیست. جمع فعلی: "+sum.toFixed(3),"error");return;}
 if(!confirm("این تغییر نسخه جدید ارزیابی ایجاد می‌کند. ارزیابی‌های قبلی محفوظ می‌مانند. ادامه می‌دهید؟"))return;
 try{
  const {error}=await db.from("cinema_scoring_model_overrides").upsert({model_id:BASE.id,definition:{policy,weights},version:modelVersion+1,updated_at:new Date().toISOString(),updated_by:actor?.id},{onConflict:"model_id"});
  if(error)throw error;E("ownerDialog").close();changed(false);message("قواعد نسخه جدید ثبت شد.","success");await loadAll();
 }catch(e){message("ذخیره قواعد ناموفق بود: "+e.message,"error");}
}
function importPrior(){
 if(!priorRecord)return;
 if(!confirm("پاسخ‌های نسخه قبلی به پیش‌نویس منتقل می‌شوند؛ همه شرط‌های جدید نیاز به بازبینی دارند. ادامه می‌دهید؟"))return;
 answers=deep(priorRecord.responses||{});context=Object.assign({metro:"unknown",amenities:{}},deep(priorRecord.profile_snapshot||{}));
 E("metroState").value=context.metro;E("oldVersionPrompt").classList.add("hidden");changed();renderGroups();renderNav();renderSummary();renderAudit();message("پاسخ‌ها به پیش‌نویس منتقل شدند؛ هنوز در پایگاه ذخیره نشده‌اند.");
}
async function authorize(user){
 const {data,error}=await db.from("admin_users").select("user_id,role").eq("user_id",user.id).maybeSingle();
 if(error||!data){E("loginError").textContent="این حساب مجوز مدیریت سینماها را ندارد.";await db.auth.signOut();return;}
 actor=user;role=data.role;E("authOverlay").classList.add("hidden");E("accountName").textContent=user.email||"مدیر";await loadAll();
}
function lock(){actor=null;role=null;E("authOverlay").classList.remove("hidden");E("loginError").textContent="";}
async function login(event){
 event.preventDefault();const btn=E("loginBtn");btn.disabled=true;E("loginError").textContent="";
 try{
  const email=E("loginEmail").value.trim(),password=E("loginPassword").value;
  const {data,error}=await db.auth.signInWithPassword({email,password});
  if(error)throw error;if(data?.user)await authorize(data.user);
 }catch(e){E("loginError").textContent="خطای ورود: "+e.message;}finally{btn.disabled=false;}
}
function wire(){
 E("loginForm").addEventListener("submit",login);
 E("logoutBtn").addEventListener("click",async()=>{if(dirty&&!confirm("تغییرات ذخیره نشده‌اند. خارج شوید؟"))return;await db.auth.signOut();lock();});
 E("cinemaSelect").addEventListener("change",e=>chooseCinema(e.target.value));
 E("metroState").addEventListener("change",e=>{context.metro=e.target.value;changed();renderGroups();renderNav();renderSummary();renderAudit();});
 E("sectionsNav").addEventListener("click",e=>{const b=e.target.closest("[data-section]");if(!b)return;axis=b.dataset.section;tab="evaluate";E("evaluateLink").classList.add("active");E("reportLink").classList.remove("active");renderGroups();renderNav();});
 E("cinemaList").addEventListener("click",e=>{const b=e.target.closest("[data-cinema]");if(!b)return;chooseCinema(b.dataset.cinema);E("cinemaSelect").value=String(currentId||"");});
 E("groupsWrap").addEventListener("change",e=>{
  const t=e.target;
  if(t.classList.contains("amenity-select")){context.amenities[t.dataset.group]=t.value;changed();renderGroups();renderSummary();renderNav();renderAudit();return;}
  const id=t.dataset.question;if(!id)return;
  const a=answers[id]||{score:null,na:false,note:""};
  if(t.classList.contains("score-select"))a.score=t.value===""?null:Number(t.value);
  if(t.classList.contains("na-toggle")){a.na=t.checked;if(a.na)a.score=null;}
  answers[id]=a;changed();
  if(t.classList.contains("na-toggle")||t.dataset.question==="parking_info_t2_1"||t.dataset.question==="parking_own")renderGroups();
  renderSummary();renderNav();renderAudit();
 });
 E("groupsWrap").addEventListener("input",e=>{const t=e.target;if(t.classList.contains("na-note")){const id=t.dataset.question;answers[id]=Object.assign({score:null,na:false,note:""},answers[id]||{},{note:t.value});changed();}});
 E("evaluateLink").addEventListener("click",()=>{tab="evaluate";E("evaluateLink").classList.add("active");E("reportLink").classList.remove("active");renderGroups();});
 E("reportLink").addEventListener("click",report);
 E("saveDraft").addEventListener("click",()=>save("draft"));
 E("saveComplete").addEventListener("click",()=>save("completed"));
 E("auditToggle").addEventListener("click",()=>E("auditPanel").classList.toggle("hidden"));
 E("policyOwnerBtn").addEventListener("click",showOwner);
 E("ownerClose").addEventListener("click",()=>E("ownerDialog").close());
 E("ownerSave").addEventListener("click",saveOwner);
 E("importOld").addEventListener("click",importPrior);
 window.addEventListener("beforeunload",e=>{if(dirty){e.preventDefault();e.returnValue="";}});
}
async function init(){
 wire();
 if(!window.supabase?.createClient){E("loginError").textContent="کتابخانه Supabase بارگذاری نشد. صفحه را مجدداً باز کنید.";return;}
 db=window.supabase.createClient(API_URL,API_KEY);
 db.auth.onAuthStateChange(event=>{if(event==="SIGNED_OUT")lock();});
 const {data,error}=await db.auth.getSession();
 if(error){E("loginError").textContent=error.message;return;}
 if(data?.session?.user)await authorize(data.session.user);
}
document.addEventListener("DOMContentLoaded",init);
window.scoringPreviewDebug={calculate:()=>calculate(),currentModel:()=>deep(model)};
})();