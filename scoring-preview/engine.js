(function(root){
 'use strict';
 const valid=a=>a&&!a.na&&a.score!==''&&a.score!==null&&a.score!==undefined&&Number.isFinite(Number(a.score))&&Number(a.score)>=0&&Number(a.score)<=5;
 const mean=xs=>{const ys=xs.filter(x=>x[0]!==null&&Number.isFinite(x[0])&&x[1]>0);const w=ys.reduce((a,x)=>a+x[1],0);return w?ys.reduce((a,x)=>a+x[0]*x[1],0)/w:null;};
 function parking(p){
  if(!p||!p.verified||!Number.isFinite(Number(p.demand))||Number(p.demand)<=0)return null;
  const capacities=['own','public','street'].map(k=>p[k]);
  if(capacities.some(v=>v===''||v===null||v===undefined||!Number.isFinite(Number(v))||Number(v)<0))return null;
  return 5*Math.min(1,capacities.reduce((a,v)=>a+Number(v),0)/Number(p.demand));
 }
 const active=q=>q.type!=='info'&&q.type!=='reference'&&q.tag!=='reference';
 function conditionErrors(model){
  const rows=new Map(),groups=new Map(),errors=[],edges=new Map();
  for(const s of model.sections)for(const g of s.groups){groups.set(g.id,g);for(const q of g.questions)rows.set(q.id,q);}
  for(const q of rows.values())if(q.condition?.enabled){const c=q.condition;
   const source=c.sourceType==='row'?[rows.get(c.sourceId)]:c.sourceType==='parameter'?groups.get(c.sourceId)?.questions.filter(active):null;
   if(!active(q)||!source?.length||source.some(x=>!x||!active(x))||!['lt','lte','gt','gte','eq','neq'].includes(c.operator)||c.threshold===null||c.threshold===''||!Number.isFinite(Number(c.threshold))||Number(c.threshold)<0||Number(c.threshold)>5){errors.push('شرط نامعتبر برای ردیف «'+q.name+'»');continue;}
   edges.set(q.id,source.map(x=>x.id));
  }
  const done=new Set(),visiting=new Set();function visit(id){if(visiting.has(id)){errors.push('وابستگی حلقه‌ای در شرط ردیف‌ها');return;}if(done.has(id))return;visiting.add(id);for(const x of edges.get(id)||[])visit(x);visiting.delete(id);done.add(id);}
  for(const id of edges.keys())visit(id);return [...new Set(errors)];
 }
 function calculate(model,answers={},context={amenities:{}}){
  const categories=[],ignored=[],risk=[],missing=[],byItem=[],errors=conditionErrors(model);let required=0,completed=0;
  const gs=new Map(),qs=new Map(),cache=new Map(),visiting=new Set(),policy=model.policy||{};
  for(const s of model.sections)for(const g of s.groups){gs.set(g.id,{g,s});for(const q of g.questions)qs.set(q.id,{q,g,s});}
  const excludedGroup=g=>!!context.excludedParams?.includes(g.id);
  const capValue=Number(policy.criticalCap??3),caps=policy.capEnabled??policy.criticalCapEnabled;
  const cap=(score,alerts,scope)=>score===null?null:caps&&alerts.some(x=>x.effect==='cap_score'&&x.scope===scope)?Math.min(score,capValue):score;
  function resolve(q){if(cache.has(q.id))return cache.get(q.id);if(visiting.has(q.id))return {score:null,excluded:false,pending:true,why:'وابستگی حلقه‌ای'};visiting.add(q.id);
   const {g,s}=qs.get(q.id),a=answers[q.id]||{};let why='',pending=false;
   if(!active(q))why=q.type==='info'?'اطلاعات پشتیبان؛ بدون امتیاز مستقل':'ارجاع به محل اصلی؛ بدون اثر دوباره در امتیاز';
   else if(excludedGroup(g))why='خروج دستی پارامتر: '+(context.exclusionReasons?.[g.id]||'بدون دلیل');
   else if(g.mode==='reference')why='ارجاع به محل اصلی؛ بدون اثر دوباره در امتیاز';
   else if(s.mode==='bonus'&&context.amenities?.[g.id]!=='yes')why='امکان جانبی موجود یا تأیید نشده';
   else if(q.condition?.enabled){const c=q.condition,source=c.sourceType==='row'?qs.get(c.sourceId):null;let value=null;
    if(source){const x=resolve(source.q);value=x.pending?null:x.score;}
    else if(c.sourceType==='parameter'&&gs.has(c.sourceId)){const sourceGroup=gs.get(c.sourceId).g,rs=sourceGroup.questions.filter(active).map(resolve),usable=rs.filter(x=>!x.excluded);if(!excludedGroup(sourceGroup)&&usable.length&&usable.every(x=>!x.pending&&x.score!==null))value=mean(usable.map(x=>[x.score,x.weight]));}
    if(value===null){pending=true;}else{const t=Number(c.threshold),ok={lt:value<t,lte:value<=t,gt:value>t,gte:value>=t,eq:Math.abs(value-t)<1e-9,neq:Math.abs(value-t)>=1e-9}[c.operator];if(!ok)why='شرط فعال‌سازی برقرار نیست';}
   }
   if(!why&&!pending&&a.na&&a.note?.trim().length>=8)why='نامرتبط: '+a.note;
   const excluded=!!why,auto=q.id==='parking_outcome'?parking(context.parking):null;
   const score=excluded||pending?null:auto!==null?auto:valid(a)?Number(a.score):null;
   const entry={id:q.id,name:q.name,score,weight:Number(q.weight??1),excluded,pending,why:pending?'در انتظار تکمیل امتیاز مرجع شرط':why,critical:q.alert?.enabled??q.tag==='critical',automatic:auto!==null};
   visiting.delete(q.id);cache.set(q.id,entry);return entry;
  }
  for(const s of model.sections){const groups=[];
   for(const g of s.groups){const items=g.questions.map(resolve),alerts=[];
    for(const entry of items){const q=qs.get(entry.id).q,a=answers[q.id]||{};byItem.push(entry);
     if(entry.excluded)ignored.push({...entry,group:g.name});
     else if(s.mode!=='bonus'&&q.required!==false&&active(q)){required++;if(entry.score!==null)completed++;else missing.push({...entry,group:g.name});}
     if(!entry.excluded&&a.na&&(!a.note||a.note.trim().length<8))missing.push({id:q.id,name:q.name,why:'دلیل نامرتبط معتبر نیست'});
     const alert=q.alert||{enabled:q.tag==='critical'||q.id==='amenities_3_3',threshold:policy.criticalFloor??1,effect:'cap_score',scope:'cinema',severity:'high'};
     if(!entry.excluded&&entry.score!==null&&alert.enabled&&entry.score<=Number(alert.threshold)){const r={id:q.id,name:q.name,group:g.name,groupId:g.id,sectionId:s.id,score:entry.score,effect:alert.effect||'warning_only',scope:alert.scope||'cinema',severity:alert.severity||'high'};risk.push(r);alerts.push(r);}
    }
    if(excludedGroup(g)&&!(context.exclusionReasons?.[g.id]?.trim().length>=8))errors.push('دلیل خروج پارامتر «'+g.name+'» باید حداقل ۸ نویسه باشد.');
    let score=mean(items.map(x=>[x.score,x.weight]));if(g.id==='amenities_3'&&items.some(x=>x.critical&&x.score!==null&&x.score<=policy.criticalFloor))score=0;
    score=cap(score,alerts,'parameter');const total=items.filter(x=>!x.excluded).reduce((a,x)=>a+x.weight,0);items.forEach(x=>x.effectiveWeight=x.excluded||!total?0:x.weight/total);
    groups.push({id:g.id,name:g.name,weight:Number(g.weight??1),score,items,mode:g.mode,excluded:excludedGroup(g)});
   }
   const raw=mean(groups.filter(g=>g.mode!=='reference').map(g=>[g.score,g.weight])),total=groups.filter(g=>g.score!==null).reduce((a,g)=>a+g.weight,0);groups.forEach(g=>g.effectiveWeight=g.score===null||!total?0:g.weight/total);
   categories.push({id:s.id,name:s.name,weight:Number(s.weight),score:cap(raw,risk.filter(r=>r.sectionId===s.id),'axis'),bonus:s.mode==='bonus',groups});
  }
  const raw=mean(categories.filter(s=>!s.bonus).map(s=>[s.score,s.weight])),extras=categories.filter(s=>s.bonus).flatMap(s=>s.groups),bonus=policy.bonusEnabled?Number(policy.bonusCap)*extras.reduce((n,g)=>n+(g.score??0)/5,0)/Math.max(1,extras.length):0;
  const before=raw===null?null:Math.min(5,raw+bonus),score=cap(before,risk,'cinema'),coverage=required?completed/required:0;
  return {categories,ignored,risk,missing,errors,required,completed,coverage,raw,bonus,before,score,ready:required>0&&coverage===1&&!missing.length&&!errors.length,byItem};
 }
 const api={calculate,parking,mean,conditionErrors};root.CinemaScoring=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
