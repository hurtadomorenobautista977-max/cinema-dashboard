/* استخراج مستقیم ردیف‌های جداول سند؛ سند فقط برای مدیر مجاز دریافت می‌شود. */
window.loadFullCinemaModel=async function(client){
 const {data,error}=await client.from('cinema_scoring_source_models').select('payload_base64').eq('id','cinema-condition-source-20261103').single();
 if(error||!data?.payload_base64)throw new Error('دریافت سند ارزیابی ناموفق بود: '+(error?.message||'منبع موجود نیست'));
 const bytes=Uint8Array.from(atob(data.payload_base64),c=>c.charCodeAt(0));
 const doc=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
 if(!doc.sourceArchive?.tables||!doc.sourceMapping?.length)throw new Error('جداول کامل سند در دسترس نیستند.');
 const weights={location:.17,physical:.19,technical:.21,safety:.24,operations:.14,amenities:.05};
 const priority={access:2,parking:2,accessibility:3,physical_4:2,physical_5:2,physical_6:2,technical_1:3,technical_2:3,technical_4:3,technical_6:2,safety_1:3,safety_2:3,safety_3:2,safety_4:3,safety_5:2,safety_6:2,operations_1:2,operations_2:2};
 const sections=doc.indices.map(s=>({id:s.id,name:s.title,description:s.description||'',weight:weights[s.id],groups:s.parameters.map(g=>({id:g.id,name:g.title,description:g.description||'',weight:g.id==='operations_4'?0:priority[g.id]||1,mode:'normal',questions:[]}))}));
 for(const m of doc.sourceMapping){
  const s=sections.find(s=>s.id===m.target?.[0]),g=s?.groups.find(g=>g.id===m.target?.[1]);if(!g)throw new Error('جایگاه ردیف '+m.table+' / '+m.row+' مشخص نیست.');
  const cells=m.original,first=m.table===1;const duplicate=(m.table===2&&m.row>1)||g.id==='operations_4';
  const sensitive=s.id==='safety'&&['safety_1','safety_2','safety_3','safety_4'].includes(g.id);
  g.questions.push({id:'source_t'+m.table+'_r'+m.row,name:cells[first?1:2]||'ردیف '+m.row,method:cells[first?0:1]||'',rubric:first?'':cells[0]||'',weight:duplicate?0:((sensitive&&m.row<=2)||/پایداری|وضوح|بدون مانع|سلامت|آمادگی|ظرفیت/.test(cells[first?1:2]||''))?2:1,tag:duplicate?'reference':sensitive?'critical':'',required:!duplicate,type:duplicate?'reference':'scored',origin:'source',source:{table:m.table,row:m.row,original:cells},referenceTo:duplicate?(g.id==='operations_4'?'safety':'parking'):'',note:duplicate?'ردیف سند حفظ شده؛ برای جلوگیری از دوباره‌شماری فعلاً مرجع است. نوع و وزن آن در مدیریت شاخص‌ها قابل تغییر است.':first?'در سند معیار تفصیلی صفر تا پنج ارائه نشده؛ امتیاز با تشخیص مستند کارشناس ثبت شود.':''});
 }
 for(const s of sections){const total=s.groups.reduce((a,g)=>a+g.weight,0);for(const g of s.groups){g.weight=total?g.weight/total:0;const w=g.questions.reduce((a,q)=>a+q.weight,0);g.questions.forEach(q=>q.weight=w?q.weight/w:0);}}
 return {id:window.CINEMA_MODEL.id,version:1,title:'نظام ارزیابی و رتبه‌بندی سینماها',policy:{criticalFloor:1,criticalCap:3,criticalCapEnabled:false,bonusEnabled:false,bonusCap:0,minCoverage:1},sections,profileFields:doc.profileFields,sourceArchive:doc.sourceArchive,note:'ارزیابی کارشناس روی ردیف‌های اصلی سند؛ تجمیع وزنی ردیف ← پارامتر ← شاخص ← سینما. وزن‌ها پیشنهادی و قابل ویرایش‌اند.',reviewNotes:doc.reviewNotes||[]};
};
