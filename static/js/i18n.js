/**
 * TRIC Academy - Internationalization (i18n) Engine
 * Seamless English <-> தமிழ் (Tamil) toggle for rules, navigation, and application labels.
 */

(function () {
  'use strict';

  // 32 Official Academy Pool Rules in English and Authentic Tamil
  const TRIC_RULES = {
    en: [
      "All the pass holders should possess proper identity card issued from the TRIC ACADEMY office on production of two passport size photographs and on payment of Rs.50/-. Membership card will be brought every day and will be shown on demand from Authorised officer. Entry to the pool will be made with only IDENTITY CARD.",
      "Swimmers may use the pool at their own risk. TRIC and its officials will not be responsible for any theft, accident, injury, covid 19 and loss of life occurring in the swimming and premises. TRIC ACADEMY AND Officials will not be responsible for any injury/loss of life during the playing period and on compensation or claim will be entertained.",
      "All instruction imposed by TRIC ACADEMY or its authorized representative will be strictly adhered to.",
      "Those who do not know proper swimming should not use the main pool.",
      "Swimmer should bring their own proper swimming dress/costumes in hand and wear it only after checking by the concerned officials/coaches.",
      "Using white/transparent costumes is strictly prohibited.",
      "Swimmers must wear swimming caps is mandatory.",
      "Use of oil, soaps, etc., is strictly prohibited in pool. No one can enter the pool with oil applied on the body and head.",
      "Spitting and passing of urine in the swimming pool is strictly prohibited.",
      "Those who have contagious disease (or) heart disease (or) epilepsy and like diseases should not use the pool.",
      "Intoxicated persons are not allowed to use the pool and consumption of alcohol or alcoholic product and smoking is strictly prohibited in the pool premises.",
      "Eatables should not be brought inside the pool premises.",
      "Jumping from the diving board is strictly prohibited during public session.",
      "Swimmers those who practice diving should use the diving board only in the presence of approved coaches.",
      "School children if not accompanied by guardian concerned teacher will not be allowed inside the pool.",
      "Unnecessary jumping from the deck of the pool is strictly prohibited.",
      "Use of foot wears in the pool deck area is prohibited.",
      "Keep the pool and its surroundings clean and tidy.",
      "Users of the pool shall abide all the rules of the pool and instructions of the staff on duty.",
      "Who are availing concessional charges, especially student should produces their school's student identity card for verification.",
      "Pets are not allowed inside the TRIC ACADEMY premises.",
      "Any deliberate damage/loss caused to the academy property will be recovered from the member.",
      "TRIC ACADEMY Authority reserves the right to suspend/cancel the membership of any individual without giving any prior notice/reason in the interest of efficient functioning of the arrangements.",
      "The access to the family members is limited to areas mentioned in the card.",
      "TRIC ACADEMY will not be responsible for any loss of any valuable/cash.",
      "Fee should be paid the member before use of the pool.",
      "No refund or adjustments of fee will be made in case the swimming pool & other facilities are closed for maintenance or for any other unavoidable reasons.",
      "Documents required for membership - Two passport size photographs, Residential proof or identity proof, Date of birth certificate, Medical Fitness certificate and also the applicant should not suffer from any contagious disease.",
      "TRIC ACADEMY reserves the right to change the training time as and when required.",
      "Any person violates these rules shall be sent out without any refund of fees.",
      "Membership fee or coaching fee will not be transferred to others including family members.",
      "The amount paid by the members or students should use their allocated dates, and the dates they do not used cannot be compensated on others days."
    ],
    ta: [
      "அனைத்து அனுமதி அட்டை வைத்திருப்பவர்களும் இரண்டு பாஸ்போர்ட் அளவு புகைப்படங்களை வழங்கி மற்றும் ரூ. 50 செலுத்தி TRIC அகாடமி அலுவலகத்திலிருந்து வழங்கப்பட்ட முறையான அடையாள அட்டையை வைத்திருக்க வேண்டும். அடையாள அட்டை தினசரி கொண்டுவரப்பட்டு அங்கீகரிக்கப்பட்ட அதிகாரி கேட்கும் போது காண்பிக்கப்பட வேண்டும். அடையாள அட்டை இருந்தால் மட்டுமே நீச்சல் குளத்திற்குள் அனுமதி வழங்கப்படும்.",
      "நீச்சல் வீரர்கள் தங்கள் சொந்த பொறுப்பிலேயே நீச்சல் குளத்தைப் பயன்படுத்த வேண்டும். நீச்சல் குள வளாகத்தில் ஏற்படும் எந்தவொரு திருட்டு, விபத்து, காயம், தொற்றுநோய் மற்றும் உயிரிழப்புகளுக்கு TRIC நிர்வாகமோ அல்லது அதன் அதிகாரிகளோ பொறுப்பாக மாட்டார்கள். பயிற்சி காலத்தில் ஏற்படும் காயங்கள் அல்லது உயிரிழப்புகளுக்கு எந்தவித நஷ்டஈடோ அல்லது கோரிக்கையோ ஏற்கப்படாது.",
      "TRIC அகாடமி அல்லது அதன் அங்கீகரிக்கப்பட்ட அதிகாரிகளால் பிறப்பிக்கப்படும் அனைத்து விதிமுறைகளும் அறிவுறுத்தல்களும் கண்டிப்பாக பின்பற்றப்பட வேண்டும்.",
      "முறையாக நீச்சல் தெரியாதவர்கள் பிரதான நீச்சல் குளத்தைப் பயன்படுத்தக் கூடாது.",
      "நீச்சல் வீரர்கள் தங்களுடைய சரியான நீச்சல் உடையை கொண்டுவர வேண்டும், மேலும் சம்பந்தப்பட்ட அதிகாரிகள் அல்லது பயிற்றுனர்கள் பரிசோதித்த பின்னரே அதை அணிய வேண்டும்.",
      "வெள்ளை அல்லது ஒளிபுகும் (வெளிப்படையான) நீச்சல் ஆடைகள் அணிவது முற்றிலும் தடைசெய்யப்பட்டுள்ளது.",
      "நீச்சல் வீரர்கள் அனைவரும் நீச்சல் தொப்பிகளை (Swimming Caps) அணிவது கட்டாயமாகும்.",
      "நீச்சல் குளத்தில் எண்ணெய், சோப்பு போன்றவற்றை உபயோகிப்பது முற்றிலும் தடைசெய்யப்பட்டுள்ளது. உடல் மற்றும் தலையில் எண்ணெய் தேய்த்து யாரும் குளத்தில் இறங்கக் கூடாது.",
      "நீச்சல் குளத்தில் எச்சில் துப்புவது மற்றும் சிறுநீர் கழிப்பது முற்றிலும் தடைசெய்யப்பட்டுள்ளது.",
      "தொற்று நோய், இதய நோய், வலிப்பு நோய் போன்ற பாதிப்புகள் உள்ளவர்கள் நீச்சல் குளத்தைப் பயன்படுத்தக் கூடாது.",
      "போதையில் இருப்பவர்கள் நீச்சல் குளத்தைப் பயன்படுத்த அனுமதி இல்லை; வளாகத்திற்குள் மது அருந்துவது, புகையிலை மற்றும் புகைபிடிப்பது முற்றிலும் தடைசெய்யப்பட்டுள்ளது.",
      "உணவுப் பண்டங்களை நீச்சல் குள வளாகத்திற்குள் கொண்டு வரக்கூடாது.",
      "பொது நேரங்களில் (Public Sessions) டைவிங் பலகையில் இருந்து குதிப்பது முற்றிலும் தடைசெய்யப்பட்டுள்ளது.",
      "டைவிங் பயிற்சி செய்யும் வீரர்கள் அங்கீகரிக்கப்பட்ட பயிற்றுனர்களின் முன்னிலையில் மட்டுமே டைவிங் பலகையைப் பயன்படுத்த வேண்டும்.",
      "பள்ளி மாணவர்கள் தங்களின் பெற்றோர்/பாதுகாவலர் அல்லது சம்பந்தப்பட்ட ஆசிரியர் உடன் வராவிட்டால் நீச்சல் குளத்திற்குள் அனுமதிக்கப்பட மாட்டார்கள்.",
      "நீச்சல் குளத்தின் விளிம்பிலிருந்து தேவையற்ற முறையில் ஆபத்தான வகையில் குதிப்பது முற்றிலும் தடைசெய்யப்பட்டுள்ளது.",
      "நீச்சல் குளத்தின் தரைத்தளப் பகுதியில் வெளி காலணிகளைப் பயன்படுத்துவது தடைசெய்யப்பட்டுள்ளது.",
      "நீச்சல் குளத்தையும் அதன் சுற்றுப்புறங்களையும் எப்போதும் சுத்தமாகவும் நேர்த்தியாகவும் வைத்திருக்க வேண்டும்.",
      "நீச்சல் குளத்தைப் பயன்படுத்துபவர்கள் குளத்தின் அனைத்து விதிகளுக்கும் பணியில் உள்ள ஊழியர்களின் அறிவுறுத்தல்களுக்கும் கட்டுப்பட வேண்டும்.",
      "கட்டணச் சலுகை பெறும் மாணவர்கள் சரிபார்ப்பிற்காக தங்கள் பள்ளியின் அதிகாரப்பூர்வ மாணவர் அடையாள அட்டையைக் காண்பிக்க வேண்டும்.",
      "TRIC அகாடமி வளாகத்திற்குள் செல்லப்பிராணிகள் கொண்டுவர அனுமதி இல்லை.",
      "அகாடமியின் சொத்துக்களுக்கு வேண்டுமென்றே சேதம் அல்லது இழப்பு ஏற்படுத்தினால் அதற்கான முழு இழப்பீட்டுத் தொகையும் சம்பந்தப்பட்ட உறுப்பினரிடமிருந்து வசூலிக்கப்படும்.",
      "அகாடமியின் திறம்பட செயல்பாட்டைக் கருத்தில் கொண்டு, எவ்வித முன்னறிவிப்போ காரணமோ இன்றி எந்தவொரு நபரின் உறுப்பினர் உரிமையையும் ரத்து செய்ய அல்லது இடைநீக்கம் செய்ய TRIC அகாடமி நிர்வாகத்திற்கு முழு அதிகாரம் உண்டு.",
      "குடும்ப உறுப்பினர்கள் அடையாள அட்டையில் அனுமதிக்கப்பட்ட பகுதிகளுக்கு மட்டுமே செல்ல வேண்டும்.",
      "விலைமதிப்பற்ற பொருட்கள் அல்லது பணம் காணாமல் போனால் அதற்கு TRIC அகாடமி எந்த வகையிலும் பொறுப்பேற்காது.",
      "நீச்சல் குளத்தைப் பயன்படுத்துவதற்கு முன்பு உறுப்பினர் உரிய கட்டணத்தை முழுமையாகச் செலுத்த வேண்டும்.",
      "பராமரிப்பு பணிகளுக்காகவோ அல்லது தவிர்க்க முடியாத சூழ்நிலைகளாலோ நீச்சல் குளம் மூடப்பட்டால் எவ்வித கட்டணத் தொகையும் திருப்பித் தரப்பட மாட்டாது அல்லது ஈடு செய்யப்பட மாட்டாது.",
      "உறுப்பினர் சேர்க்கைக்கு தேவையான ஆவணங்கள்: இரண்டு பாஸ்போர்ட் அளவு புகைப்படங்கள், இருப்பிடச் சான்று அல்லது அடையாளச் சான்று, பிறப்புச் சான்றிதழ், மருத்துவ தகுதிச் சான்றிதழ்; மேலும் விண்ணப்பதாரருக்கு தொற்று நோய் எதுவும் இருக்கக்கூடாது.",
      "தேவைக்கேற்ப பயிற்சி நேரங்களை மாற்றி அமைக்கும் உரிமை TRIC அகாடமி நிர்வாகத்திற்கு உண்டு.",
      "இந்த விதிகளை மீறும் எந்தவொரு நபரும் செலுத்திய கட்டணம் திருப்பித் தராமல் உடனடியாக வெளியேற்றப்படுவார்.",
      "உறுப்பினர் கட்டணம் அல்லது பயிற்சி கட்டணம் குடும்ப உறுப்பினர்கள் உட்பட மற்ற எவருக்கும் எக்காரணம் கொண்டும் மாற்றப்பட மாட்டாது.",
      "உறுப்பினர்கள் அல்லது மாணவர்கள் தங்களுக்கு ஒதுக்கப்பட்ட நாட்களில் மட்டுமே நீச்சல் குளத்தைப் பயன்படுத்த வேண்டும்; பயன்படுத்தாத நாட்களுக்கு மாற்று நாட்கள் வழங்கப்பட மாட்டாது."
    ]
  };

  // UI Strings Dictionary
  const TRIC_I18N = {
    en: {
      // Nav & Brand
      nav_brand_sub: "School of Swimming",
      nav_about: "About",
      nav_batches: "Batches",
      nav_fees: "Fees",
      nav_testimonials: "Testimonials",
      nav_gallery: "Gallery",
      nav_explore: "Explore",
      nav_rules: "Rules & Regulations",
      nav_contact: "Contact",
      nav_login: "Login",
      nav_apply: "Apply for Pass",
      nav_dashboard: "🏊 My Dashboard",
      nav_renew: "⚡ Renew Pass",
      nav_logout: "🚪 Log Out",
      nav_admin: "Admin Hub",
      nav_attendance: "Attendance",
      nav_competition: "Competition Hub",
      lang_btn_text: "தமிழ்",

      // Testimonials & Gallery Lightbox
      heading_testimonials: "Testimonials",
      subheading_testimonials: "Trusted by Hundreds of Swimmers in Tirupur",
      badge_testimonials: "Swimmer & Parent Stories",
      tap_to_expand: "Expand Photo",
      lightbox_close: "Close (Esc)",
      lightbox_prev: "Previous",
      lightbox_next: "Next",

      // Rules Page
      rules_page_title: "Pool Rules & Regulations",
      rules_page_subtitle: "Official Academy Guidelines",
      rules_page_lead: "All members, swimmers, parents, and visitors are strictly required to adhere to the 32 general rules and regulations established by TRIC Academy authority.",
      rules_print_btn: "🖨️ Print Rules",
      rules_back_dash: "← Back to Dashboard",
      rules_back_home: "← Back to Home",
      rules_apply_btn: "Apply for Pass",
      rules_declaration_title: "Declaration Undertaking",
      rules_declaration_text: "\"I have read and understood all the above rules. I do hereby undertake that all injuries/loss of life sustained by me/my above ward trainee due to accident during swimming competition and practice will be at risk and responsibility and also I undertake that I/my above ward will abide by the rules and regulations stated above.\"",

      // Rules Modal
      modal_rules_super: "TRIC Academy – School of Swimming",
      modal_rules_title: "32 General Rules & Regulations",
      modal_rules_lead: "Please review all 32 academy rules carefully. Your confirmation is required before an entry pass or user account can be created.",
      modal_rules_agree_label: "I have read and agree to all 32 Academy Rules",
      modal_rules_close: "Close",
      modal_rules_confirm: "Confirm & Acknowledge",

      // Application Form
      app_swimming: "SWIMMING",
      app_form_title: "APPLICATION FORM FOR ENTRY PASS",
      app_no_label: "NO",
      app_date_label: "DATE",
      app_photo_text: "PASSPORT SIZE PHOTO",
      app_name_label: "NAME OF THE APPLICANT",
      app_name_ph: "IN CAPITAL LETTERS",
      app_address_label: "ADDRESS",
      app_address_ph: "House / Door No., Street Name, Area",
      app_pincode_label: "PIN CODE :",
      app_phone_label: "CONTACT NO",
      app_phone_ph: "10-digit mobile number",
      app_email_label: "EMAIL ID",
      app_email_ph: "active email address",
      app_age_dob_label: "AGE & DATE OF BIRTH",
      app_age_label: "AGE:",
      app_yrs_label: "YRS",
      app_dob_label: "DOB:",
      app_guardian_label: "NAME OF GAURDIAN/PARENT (IN CASE OF MINOR)",
      app_guardian_ph: "Parent or Legal Guardian Name",
      app_occupation_label: "OCCUPATION / PARENT",
      app_occupation_ph: "Parent Occupation",
      app_experience_label: "SWIMMING EXPERIENCE (IF ANY)",
      app_experience_ph: "Beginner / Years of training / Strokes known",
      app_pass_type_label: "TYPE OF PASS REQUIRED",
      app_learn_to_swim: "LEARN TO SWIM",
      app_competition: "COMPETITION",
      app_sponsored_label: "WHETHER THE COMPETITIVE SWIMMER IS SPONSORED BY ANY DEPARTMENT (IF YES PRODUCE CERTIFICATE FROM THE SPONSOR)",
      app_yes: "YES",
      app_no: "NO",
      app_health_declaration_title: "HEALTH DECLARATION",
      app_health_declare_text: "I hereby confirm that I (or my ward) do not suffer from any contagious skin diseases, cardiac conditions, asthma, or epilepsy, and am medically fit to undertake swimming training.",
      app_dpdp_title: "Digital Personal Data Protection (DPDP) Act, 2023 — Section 9 Parental Consent",
      app_dpdp_desc: "Pursuant to Section 9(1) of the Digital Personal Data Protection Act, 2023 (DPDP Act), TRIC Academy collects and processes minor applicant data (name, date of birth, identity card photograph, and medical/fitness declarations) solely for legitimate swimming coaching, safety oversight, batch allocation, and pass issuance. In compliance with Section 9(3), TRIC Academy does not track, profile, or conduct behavioral monitoring of children or serve targeted advertisements.",
      app_dpdp_checkbox_label: "As parent/lawful guardian of the minor applicant, I confirm my legal authority and grant explicit, verifiable consent under the DPDP Act 2023 for TRIC Academy to process my child's personal and health data solely for swimming instruction, pool safety, and identity pass issuance.",
      app_rules_section_title: "32 General Rules & Regulations of TRIC Academy",
      app_btn_read_rules: "📖 Read & Review 32 Rules",
      app_rules_agreed_text: "I have read, understood, and accept all 32 Rules & Regulations of TRIC Academy – School of Swimming.",
      app_rules_confirmed_badge: "✓ 32 Rules & Policies reviewed and agreed.",
      app_submit_btn: "Submit Application & Register Pass",

      // Member Dashboard
      dash_portal_label: "Member Portal",
      dash_welcome: "Welcome,",
      dash_renew_btn: "⚡ Renew Membership",
      dash_logout_btn: "🚪 Log Out",
      dash_family_title: "Family Member Passes",
      dash_family_sub: "Manage multiple linked swimmer passes under a single parent login",
      dash_add_child_btn: "➕ Add Child Pass",
      dash_badge_self: "Parent (Self)",
      dash_badge_child: "Child",
      dash_viewing_child: "Currently viewing child pass for",
      dash_id_card_title: "MEMBER IDENTITY CARD",
      dash_pass_validity: "Pass Validity",
      dash_batch_title: "Batch Assignment",
      dash_recent_attendance: "Recent Attendance Record",
      dash_payment_history: "Membership Payment & Invoice History"
    },
    ta: {
      // Nav & Brand
      nav_brand_sub: "நீச்சல் பயிற்சிப் பள்ளி",
      nav_about: "எங்களை பற்றி",
      nav_batches: "பயிற்சி பிரிவுகள்",
      nav_fees: "கட்டண விபரம்",
      nav_testimonials: "கருத்துக்கள்",
      nav_rules: "நீச்சல் விதிகள்",
      nav_contact: "தொடர்பு",
      nav_login: "உள்நுழைவு",
      nav_apply: "அட்டை விண்ணப்பிக்க",
      nav_dashboard: "🏊 எனது தளம்",
      nav_renew: "⚡ அட்டை புதுப்பிப்பு",
      nav_logout: "🚪 வெளியேறு",
      nav_admin: "நிர்வாக தளம்",
      nav_attendance: "வருகைப் பதிவு",
      nav_competition: "போட்டி நீச்சல்",
      lang_btn_text: "English",

      // Testimonials & Gallery Lightbox
      heading_testimonials: "சான்றுகள் & கருத்துக்கள்",
      subheading_testimonials: "திருப்பூரில் நூற்றுக்கணக்கான நீச்சல் வீரர்களால் நம்பப்படுகிறது",
      badge_testimonials: "நீச்சல் வீரர்கள் & பெற்றோர் கருத்துக்கள்",
      tap_to_expand: "புகைப்படத்தை பெரிதாக்கு",
      lightbox_close: "மூடு (Esc)",
      lightbox_prev: "முந்தையது",
      lightbox_next: "அடுத்தது",

      // Rules Page
      rules_page_title: "நீச்சல் குளம் பொது விதிகள் & ஒழுங்குமுறைகள்",
      rules_page_subtitle: "அகாடமியின் அதிகாரப்பூர்வ வழிகாட்டுதல்கள்",
      rules_page_lead: "அனைத்து உறுப்பினர்கள், நீச்சல் வீரர்கள், பெற்றோர்கள் மற்றும் பார்வையாளர்கள் TRIC அகாடமி நிர்வாகத்தால் நிர்ணயிக்கப்பட்ட 32 பொது விதிகளையும் கண்டிப்பாகப் பின்பற்றுமாறு கேட்டுக்கொள்ளப்படுகிறார்கள்.",
      rules_print_btn: "🖨️ விதிகளை அச்சிடுக",
      rules_back_dash: "← டேஷ்போர்டுக்கு திரும்பு",
      rules_back_home: "← முகப்புக்கு திரும்பு",
      rules_apply_btn: "அட்டைக்கு விண்ணப்பிக்க",
      rules_declaration_title: "உறுதிமொழிப் பத்திரம்",
      rules_declaration_text: "\"மேற்கண்ட அனைத்து விதிகளையும் நான் படித்து முழுமையாகப் புரிந்துகொண்டேன். நீச்சல் பயிற்சி மற்றும் போட்டிகளின் போது எனக்கோ/எனது மேற்பார்வையிலுள்ள நபருக்கோ விபத்துகளால் ஏற்படும் காயங்கள் அல்லது உயிரிழப்புகளுக்கு நானே பொறுப்பேற்கிறேன் என்றும், மேற்கூறிய விதிகளுக்கு முழுமையாகக் கட்டுப்படுவேன் என்றும் இதன்மூலம் உறுதியளிக்கிறேன்.\"",

      // Rules Modal
      modal_rules_super: "TRIC அகாடமி – நீச்சல் பயிற்சிப் பள்ளி",
      modal_rules_title: "32 பொது விதிகள் மற்றும் ஒழுங்குமுறைகள்",
      modal_rules_lead: "தயவுசெய்து அகாடமியின் 32 விதிகளையும் கவனமாக படிக்கவும். அனுமதி அட்டை உருவாக்கப்படுவதற்கு முன் தங்களின் ஒப்புதல் கட்டாயமாகும்.",
      modal_rules_agree_label: "அனைத்து 32 அகாடமி விதிகளையும் படித்து ஏற்றுக்கொள்கிறேன்",
      modal_rules_close: "மூடுக",
      modal_rules_confirm: "படித்தேன் & உறுதிசெய்கிறேன்",

      // Application Form
      app_swimming: "நீச்சல் பயிற்சி",
      app_form_title: "அனுமதி அட்டைக்கான உறுப்பினர் விண்ணப்பப் படிவம்",
      app_no_label: "எண்",
      app_date_label: "தேதி",
      app_photo_text: "பாஸ்போர்ட் அளவு புகைப்படம்",
      app_name_label: "விண்ணப்பதாரரின் முழுப் பெயர்",
      app_name_ph: "ஆங்கில பெரிய எழுத்துக்களில்",
      app_address_label: "வசிப்பிட முகவரி",
      app_address_ph: "வீட்டு எண், தெரு பெயர், பகுதி",
      app_pincode_label: "அஞ்சல் குறியீடு :",
      app_phone_label: "தொடர்பு தொலைபேசி எண்",
      app_phone_ph: "10-இலக்க மொபைல் எண்",
      app_email_label: "மின்னஞ்சல் முகவரி",
      app_email_ph: "செயலில் உள்ள மின்னஞ்சல்",
      app_age_dob_label: "வயது மற்றும் பிறந்த தேதி",
      app_age_label: "வயது:",
      app_yrs_label: "ஆண்டுகள்",
      app_dob_label: "பிறந்த தேதி:",
      app_guardian_label: "பெற்றோர் / பாதுகாவலர் பெயர் (18 வயதுக்குட்பட்டவர்கள்)",
      app_guardian_ph: "பெற்றோர் அல்லது பாதுகாவலர் பெயர்",
      app_occupation_label: "பெற்றோர் / பாதுகாவலர் தொழில்",
      app_occupation_ph: "பெற்றோரின் தொழில்",
      app_experience_label: "முந்தைய நீச்சல் அனுபவம் (இருப்பின்)",
      app_experience_ph: "தொடக்க நிலை / பயிற்சி ஆண்டுகள் / தெரிந்த நீச்சல் முறைகள்",
      app_pass_type_label: "தேவையான அனுமதி அட்டை வகை",
      app_learn_to_swim: "நீச்சல் கற்றல் (LEARN TO SWIM)",
      app_competition: "போட்டி நீச்சல் பயிற்சி (COMPETITION)",
      app_sponsored_label: "போட்டி நீச்சல் வீரர் ஏதேனும் துறையால் ஸ்பான்சர் செய்யப்பட்டுள்ளாரா? (ஆம் எனில் சான்றிதழ் இணைக்கவும்)",
      app_yes: "ஆம்",
      app_no: "இல்லை",
      app_health_declaration_title: "உடல்நல உறுதிமொழி",
      app_health_declare_text: "எனக்கு (அல்லது எனது குழந்தைக்கு) எவ்வித தொற்று நோய்களோ, இதய பாதிப்போ, ஆஸ்துமாவோ அல்லது வலிப்பு நோயோ இல்லை என்பதையும், நீச்சல் பயிற்சி பெற முழு உடற்தகுதியுடன் உள்ளேன் என்பதையும் உறுதியளிக்கிறேன்.",
      app_dpdp_title: "டிஜிட்டல் தனிநபர் தரவு பாதுகாப்பு சட்டம் 2023 (DPDP Act) — பிரிவு 9 பெற்றோர் ஒப்புதல்",
      app_dpdp_desc: "இந்தியாவின் டிஜிட்டல் தனிநபர் தரவு பாதுகாப்புச் சட்டம் 2023 பிரிவு 9(1)-இன் கீழ், சிறார்களின் தனிநபர் மற்றும் மருத்துவத் தரவுகள் நீச்சல் பயிற்சி, பாதுகாப்பு மேற்பார்வை மற்றும் அடையாள அட்டை வழங்குவதற்காக மட்டுமே சேகரிக்கப்படுகின்றன. சிறார்களைக் கண்காணிப்பதோ அல்லது விளம்பர நோக்கங்களுக்காகப் பயன்படுத்துவதோ முற்றிலும் செய்யப்படாது.",
      app_dpdp_checkbox_label: "சிறுவர் விண்ணப்பதாரரின் பெற்றோர்/பாதுகாவலராகிய நான், DPDP சட்டம் 2023-இன் கீழ் நீச்சல் பயிற்சி மற்றும் பாதுகாப்பு பணிகளுக்காக எனது குழந்தையின் தரவுகளைப் பயன்படுத்த முழு ஒப்புதல் அளிக்கிறேன்.",
      app_rules_section_title: "TRIC அகாடமியின் 32 பொது விதிகள் மற்றும் ஒழுங்குமுறைகள்",
      app_btn_read_rules: "📖 32 விதிகளைப் படிக்கவும்",
      app_rules_agreed_text: "TRIC அகாடமியின் அனைத்து 32 விதிகளையும் நான் படித்து, முழுமையாக ஏற்றுக்கொள்கிறேன்.",
      app_rules_confirmed_badge: "✓ 32 விதிகளும் படிக்கப்பட்டு உறுதிசெய்யப்பட்டது.",
      app_submit_btn: "விண்ணப்பத்தைச் சமர்ப்பித்து பதிவு செய்க",

      // Member Dashboard
      dash_portal_label: "உறுப்பினர் தளம்",
      dash_welcome: "வரவேற்கிறோம்,",
      dash_renew_btn: "⚡ அட்டையைப் புதுப்பிக்கவும்",
      dash_logout_btn: "🚪 வெளியேறு",
      dash_family_title: "குடும்ப அனுமதி அட்டைகள்",
      dash_family_sub: "உங்கள் ஒரே பெற்றோர் கணக்கின் கீழ் அனைத்து குழந்தை அட்டைகளையும் நிர்வகிக்கவும்",
      dash_add_child_btn: "➕ புதிய குழந்தை அட்டை சேர்க்க",
      dash_badge_self: "பெற்றோர் (சுய)",
      dash_badge_child: "குழந்தை",
      dash_viewing_child: "தற்போது பார்க்கப்படும் குழந்தை அட்டை:",
      dash_id_card_title: "உறுப்பினர் அடையாள அட்டை",
      dash_pass_validity: "அனுமதி செல்லுபடியாகும் காலம்",
      dash_batch_title: "ஒதுக்கப்பட்ட பயிற்சி பிரிவு",
      dash_recent_attendance: "சமீபத்திய வருகைப் பதிவு",
      dash_payment_history: "கட்டண ரசீது & வரலாறு"
    }
  };

  /**
   * Get current selected language ('en' or 'ta')
   */
  function getCurrentLanguage() {
    return 'en';
  }

  /**
   * Apply language to all registered elements in the document
   */
  function applyLanguage(lang) {
    if (lang !== 'en' && lang !== 'ta') {
      lang = 'en';
    }
    localStorage.setItem('tric_lang', lang);

    // Update document HTML lang attribute
    document.documentElement.lang = lang;

    // Update toggle buttons text & tooltip
    const nextLang = lang === 'en' ? 'ta' : 'en';
    const nextLabel = TRIC_I18N[lang].lang_btn_text;

    const desktopBtnLabel = document.getElementById('langToggleLabel');
    if (desktopBtnLabel) {
      desktopBtnLabel.textContent = nextLabel;
    }
    const mobileBtnLabel = document.getElementById('mobileLangToggleLabel');
    if (mobileBtnLabel) {
      mobileBtnLabel.textContent = nextLabel;
    }

    const desktopBtn = document.getElementById('langToggleBtn');
    if (desktopBtn) {
      desktopBtn.title = lang === 'en' ? 'தமிழில் படிக்க இங்கே கிளிக் செய்யவும்' : 'Switch to English';
      desktopBtn.setAttribute('aria-label', desktopBtn.title);
    }
    const mobileBtn = document.getElementById('mobileLangToggleBtn');
    if (mobileBtn) {
      mobileBtn.title = desktopBtn ? desktopBtn.title : '';
    }

    // 1. Translate elements with data-i18n
    const translatableElements = document.querySelectorAll('[data-i18n]');
    translatableElements.forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (TRIC_I18N[lang] && TRIC_I18N[lang][key] !== undefined) {
        // If element contains simple text or HTML
        el.textContent = TRIC_I18N[lang][key];
      }
    });

    // 2. Translate placeholders with data-i18n-placeholder
    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderElements.forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (TRIC_I18N[lang] && TRIC_I18N[lang][key] !== undefined) {
        el.setAttribute('placeholder', TRIC_I18N[lang][key]);
      }
    });

    // 3. Translate all 32 Rules lists (<ol class="tric-rules-list">)
    const rulesLists = document.querySelectorAll('.tric-rules-list');
    rulesLists.forEach((ol) => {
      const listItems = ol.querySelectorAll('li');
      listItems.forEach((li, idx) => {
        if (TRIC_RULES[lang] && TRIC_RULES[lang][idx]) {
          li.textContent = TRIC_RULES[lang][idx];
        }
      });
    });

    // Dispatch event for custom components
    window.dispatchEvent(new CustomEvent('tricLanguageChanged', { detail: { lang: lang } }));
  }

  /**
   * Toggle between English and Tamil
   */
  function toggleTricLanguage() {
    const current = getCurrentLanguage();
    const target = current === 'en' ? 'ta' : 'en';
    applyLanguage(target);
  }

  // Expose to window
  window.TRIC_RULES = TRIC_RULES;
  window.TRIC_I18N = TRIC_I18N;
  window.getCurrentLanguage = getCurrentLanguage;
  window.applyLanguage = applyLanguage;
  window.toggleTricLanguage = toggleTricLanguage;

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyLanguage(getCurrentLanguage());
    });
  } else {
    applyLanguage(getCurrentLanguage());
  }
})();
