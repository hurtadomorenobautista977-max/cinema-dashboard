/* مدل نسخه آزمایشی بر مبنای سند طراحی بهمن سبز؛ قواعد و وزن‌ها پیشنهادی و قابل بازنگری‌اند. */
window.CINEMA_MODEL = {
 id:"cinema-condition-v2-preview", title:"مدل ارزیابی وضعیت سینما", version:1,
 note:"ساختار محورهای ارزیابی و پرسش‌ها از سند مبنا استخراج شده‌اند. وزن‌ها، قواعد تقدم و تأخر، سقف ایمنی و امتیاز تشویقی پیشنهاد اجرایی هستند، نه مصوبه یا الزام استاندارد.",
 policy:{parkingThreshold:4,criticalFloor:1,criticalCap:2.49,bonusCap:0.25, minCoverage:1},
 scale:["فاقد / غیرقابل استفاده","وضعیت بسیار ضعیف","ضعیف و نیازمند اصلاح جدی","قابل قبول با محدودیت","خوب با نقص جزئی","مطلوب و کامل"],
 sections:[
 {id:"access",name:"موقعیت، دسترسی و پارکینگ",weight:0.18,groups:[
 {id:"roads",name:"وضعیت دسترسی به سینما",questions:[
 ["road_access","سهولت دسترسی از طریق معابر شهری"],
 ["road_bus","فاصله و کیفیت دسترسی به ایستگاه اتوبوس"],
 ["road_metro","فاصله و کیفیت دسترسی به ایستگاه مترو","metro"],
 ["road_walk","پیوستگی و کیفیت مسیر پیاده تا ورودی"]]},
 {id:"parking",name:"پارکینگ و جایگزین‌های توقف خودرو",mode:"parking",questions:[
 ["parking_own","وجود، نوع و کفایت ظرفیت پارکینگ اختصاصی / مشترک","primary"],
 ["parking_distance","فاصله پارکینگ عمومی تا ورودی سینما","parkingAlternative"],
 ["parking_space","کفایت ظرفیت پارکینگ عمومی و فضای مجاز اطراف","parkingAlternative"],
 ["parking_peak","امکان یافتن جای پارک در ساعات پرتردد","parkingAlternative"]]},
 {id:"city",name:"موقعیت نسبت به نقاط مهم شهری",questions:[
 ["city_centers","دسترسی به مراکز تجاری، فرهنگی، آموزشی و گردشگری"]]},
 {id:"traffic",name:"میزان تردد و دسترسی‌پذیری محدوده",questions:[
 ["traffic_flow","شرایط ترافیک، ازدحام و ایمنی رفت‌وآمد"],
 ["traffic_pedestrian","دسترسی ایمن و روان در ساعات پرتردد"]]},
 {id:"visibility",name:"قابلیت دیده‌شدن و دسترسی بصری",questions:[
 ["visibility_street","دیده‌شدن ساختمان سینما از معابر اصلی"],
 ["visibility_sign","خوانایی و وضوح نام و تابلو در روز و شب"]]},
 {id:"accessibility",name:"دسترسی افراد دارای معلولیت",questions:[
 ["access_enter","مسیر پیوسته و قابل استفاده تا ورودی","critical"],
 ["access_facilities","دسترسی به سالن‌ها، لابی، سرویس‌ها و خدمات اصلی","critical"]]}
 ]},
 {id:"physical",name:"وضعیت فیزیکی، نوسازی و فضای عمومی",weight:0.20,groups:[
 {id:"facade",name:"نمای بیرونی و سردر",questions:[
 ["facade_health","سلامت فیزیکی نمای بیرونی و میزان فرسودگی"],
 ["facade_entry","وضعیت فیزیکی سردر و اجزای معماری ورودی"],
 ["facade_look","یکپارچگی و کیفیت ظاهر نمای بیرونی"]]},
 {id:"lobby",name:"لابی و فضای انتظار",questions:[
 ["lobby_health","وضعیت فیزیکی و نگهداشت لابی"],
 ["lobby_capacity","تناسب ظرفیت و چیدمان لابی با مراجعه‌کنندگان"],
 ["lobby_furniture","سلامت و کیفیت مبلمان و تجهیزات لابی"]]},
 {id:"halls",name:"وضعیت عمومی سالن‌های نمایش",questions:[
 ["halls_surfaces","سلامت کف، دیوار، سقف و پوشش‌های سالن"],
 ["halls_fixed","سلامت اجزای ثابت و پوشش‌های داخلی"],
 ["halls_maintenance","کیفیت تعمیرات و یکپارچگی ظاهری سالن"]]},
 {id:"seats",name:"کیفیت صندلی‌های سالن",questions:[
 ["seats_physical","سلامت روکش، نشیمن و اجزای صندلی"],
 ["seats_comfort","راحتی نشیمن و پشتی"],
 ["seats_stability","استحکام، اتصال و عملکرد اجزای متحرک"]]},
 {id:"common",name:"فضاهای عمومی",questions:[
 ["common_physical","سلامت سطوح و اجزای ثابت فضاهای عمومی"],
 ["common_pass","روان‌بودن تردد و نبود مانع در مسیرها"],
 ["common_safety","ایمنی پله‌ها، نرده‌ها و اجزای ثابت"]]},
 {id:"restrooms",name:"سرویس‌های بهداشتی",questions:[
 ["restrooms_condition","وضعیت فیزیکی و فرسودگی سرویس‌ها"],
 ["restrooms_function","عملکرد شیرآلات، قفل‌ها و تجهیزات"],
 ["restrooms_capacity","تناسب تعداد و ظرفیت با حجم مخاطبان"]]},
 {id:"lighting",name:"نورپردازی و روشنایی عمومی",questions:[
 ["lighting_function","سلامت و عملکرد چراغ‌های عمومی"],
 ["lighting_quality","کیفیت بصری و تناسب نورپردازی با محیط"]]},
 {id:"signage",name:"تابلوها، علائم و راهنمایی مخاطب",questions:[
 ["signage_coverage","کفایت تابلوهای راهنما در مسیر مخاطب"],
 ["signage_readability","خوانایی، وضوح و جانمایی تابلوها"]]},
 {id:"cleaning",name:"نظافت و نگهداشت",questions:[
 ["cleaning_current","پاکیزگی فضاهای عمومی و سالن‌ها"],
 ["cleaning_restrooms","نظافت سرویس‌های بهداشتی"],
 ["cleaning_program","تداوم نظافت، تأمین اقلام و رفع نواقص روزمره"]]}
 ]},
 {id:"technical",name:"وضعیت فنی و کیفیت تجهیزات",weight:0.22,groups:[
 {id:"projection",name:"تجهیزات نمایش",questions:[
 ["projection_ready","آمادگی و سلامت پروژکتور و اجزای اصلی","critical"],
 ["projection_stable","پایداری عملکرد تجهیزات در طول سانس","critical"]]},
 {id:"image",name:"کیفیت تصویر",questions:[
 ["image_focus","وضوح و فوکوس تصویر"],
 ["image_brightness","میزان و یکنواختی روشنایی تصویر"],
 ["image_color","کیفیت رنگ و کنتراست"],
 ["image_geometry","صحیح‌بودن کادر، تناسب و هندسه تصویر"]]},
 {id:"screen",name:"پرده نمایش",questions:[
 ["screen_surface","سلامت سطح پرده و نبود آسیب"],
 ["screen_uniform","صافی سطح و نبود موج و افتادگی"],
 ["screen_install","نصب، تثبیت و استحکام پرده"]]},
 {id:"sound",name:"سیستم صوتی",questions:[
 ["sound_clarity","وضوح و تفکیک صدای گفتار، موسیقی و افکت"],
 ["sound_distribution","یکنواختی توزیع صدا در سالن"],
 ["sound_stability","نبود نویز، قطع و اختلال صدا"],
 ["sound_acoustics","وضعیت آکوستیک و بازتاب صدا"],
 ["sound_speakers","سلامت بلندگو و تجهیزات اصلی"],
 ["sound_wiring","سلامت کابل‌ها و اتصالات"]]},
 {id:"tech_extra",name:"تجهیزات فنی و جانبی",questions:[
 ["tech_storage","سامانه دریافت، ذخیره و آماده‌سازی محتوای نمایش"],
 ["tech_automation","عملکرد سامانه کنترل و اتوماسیون نمایش"],
 ["tech_power","محافظ برق و برق پشتیبان موردنیاز تجهیزات"],
 ["tech_special","سلامت تجهیزات تخصصی موجود","optionalEquipment"]]},
 {id:"tech_service",name:"نگهداری و سرویس تجهیزات",questions:[
 ["service_plan","برنامه سرویس دوره‌ای و اجرای آن"],
 ["service_records","ثبت و نگهداری سوابق تعمیر و سرویس"],
 ["service_response","سرعت پیگیری و رفع خرابی"],
 ["service_support","دسترسی به نیروی متخصص و پشتیبانی"],
 ["service_parts","تأمین به‌موقع قطعات یدکی ضروری"]]}
 ]},
 {id:"safety",name:"ایمنی، مدیریت بحران و امنیت",weight:0.25,groups:[
 {id:"fire",name:"اعلام و اطفای حریق",questions:[
 ["fire_detection","وجود و آمادگی سامانه تشخیص و اعلام حریق","critical"],
 ["fire_extinguish","کفایت، سلامت و دسترسی به خاموش‌کننده‌ها","critical"],
 ["fire_maintenance","سرویس و بازبینی تجهیزات حریق","critical"]]},
 {id:"egress",name:"خروج اضطراری و مسیر تخلیه",questions:[
 ["egress_count","تعداد و محل خروج‌های اضطراری متناسب با ظرفیت","critical"],
 ["egress_open","بازشدن ایمن و بدون مانع درهای خروج اضطراری","critical"],
 ["egress_route","سلامت، عرض و ایمنی مسیرهای تخلیه","critical"]]},
 {id:"emergency_signs",name:"علائم ایمنی و روشنایی اضطراری",questions:[
 ["safety_signs","خوانایی و پوشش علائم خروج اضطراری","critical"],
 ["safety_light","عملکرد روشنایی اضطراری هنگام قطع برق","critical"]]},
 {id:"facilities_safety",name:"ایمنی تأسیسات و خطرات محیطی",questions:[
 ["safety_electric","ایمنی ظاهری تأسیسات برقی","critical"],
 ["safety_mechanical","ایمنی تأسیسات مکانیکی و گازسوز موجود","critical"],
 ["safety_hazards","نگهداری ایمن مواد و مدیریت خطرات محیطی","critical"]]},
 {id:"preparedness",name:"آمادگی و مدیریت شرایط اضطراری",questions:[
 ["emergency_plan","برنامه مکتوب و به‌روز واکنش اضطراری","critical"],
 ["emergency_staff","تعیین مسئولیت و آموزش کارکنان"],
 ["emergency_drills","اجرای مانور، مستندسازی و اصلاح نواقص"]]},
 {id:"firstaid",name:"تجهیزات کمک‌های اولیه و آمادگی امدادی",questions:[
 ["aid_equipment","کفایت، دسترسی و تاریخ اعتبار تجهیزات کمک‌های اولیه","critical"],
 ["aid_training","آگاهی کارکنان و آمادگی برای فوریت‌های پزشکی"]]},
 {id:"physical_security",name:"امنیت فیزیکی و کنترل دسترسی",questions:[
 ["secure_restricted","کنترل دسترسی به فضاهای فنی و حساس"],
 ["secure_keys","مدیریت کلیدها و مجوزهای ورود"]]},
 {id:"surveillance",name:"نظارت و مدیریت حوادث",questions:[
 ["cctv_coverage","پوشش مناسب دوربین‌های نظارتی"],
 ["cctv_record","ضبط و نگهداری تصاویر"],
 ["cctv_retrieve","امکان بازیابی تصاویر"],
 ["cctv_privacy","محدودبودن دسترسی به تصاویر به افراد مجاز"],
 ["cctv_service","پیگیری و رفع خرابی دوربین‌ها"]]}
 ]},
 {id:"operations",name:"راهبری و بهره‌برداری",weight:0.15,groups:[
 {id:"ticket",name:"زیرساخت و سازوکار بلیت‌فروشی",questions:[
 ["ticket_methods","در دسترس‌بودن روش‌های تعریف‌شده فروش بلیت"],
 ["ticket_info","درستی و کامل‌بودن اطلاعات بلیت"],
 ["ticket_payment","ثبت و تأیید صحیح پرداخت"],
 ["ticket_check","اعتبارسنجی و کنترل ورود به سالن"]]},
 {id:"service",name:"خدمات و پذیرش مخاطب",questions:[
 ["audience_answers","سازوکار پاسخگویی و اطلاع‌رسانی"],
 ["audience_changes","اطلاع‌رسانی تأخیر یا تغییر برنامه"],
 ["audience_complaints","ثبت و پیگیری شکایات و درخواست‌ها"],
 ["audience_lost","رویه ثبت و تحویل اشیای گمشده"],
 ["audience_help","رویه کمک به مخاطبان نیازمند حمایت"]]},
 {id:"revenue",name:"ظرفیت درآمدهای جانبی",questions:[
 ["revenue_identify","شناسایی و مستندسازی ظرفیت‌های بالقوه"],
 ["revenue_conditions","تعیین الزامات حقوقی و شرایط بهره‌برداری"]]},
 {id:"operation_crisis",name:"ظرفیت‌های مدیریت بحران (ارجاع به بخش ایمنی)",mode:"reference",questions:[
 ["ops_crisis","شاخص‌های این بخش در محور ایمنی محاسبه می‌شوند تا دوباره‌شماری نشوند","reference"]]}
 ]},
 {id:"amenities",name:"امکانات و فضاهای جانبی (تشویقی)",weight:0,mode:"bonus",groups:[
 {id:"buffet",name:"بوفه و امکانات پذیرایی",questions:[
 ["buffet_space","وجود و کفایت فضای بوفه"],
 ["buffet_equipment","تجهیزات و زیرساخت‌های پذیرایی"],
 ["buffet_access","دسترسی مخاطب و مدیریت صف"]]},
 {id:"cafe",name:"کافه و رستوران",questions:[
 ["cafe_space","تناسب ظرفیت و کاربری فضای کافه / رستوران"],
 ["cafe_equipment","تجهیزات و زیرساخت موردنیاز"]]},
 {id:"play",name:"فضای بازی و سرگرمی",questions:[
 ["play_space","کفایت و کاربری فضای بازی"],
 ["play_equipment","تنوع و سلامت تجهیزات بازی"],
 ["play_safety","ایمنی فضا و تجهیزات بازی","criticalBonus"]]},
 {id:"events",name:"ظرفیت برگزاری همایش و تئاتر",questions:[
 ["events_hall","وجود فضای مناسب همایش و اجرای نمایشی"],
 ["events_stage","امکانات صحنه و پشت‌صحنه"],
 ["events_technical","امکانات فنی، صوتی و تصویری برنامه"],
 ["events_support","فضاهای پشتیبان و پذیرش رویداد"]]},
 {id:"culture",name:"امکانات فرهنگی و آموزشی",questions:[
 ["culture_space","فضای برگزاری کارگاه و نشست آموزشی"],
 ["culture_equipment","تجهیزات ارائه محتوای آموزشی"],
 ["culture_display","فضا برای نمایش و عرضه محصولات فرهنگی"]]}
 ]}
]};
window.CINEMA_MODEL.sections.forEach(s=>s.groups.forEach(g=>g.questions=g.questions.map(([id,name,tag])=>({id,name,tag:tag||"",required:tag!=="reference",weight:1}))));
