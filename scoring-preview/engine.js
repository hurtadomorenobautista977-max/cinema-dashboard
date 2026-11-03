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
 function calculate(model,answers={},context={amenities:{}}){
  const categories=[],ignored=[],risk=[],missing=[],byItem=[];let required=0,completed=0;
  for(const s of model.sections){const groups=[];
   for(const g of s.groups){const items=[],rows=[];
    for(const q of g.questions){const a=answers[q.id]||{};let why='';
     if(q.type==='info')why='اطلاعات پشتیبان؛ بدون امتیاز مستقل';
     else if(g.mode==='reference'||q.type==='reference'||q.tag==='reference')why='ارجاع به محل اصلی؛ بدون اثر دوباره در امتیاز';
     else if(s.mode==='bonus'&&context.amenities?.[g.id]!=='yes')why='امکان جانبی موجود یا تأیید نشده؛ بدون جریمه پایه';
     else if(a.na&&a.note?.trim().length>=8)why='نامرتبط: '+a.note;
     const excluded=!!why;
     const auto=q.id==='parking_outcome'?parking(context.parking):null;
     const score=excluded?null:auto!==null?auto:valid(a)?Number(a.score):null;
     const weight=Number(q.weight??1);
     if(excluded)ignored.push({id:q.id,name:q.name,group:g.name,why});
     if(!excluded&&s.mode!=='bonus'&&q.required!==false){required++;if(score!==null)completed++;else missing.push({id:q.id,name:q.name,group:g.name});}
     if(a.na&&!excluded)missing.push({id:q.id,name:q.name,group:g.name,why:'دلیل نامرتبط معتبر نیست'});
     if(score!==null){rows.push([score,weight]);if((q.tag==='critical'||q.id==='amenities_3_3')&&score<=model.policy.criticalFloor)risk.push({id:q.id,name:q.name,group:g.name,score});}
     const entry={id:q.id,name:q.name,score,weight,excluded,why,critical:q.tag==='critical'||q.id==='amenities_3_3',automatic:auto!==null};items.push(entry);byItem.push(entry);
    }
    let score=mean(rows);if(g.id==='amenities_3'&&items.some(x=>x.critical&&x.score!==null&&x.score<=model.policy.criticalFloor))score=0;
    groups.push({id:g.id,name:g.name,weight:Number(g.weight??1),score,items,mode:g.mode});
   }
   categories.push({id:s.id,name:s.name,weight:Number(s.weight),score:mean(groups.filter(g=>g.mode!=='reference').map(g=>[g.score,g.weight])),bonus:s.mode==='bonus',groups});
  }
  const raw=mean(categories.filter(s=>!s.bonus).map(s=>[s.score,s.weight]));
  const extras=categories.filter(s=>s.bonus).flatMap(s=>s.groups);const bonus=model.policy.bonusEnabled?Number(model.policy.bonusCap)*extras.reduce((n,g)=>n+(g.score??0)/5,0)/Math.max(1,extras.length):0;
  const before=raw===null?null:Math.min(5,raw+bonus);const score=before===null?null:risk.length&&model.policy.criticalCapEnabled?Math.min(before,model.policy.criticalCap):before;
  const coverage=required?completed/required:0;
  return {categories,ignored,risk,missing,required,completed,coverage,raw,bonus,before,score,ready:required>0&&coverage===1&&!missing.length,byItem};
 }
 const api={calculate,parking,mean};root.CinemaScoring=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
