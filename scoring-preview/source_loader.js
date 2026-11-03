/* خواندن مدل جامع استخراج‌شده از سند ۴۴ صفحه‌ای، بدون وابستگی به قالب قدیمی داشبورد */
window.loadFullCinemaModel = async function (client) {
 const {data,error}=await client.from("cinema_scoring_source_models").select("payload_base64").eq("id","cinema-condition-source-20261103").single();
 if(error||!data?.payload_base64)throw Error("مدل جامع فقط برای مدیر مجاز قابل دریافت است: "+(error?.message||"داده‌ای یافت نشد"));
 const encoded=data.payload_base64;
 if(typeof DecompressionStream==="undefined")throw Error("مرورگر از بازکردن داده‌های فشرده پشتیبانی نمی‌کند.");
 const binary=atob(encoded);
 const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
 const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
 const doc=JSON.parse(await new Response(stream).text());
 if(!Array.isArray(doc.indices)||doc.indices.length!==6)throw Error("ساختار سند معتبر نیست.");
 const baseline=window.CINEMA_MODEL;
 const weights={access:.18,location:.18,physical:.20,technical:.22,safety:.25,operations:.15,amenities:0};
 const critical=(index,param,item)=>{
  if(index==="safety")return ["safety_1","safety_2","safety_3","safety_4"].includes(param)||item==="safety_5_1"||item==="safety_6_1";
  return false;
 };
 const sections=doc.indices.map(s=>({
  id:s.id,name:s.title,description:s.description,weight:weights[s.id]??0,
  mode:s.id==="amenities"?"bonus":"base",
  groups:s.parameters.map(g=>{
   const mode=g.id==="parking"?"outcome":g.aggregation==="reference_only"?"reference":"normal";
   let items=g.items||[];
   // سند پارکینگ دو جدول تکراری دارد. در اینجا فقط چهار ردیف غیرتکراری
   // با منطق «راه‌حل اصلی/جایگزین» ارزیابی می‌شود.

   const questions=items.map((q,i)=>({
    id:q.id,name:q.question||q.title,
    method:q.method||"",
    rubric:q.rubric||q.sourceRubric||"",
    origin:q.rubricOrigin||"source",
    tag:mode==="reference"?"reference":
       critical(s.id,g.id,q.id)?"critical":"",
    required:mode!=="reference", source:q.source||q.sourceRefs||null,
    weight:Number(q.weight)||1
   }));
   return {id:g.id,name:g.title,description:g.description||"",mode,weight:1,
    sourceInfo:g.supportingInfo||[],referenceTo:g.referenceTo||null,
    questions};
  })
 }));
 const importance={accessibility:3,parking:2,access:2,physical_4:2,physical_5:2,physical_6:2,technical_1:3,technical_2:3,technical_4:3,technical_6:2,safety_1:3,safety_2:3,safety_3:2,safety_4:3,safety_5:2,safety_6:2,operations_1:2,operations_2:2};
 sections.forEach(s=>{s.groups.forEach(g=>{g.weight=g.mode==="reference"?0:(importance[g.id]||1);g.questions.forEach(q=>q.weight=q.tag==="critical"?2:1);});const total=s.groups.reduce((n,g)=>n+g.weight,0);s.groups.forEach(g=>g.weight=total?g.weight/total:0);s.groups.forEach(g=>{const n=g.questions.reduce((a,q)=>a+q.weight,0);g.questions.forEach(q=>q.weight=n?q.weight/n:0);});});
 return {id:baseline.id,title:doc.title,version:baseline.version,note:baseline.note,scale:baseline.scale,policy:{...baseline.policy,criticalCapEnabled:false,bonusEnabled:false,minCoverage:1},sections,reviewNotes:doc.reviewNotes||[],documentVersion:doc.version,profileFields:doc.profileFields,sourceArchive:doc.sourceArchive,sourceMapping:doc.sourceMapping,weightBasis:"پیشنهاد آزمایشی: ایمنی و تجهیزات اصلی اولویت بالاتر؛ در هر سطح وزن‌ها مستقل از تعداد ردیف‌ها نرمال می‌شوند. تأیید تخصصی لازم است."};
};
