/* خواندن مدل جامع استخراج‌شده از سند ۴۴ صفحه‌ای، بدون وابستگی به قالب قدیمی داشبورد */
window.loadFullCinemaModel = async function () {
 const {data,error}=await arguments[0].from("cinema_scoring_source_models").select("payload_base64").eq("id",window.CINEMA_MODEL.id).single();
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
   const mode=g.id==="parking"?"parking":g.aggregation==="reference_only"?"reference":"normal";
   let items=g.items||[];
   // سند پارکینگ دو جدول تکراری دارد. در اینجا فقط چهار ردیف غیرتکراری
   // با منطق «راه‌حل اصلی/جایگزین» ارزیابی می‌شود.
   if(g.id==="parking")items=(g.supportingInfo||[]).filter(x=>["parking_info_t2_1","parking_info_t3_1","parking_info_t3_2","parking_info_t3_3"].includes(x.id));
   const questions=items.map((q,i)=>({
    id:q.id,name:q.question||q.title,
    method:q.method||"",
    rubric:q.rubric||q.sourceRubric||"",
    origin:q.rubricOrigin||"source",
    tag:g.id==="parking"?(i===0?"primary":"parkingAlternative"):
       mode==="reference"?"reference":
       critical(s.id,g.id,q.id)?"critical":"",
    required:mode!=="reference",
    weight:Number(q.weight)||1
   }));
   return {id:g.id,name:g.title,description:g.description||"",mode,
    sourceInfo:g.supportingInfo||[],referenceTo:g.referenceTo||null,
    questions};
  })
 }));
 return {id:baseline.id,title:doc.title,version:baseline.version,note:baseline.note,scale:baseline.scale,policy:baseline.policy,sections,reviewNotes:doc.reviewNotes||[],documentVersion:doc.version};
};