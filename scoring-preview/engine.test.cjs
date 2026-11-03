const assert=require('node:assert/strict'),{calculate,parking,mean}=require('./engine.js');
const results=[];function test(name,expected,fn){const actual=fn();assert.deepEqual(actual,expected);results.push({name,expected,actual,status:'passed'});}
function model(groups,policy={}){return {policy:{criticalFloor:1,criticalCap:2.49,criticalCapEnabled:false,bonusEnabled:false,bonusCap:.25,...policy},sections:[{id:'a',name:'a',weight:1,groups}]};}
const q=(id,weight=1,extra={})=>({id,name:id,weight,...extra}),g=(id,questions,weight=1,extra={})=>({id,name:id,questions,weight,...extra});
test('۱ پارکینگ اختصاصی کافی؛ نبود جایگزین',5,()=>parking({demand:100,own:100,public:0,street:0,verified:true}));
test('۲ ظرفیت مکمل اختصاصی و عمومی',4,()=>parking({demand:100,own:40,public:40,street:0,verified:true}));
test('۳ میانگین وزنی مستقل',4,()=>mean([[5,.75],[1,.25]]));
test('۴ نامرتبط از مخرج خارج می‌شود',5,()=>calculate(model([g('g',[q('x'),q('y')])]),{x:{score:5},y:{na:true,note:'در این مجموعه کاربرد ندارد'}}).score);
test('۵ بررسی‌نشده صفر نیست و نهایی نمی‌شود',[5,.5,false],()=>{const r=calculate(model([g('g',[q('x'),q('y')])]),{x:{score:5}});return [r.score,r.coverage,r.ready]});
test('۶ نقص بحرانی و سقف قابل فعال‌سازی',[1,2.49,4],()=>{const m=model([g('g',[q('x',.2,{tag:'critical'}),q('y',.8)])],{criticalCapEnabled:true});const a={x:{score:0},y:{score:5}},r=calculate(m,a);m.policy.criticalCapEnabled=false;return [r.risk.length,r.score,calculate(m,a).score]});
test('۷ تعداد ردیف‌ها وزن پارامتر را زیاد نمی‌کند',2.5,()=>calculate(model([g('one',[q('x')],.5),g('many',[q('y'),q('z'),q('w')],.5)]),{x:{score:5},y:{score:0},z:{score:0},w:{score:0}}).score);
test('۸ تغییر وزن',4,()=>calculate(model([g('x',[q('x')],.8),g('y',[q('y')],.2)]),{x:{score:5},y:{score:0}}).score);
test('۹ ارجاع دوباره‌شماری نمی‌شود',5,()=>calculate(model([g('main',[q('x')]),g('ref',[q('y')],0,{mode:'reference'})]),{x:{score:5},y:{score:0}}).score);
test('۱۰ استقلال نسخه قدیم از تغییر وزن نسخه جدید',[2.5,4],()=>{const old=model([g('x',[q('x')],.5),g('y',[q('y')],.5)]),next=structuredClone(old),a={x:{score:5},y:{score:0}};next.sections[0].groups[0].weight=.8;next.sections[0].groups[1].weight=.2;return [calculate(old,a).score,calculate(next,a).score]});
test('نامرتبط بدون دلیل مانع نهایی‌سازی',false,()=>calculate(model([g('g',[q('x')])]),{x:{na:true}}).ready);
test('صفر یک ارزیابی کامل است',[0,true],()=>{const r=calculate(model([g('g',[q('x')])]),{x:{score:0}});return [r.score,r.ready]});
test('ظرفیت فاقد تأیید یا ناقص محاسبه نمی‌شود',null,()=>parking({demand:100,own:100,verified:true}));
test('وزن صفر حذف می‌شود',5,()=>calculate(model([g('g',[q('x',1),q('y',0)])]),{x:{score:5},y:{score:0}}).score);
require('fs').writeFileSync(__dirname+'/test-results.json',JSON.stringify(results,null,2));console.log(results.length+' tests passed');
