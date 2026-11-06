"""
หน้าเสริม: ทำไมถึงสร้างโปรเจกต์นี้ (มุมมองฝ่ายป้องกัน)
เป็นหน้าแยกจาก app.py ไม่กระทบโมเดลหรือส่วนทำนายผล
ใช้ธีมมืด/สว่างเดียวกับหน้าหลัก (อ่านค่าจาก st.session_state.is_dark)
"""

import streamlit as st

st.set_page_config(
    page_title="ทำไมต้องสร้างระบบป้องกัน | Mini-Project",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------
# ธีม (ใช้ค่าเดียวกับหน้าหลัก)
# ----------------------------------------------------
is_dark = st.session_state.get("is_dark", True)

if is_dark:
    bg_app, bg_card, border = "#121212", "#1F1F1F", "#2D2D2D"
    text_main, text_sub = "#FFFFFF", "#9E9E9E"
    inner_bg, inner_border = "#181818", "#2B2B2B"
    hero_grad = "linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%)"
else:
    bg_app, bg_card, border = "#F8FAFC", "#FFFFFF", "#E2E8F0"
    text_main, text_sub = "#0F172A", "#64748B"
    inner_bg, inner_border = "#F8FAFC", "#E2E8F0"
    hero_grad = "linear-gradient(180deg, #000000 0%, #666666 100%)"

st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
    .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp li, .stApp button, .stApp input {{
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}
    .stApp {{ background-color: {bg_app} !important; color: {text_main} !important; }}
    
    /* ป้องกันตัวอักษร ligature หลุดซ้อนข้อความ เช่น keyboard_arrow_down หรือ arrd_ */
    [data-testid="stIconMaterial"],
    [data-testid*="stIcon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    [data-testid="stExpander"] summary span:first-child,
    .material-symbols-rounded,
    [class*="material-symbols"] {{
        font-family: "Material Symbols Rounded" !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-smoothing: antialiased !important;
        overflow: hidden !important;
        vertical-align: middle !important;
    }}
    .hero {{ max-width: 680px; margin: 0 auto 32px auto; text-align: center; }}
    .hero-badge {{
        display: inline-block; padding: 4px 12px; border-radius: 9999px;
        border: 1px solid {inner_border}; background: {inner_bg};
        color: #00D26A; font-size: 13px; font-weight: 600; margin-bottom: 16px;
    }}
    .hero-title {{
        font-size: 36px; font-weight: 700; line-height: 1.2; text-wrap: balance;
        background: {hero_grad}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }}
    .hero-sub {{ font-size: 16px; line-height: 1.5; color: {text_sub}; text-wrap: balance; }}
    .card {{
        background: {bg_card}; border: 1px solid {border}; border-radius: 16px;
        padding: 24px; margin-bottom: 24px; color: {text_main};
    }}
    .card h3 {{ font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: {text_main}; }}
    .card p, .card li {{ font-size: 15px; line-height: 1.6; color: {text_sub}; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
    .tile {{
        background: {inner_bg}; border: 1px solid {inner_border}; border-radius: 12px; padding: 16px;
    }}
    .tile-tag {{ font-size: 12px; font-weight: 700; margin-bottom: 6px; }}
    .tile-title {{ font-size: 16px; font-weight: 600; color: {text_main}; margin-bottom: 6px; }}
    .tile-desc {{ font-size: 14px; line-height: 1.5; color: {text_sub}; }}
    .quote {{
        border: 1px solid #00D26A; border-radius: 12px; padding: 16px 20px;
        background: {inner_bg}; color: {text_main}; font-size: 16px; line-height: 1.6;
    }}
</style>
""", unsafe_allow_html=True)

st.page_link("app.py", label="กลับไปหน้าทดสอบโมเดล", icon="⬅️")

# ----------------------------------------------------
# HERO
# ----------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-badge">ที่มาของโปรเจกต์ · มุมมองฝ่ายป้องกัน (Blue Team)</div>
    <div class="hero-title">เมื่อแฮกเกอร์ใช้ AI โจมตี<br>ฝ่ายป้องกันก็ต้องใช้ AI ตอบโต้</div>
    <div class="hero-sub">
        โปรเจกต์นี้เริ่มจากคำถามง่ายๆ ว่า ถ้าธนาคารและสถาบันการเงินทั่วโลกกำลังถูกโจมตีด้วยเครื่องมือ AI
        แล้ว "ฝ่ายป้องกัน" เขาทำงานกันอย่างไร
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. แรงบันดาลใจ
# ----------------------------------------------------
st.markdown("""
<div class="card">
    <h3>1. แรงบันดาลใจ : ทำไมผมถึงสร้างโปรเจกต์นี้</h3>
    <p>
        ทุกวันนี้เราเห็นข่าวแฮกเกอร์นำ AI มาใช้โจมตีภาคการเงินบ่อยขึ้นเรื่อยๆ ทั้งการปลอมเสียงผู้บริหารเพื่อสั่งโอนเงิน
        การสร้างเว็บไซต์ธนาคารปลอมที่เหมือนของจริง และการโจมตีระบบของสถาบันการเงินในหลายภูมิภาค
        ไม่ว่าจะเป็นยุโรป สหรัฐอเมริกา ญี่ปุ่น อินเดีย หรือเกาหลีใต้
    </p>
    <p>
        ข่าวส่วนใหญ่มักเล่าจากมุมของ <b>ฝ่ายโจมตี</b> ว่าแฮกเกอร์ทำอะไร แต่ผมอยากรู้อีกด้านหนึ่งว่า
        <b>ฝ่ายป้องกันจะรู้ตัวได้อย่างไรว่ากำลังถูกโจมตี</b> และจะใช้ AI มาช่วยตอบโต้ได้หรือไม่
        มินิโปรเจกต์นี้จึงเป็นการทดลองสร้าง "ด่านตรวจจับ" ด้วย Machine Learning ด้วยตัวเอง
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. ภัยคุกคามที่ขับเคลื่อนด้วย AI
# ----------------------------------------------------
st.markdown("""
<div class="card">
    <h3>2. ภัยคุกคามยุคใหม่ที่แฮกเกอร์ใช้ AI</h3>
    <div class="grid">
        <div class="tile">
            <div class="tile-tag" style="color:#FF4B4B;">DEEPFAKE เสียงและวิดีโอ</div>
            <div class="tile-title">ปลอมเสียงหรือหน้าผู้บริหาร</div>
            <div class="tile-desc">ใช้ AI โคลนเสียงหรือวิดีโอคอลปลอม หลอกให้พนักงานฝ่ายการเงินโอนเงินออกไป</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#FFA800;">AI PHISHING</div>
            <div class="tile-title">เว็บและข้อความหลอกลวงที่แนบเนียน</div>
            <div class="tile-desc">AI สร้างหน้าเว็บธนาคารปลอมและข้อความภาษาไทยที่สมจริง ทำให้จับผิดได้ยากกว่าเดิม</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#A855F7;">AUTOMATED ATTACKS</div>
            <div class="tile-title">โจมตีอัตโนมัติด้วยความเร็วสูง</div>
            <div class="tile-desc">บอทสแกนช่องโหว่ สุ่มรหัสผ่าน หรือยิงทราฟฟิกถล่มระบบได้ตลอด 24 ชั่วโมง เร็วเกินกว่าคนจะเฝ้าดูทัน</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📰 ตัวอย่างเหตุการณ์จริงที่มีการรายงานในสื่อ"):
    st.markdown("""
    * **ฮ่องกง (2024):** พนักงานบริษัทข้ามชาติถูกหลอกให้โอนเงินราว 25 ล้านดอลลาร์สหรัฐ
      หลังเข้าประชุมวิดีโอคอลที่ผู้เข้าร่วมเป็นภาพ Deepfake ของผู้บริหาร (บริษัท Arup ยืนยันว่าเป็นผู้เสียหาย)
    * **สหราชอาณาจักร (2019):** ผู้บริหารบริษัทพลังงานถูกหลอกโอนเงินราว 220,000 ยูโร
      เพราะได้รับโทรศัพท์ที่ใช้ AI เลียนเสียง CEO ของบริษัทแม่

    > หมายเหตุ: ตัวเลขข้างต้นอ้างอิงจากข่าวที่เผยแพร่สาธารณะ หากนำไปใส่ในรายงาน ควรแนบลิงก์แหล่งข่าวต้นฉบับประกอบ
    """)

# ----------------------------------------------------
# 3. ฝ่ายป้องกันทำงานอย่างไร
# ----------------------------------------------------
st.markdown("""
<div class="card">
    <h3>3. ฝ่ายป้องกันทำงานอย่างไร : แนวคิดป้องกันหลายชั้น (Defense in Depth)</h3>
    <p>ไม่มีเครื่องมือชิ้นเดียวที่กันได้ทุกอย่าง ฝ่ายป้องกันจึงวางด่านซ้อนกันหลายชั้น ถ้าด่านหนึ่งพลาด ด่านถัดไปยังช่วยจับได้</p>
    <div class="grid">
        <div class="tile">
            <div class="tile-tag" style="color:#00D26A;">ชั้นที่ 1 · คน</div>
            <div class="tile-title">สร้างความตระหนักรู้</div>
            <div class="tile-desc">อบรมพนักงานให้สงสัยไว้ก่อน เช่น โทรกลับเบอร์ทางการทุกครั้งเมื่อมีคำสั่งโอนเงินด่วน</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#00D26A;">ชั้นที่ 2 · กระบวนการ</div>
            <div class="tile-title">ขั้นตอนยืนยันหลายคน</div>
            <div class="tile-desc">การโอนเงินจำนวนมากต้องมีผู้อนุมัติมากกว่าหนึ่งคน และยืนยันผ่านช่องทางที่สอง</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#00D26A;">ชั้นที่ 3 · เทคโนโลยี</div>
            <div class="tile-title">AI ตรวจจับพฤติกรรมผิดปกติ</div>
            <div class="tile-desc">ใช้ Machine Learning เฝ้าดูทราฟฟิกเครือข่ายและธุรกรรม แจ้งเตือนทันทีเมื่อพฤติกรรมไม่เหมือนปกติ</div>
        </div>
    </div>
    <p style="margin-top:16px;"><b>โปรเจกต์นี้คือการทดลองสร้าง "ชั้นที่ 3"</b> ในรูปแบบที่เล็กและเข้าใจง่าย</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. โปรเจกต์นี้อยู่ตรงไหน (ขอบเขตแบบตรงไปตรงมา)
# ----------------------------------------------------
st.markdown("""<div class="card"><h3>4. โปรเจกต์นี้ช่วยป้องกันอะไรได้บ้าง</h3>
<p>โมเดลในโปรเจกต์นี้ทำงานที่ <b>ระดับเครือข่าย (Network Layer)</b> คือดูพฤติกรรมการเชื่อมต่อ ไม่ได้ฟังเสียงหรือดูวิดีโอ
จึงขอระบุขอบเขตให้ชัดเจนดังนี้</p></div>""", unsafe_allow_html=True)

scope_col1, scope_col2 = st.columns(2)
with scope_col1:
    st.success("""
**✅ สิ่งที่โมเดลนี้ตรวจจับได้**

* **DDoS** : บอทยิงทราฟฟิกถล่มเว็บธนาคารจนล่ม
* **Port Scan** : แฮกเกอร์ (หรือบอท AI) สำรวจหาช่องโหว่ของเซิร์ฟเวอร์
* **Brute Force** : การสุ่มรหัสผ่านเข้าระบบซ้ำๆ แบบอัตโนมัติ
""")
with scope_col2:
    st.warning("""
**⏳ สิ่งที่ยังอยู่นอกขอบเขต (ต่อยอดได้ในอนาคต)**

* ตรวจจับเสียงหรือวิดีโอ Deepfake
* ตรวจจับเว็บไซต์ Phishing จาก URL หรือหน้าเว็บ
* ตรวจจับธุรกรรมการเงินที่ผิดปกติ (Fraud Detection)
""")

# ----------------------------------------------------
# 5. เชื่อมโยงกับสถานการณ์ธนาคาร
# ----------------------------------------------------
st.markdown("""
<div class="card">
    <h3>5. ถ้านำไปใช้ในธนาคาร จะช่วยอะไรได้</h3>
    <div class="grid">
        <div class="tile">
            <div class="tile-tag" style="color:#FF4B4B;">DDoS</div>
            <div class="tile-title">แอปธนาคารล่มช่วงเงินเดือนออก</div>
            <div class="tile-desc">ระบบแจ้งเตือนตั้งแต่ทราฟฟิกเริ่มผิดปกติ ทีมงานเปิด Rate Limiting ได้ก่อนลูกค้าทั้งประเทศใช้งานไม่ได้</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#FFA800;">PORT SCAN</div>
            <div class="tile-title">สัญญาณเตือนก่อนการเจาะระบบ</div>
            <div class="tile-desc">การสแกนพอร์ตมักเป็นขั้นตอนแรกของการโจมตี ถ้าจับได้เร็ว ก็ปิดช่องโหว่ได้ก่อนถูกเจาะจริง</div>
        </div>
        <div class="tile">
            <div class="tile-tag" style="color:#A855F7;">BRUTE FORCE</div>
            <div class="tile-title">ปกป้องบัญชีผู้ดูแลระบบ</div>
            <div class="tile-desc">ล็อกบัญชีและบังคับใช้ MFA ทันทีที่พบการสุ่มรหัสผ่าน ลดโอกาสที่แฮกเกอร์จะเข้าถึงระบบหลังบ้าน</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 6. วิธีป้องกันตัวเองสำหรับคนทั่วไป
# ----------------------------------------------------
with st.expander("🧑‍💻 วิธีป้องกันตัวเองจากการหลอกลวงด้วย AI สำหรับคนทั่วไป"):
    st.markdown("""
    1. **ได้รับสายขอเงินด่วน แม้เสียงจะเหมือนคนรู้จัก ให้วางสายแล้วโทรกลับเบอร์เดิมที่บันทึกไว้เอง**
    2. **ตั้ง "คำลับ" ในครอบครัว** ไว้ถามยืนยันตัวตนเวลามีเหตุฉุกเฉินเรื่องเงิน
    3. **เปิดใช้การยืนยันตัวตนสองชั้น (MFA)** กับแอปธนาคาร อีเมล และโซเชียลมีเดีย
    4. **ตรวจสอบ URL ทุกครั้งก่อนกรอกรหัสผ่าน** และไม่กดลิงก์จาก SMS ที่อ้างว่าเป็นธนาคาร
    5. **ธนาคารไม่มีนโยบายขอรหัส OTP ทางโทรศัพท์** ถ้ามีคนขอ ให้สันนิษฐานว่าเป็นมิจฉาชีพ
    """)

# ----------------------------------------------------
# 7. สรุป
# ----------------------------------------------------
st.markdown("""
<div class="card">
    <h3>6. สรุป : นี่เป็นไอเดียที่ดีหรือไม่</h3>
    <p>
        การเริ่มศึกษาจากฝั่ง <b>ฝ่ายป้องกัน</b> เป็นจุดเริ่มต้นที่ดี เพราะแม้มินิโปรเจกต์นี้จะเล็ก
        แต่ใช้หลักการเดียวกับระบบที่องค์กรจริงใช้ คือ <b>เรียนรู้พฤติกรรมปกติ แล้วแจ้งเตือนเมื่อมีสิ่งผิดปกติ</b>
        และสามารถต่อยอดไปสู่การตรวจจับ Deepfake หรือธุรกรรมฉ้อโกงได้ในอนาคต
    </p>
    <div class="quote">
        "แฮกเกอร์ใช้ AI ทำให้การโจมตีเร็วขึ้นและแนบเนียนขึ้น ฝ่ายป้องกันจึงต้องใช้ AI ช่วยมองเห็นสิ่งผิดปกติให้เร็วพอๆ กัน
        โปรเจกต์นี้คือก้าวแรกของผมในการทำความเข้าใจโลกของฝ่ายป้องกัน"
    </div>
</div>
""", unsafe_allow_html=True)

