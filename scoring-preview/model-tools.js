(function(root){
'use strict';
const active=q=>q.type!=='info'&&q.type!=='reference'&&q.tag!=='reference';
function distribute(xs,eligible=()=>true){const yes=xs.filter(eligible);xs.filter(x=>!eligible(x)).forEach(x=>x.weight=0);const sum=yes.reduce((a,x)=>a+(Number.isFinite(Number(x.weight))&&Number(x.weight)>0?Number(x.weight):0),0);yes.forEach(x=>x.weight=sum?Math.max(0,Number(x.weight)||0)/sum:1/Math.max(1,yes.length));}
function normalize(m){for(const s of m.sections){for(const g of s.groups)distribute(g.questions,active);distribute(s.groups,g=>g.questions.some(active));}distribute(m.sections,s=>s.groups.some(g=>g.questions.some(active)));return m;}
function validate(m){const errors=[],seen=new Set(),weight=x=>x!==null&&x!==undefined&&x!==''&&Number.isFinite(Number(x))&&Number(x)>=0&&Number(x)<=1,sum=xs=>xs.reduce((a,x)=>a+Number(x.weight),0),named=(x,label)=>{if(!x.id||!/^[a-zA-Z0-9_-]+$/.test(x.id)||seen.has(x.id))errors.push('شناسه تکراری یا خالی: '+label);seen.add(x.id);if(!x.name?.trim())errors.push('عنوان خالی: '+label);if(!weight(x.weight))errors.push('وزن نامعتبر: '+label);};
 if(!m.sections?.length)return ['حداقل یک شاخص لازم است.'];for(const s of m.sections){named(s,'شاخص');if(!s.groups?.length){errors.push('شاخص «'+s.name+'» پارامتر ندارد.');continue;}for(const g of s.groups){named(g,'پارامتر');if(!g.questions?.length){errors.push('جدول «'+g.name+'» ردیف ندارد.');continue;}for(const q of g.questions){named(q,'ردیف');if(!active(q)&&Number(q.weight)!==0)errors.push('وزن ردیف مرجع یا اطلاعاتی باید صفر باشد: '+q.name);if(active(q)&&q.required===false)errors.push('ردیف امتیازی باید مشمول پوشش ارزیابی باشد: '+q.name);}const qs=g.questions.filter(active);if(qs.length&&Math.abs(sum(qs)-1)>1e-6)errors.push('جمع وزن ردیف‌های «'+g.name+'» باید ۱ باشد.');if(!qs.length&&g.weight!==0)errors.push('پارامتر بدون ردیف امتیازی باید وزن صفر داشته باشد.');}if(s.groups.some(g=>g.questions.some(active))&&Math.abs(sum(s.groups)-1)>1e-6)errors.push('جمع وزن پارامترهای «'+s.name+'» باید ۱ باشد.');}if(Math.abs(sum(m.sections)-1)>1e-6)errors.push('جمع وزن شاخص‌ها باید ۱ باشد.');if(root.CinemaScoring)errors.push(...root.CinemaScoring.conditionErrors(m));return errors;}
function snapshot(m){const x=JSON.parse(JSON.stringify(m));delete x.sourceArchive;return x;}
const rank=(scores,score)=>1+scores.filter(s=>s>score+1e-12).length;
function carryResponses(model,prior){const ids=new Set(model.sections.flatMap(s=>s.groups).flatMap(g=>g.questions).map(q=>q.id));return JSON.parse(JSON.stringify(Object.fromEntries(Object.entries(prior||{}).filter(([id])=>ids.has(id)))));}
function setNewShare(xs,item,eligible=()=>true){
 const others=xs.filter(x=>x!==item&&eligible(x));if(!eligible(item)){item.weight=0;distribute(xs,eligible);return;}
 const share=1/(others.length+1),sum=others.reduce((n,x)=>n+Math.max(0,Number(x.weight)||0),0);
 for(const x of others)x.weight=(1-share)*(sum?Math.max(0,Number(x.weight)||0)/sum:1/others.length);
 item.weight=share;xs.filter(x=>!eligible(x)).forEach(x=>x.weight=0);
}
function adjustShares(weights,index,value,locked=[]){
 const out=weights.map(w=>Math.max(0,Number(w)||0));if(locked.includes(index))return out;
 const fixed=locked.filter(i=>i!==index),fixedTotal=fixed.reduce((n,i)=>n+out[i],0),others=out.map((_,i)=>i).filter(i=>i!==index&&!fixed.includes(i));
 const available=Math.max(0,1-fixedTotal);out[index]=others.length?Math.max(0,Math.min(available,Number(value)||0)):available;
 const remaining=available-out[index],old=others.reduce((n,i)=>n+out[i],0);
 for(const i of others)out[i]=remaining*(old?out[i]/old:1/others.length);
 if(others.length)out[others.at(-1)]+=1-out.reduce((a,b)=>a+b,0);
 return out;
}

const api={active,normalize,validate,snapshot,rank,carryResponses,setNewShare,adjustShares};root.CinemaModelTools=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
