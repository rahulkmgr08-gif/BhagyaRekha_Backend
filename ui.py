import streamlit as st
import requests

# पेज की शुरुआती सेटिंग (मोबाइल जैसा लुक देने के लिए)
st.set_page_config(page_title="BhagyaRekha - Home", page_icon="✨", layout="centered")

# स्टाइलिंग (आध्यात्मिक और प्रीमियम लुक के लिए CSS)
st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #FF9933; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #888888; text-align: center; margin-bottom: 30px; }
    .horoscope-card { background-color: #1E1E2F; padding: 20px; border-radius: 15px; border-left: 5px solid #FF9933; margin-top: 20px; }
    .wallet-box { background-color: #2D2D44; padding: 10px 15px; border-radius: 10px; text-align: right; font-weight: bold; color: #00FFCC; }
    </style>
""", unsafe_allow_html=True)

# ऐप का लोगो और हेडर
st.markdown("<div class='main-title'>✨ BhagyaRekha ✨</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>आपकी किस्मत, आपकी रेखाएं</div>", unsafe_allow_html=True)

# Streamlit में स्टेट मैनेजमेंट (ताकि लॉगिन के बाद स्क्रीन बदल सके)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- स्क्रीन 1: लॉगिन / साइनअप स्क्रीन ---
if not st.session_state.logged_in:
    st.subheader("🔮 अपना अकाउंट बनाएं (Signup)")
    
    with st.form("signup_form"):
        name = st.text_input("👤 आपका पूरा नाम (Full Name)", placeholder="जैसे: Sangeeta Kumari")
        phone_number = st.text_input("📞 आपका मोबाइल नंबर (Phone Number)", placeholder="जैसे: 9876543210")
        birth_date = st.date_input("📅 जन्म तिथि (Birth Date)", min_value=None)
        birth_time = st.text_input("⏰ जन्म का समय (Birth Time)", placeholder="जैसे: 02:45 PM")
        birth_place = st.text_input("📍 जन्म का स्थान (Birth Place)", placeholder="जैसे: Noida")
        
        submit_button = st.form_submit_button(label="✨ भाग्य की रेखाएं देखें (Enter App)")

    if submit_button:
        if not name or not phone_number or not birth_place or not birth_time:
            st.error("⚠️ कृपया अपनी पूरी डिटेल्स ध्यान से भरें!")
        else:
            LIVE_BACKEND_URL = "https://bhagyarekha-backend.onrender.com/register_user"
            payload = {
                "name": name,
                "phone_number": phone_number,
                "birth_date": str(birth_date),
                "birth_time": birth_time,
                "birth_place": birth_place
            }
            
            with st.spinner("क्लाउड सर्वर से जुड़ रहे हैं..."):
                try:
                    response = requests.post(LIVE_BACKEND_URL, json=payload)
                    if response.status_code == 200:
                        st.session_state.user_data = response.json()
                        st.session_state.logged_in = True
                        st.balloons()
                        st.rerun() # स्क्रीन को तुरंत रीलोड करके होम पेज पर ले जाएगा
                    else:
                        st.error(f"❌ सर्वर एरर: {response.json().get('detail', 'Unknown Error')}")
                except Exception as e:
                    st.error(f"🔌 कनेक्ट नहीं हो पाए: {str(e)}")

# --- स्क्रीन 2: होम स्क्रीन (लॉगिन के बाद) ---
else:
    user = st.session_state.user_data
    user_name = user.get('name', 'User')
    
    # टॉप बार: स्वागत संदेश और लाइव वॉलेट बैलेंस
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 🪐 नमस्ते, {user_name} जी!")
    with col2:
        st.markdown(f"<div class='wallet-box'>👛 ₹{user.get('wallet_balance', 0.0)}</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    # राशिफल सेक्शन (कल रात वाली API को लाइव कॉल करना)
    st.subheader("📆 आपका आज का राशिफल (Daily Horoscope)")
    
    # टेस्टिंग के लिए हम मान लेते हैं कि यूजर की राशिफल ID 2 है, आगे इसे डायनामिक करेंगे
    HOROSCOPE_URL = "https://bhagyarekha-backend.onrender.com/get_horoscope/2"
    
    with st.spinner("सितारों की गणना की जा रही है..."):
        try:
            horo_response = requests.get(HOROSCOPE_URL)
            if horo_response.status_code == 200:
                horo_data = horo_response.json()
                
                # सुंदर कार्ड में राशिफल दिखाना
                st.markdown(f"""
                    <div class='horoscope-card'>
                        <h4 style='color: #FF9933; margin-top:0;'>🌟 राशि: {horo_data.get('rashi_name', 'Unknown')}</h4>
                        <p style='color: #E0E0E0; font-size: 16px; line-height: 1.6;'>
                            <b>आज का प्रेडिक्शन:</b><br>{horo_data.get('prediction', 'Prediction not available')}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ राशिफल लोड नहीं हो पाया, लेकिन आपका अकाउंट सुरक्षित है।")
        except Exception:
            st.warning("🔌 राशिफल सर्वर से कनेक्ट नहीं हो पाया।")
            
    st.write("")
    st.write("---")
    
    # मुख्य फीचर्स के बटन (अभी सिर्फ डिज़ाइन के लिए)
    st.subheader("🔮 हमारी मुख्य सेवाएं")
    c1, c2 = st.columns(2)
    with c1:
        st.button("💬 ज्योतिषी से चैट करें (₹19/min)", use_container_width=True)
    with c2:
        st.button("✋ हाथ की रेखाएं स्कैन करें (AI)", use_container_width=True)
        
    # लॉगआउट बटन
    if st.button("🚪 लॉगआउट करें", type="secondary"):
        st.session_state.logged_in = False
        st.rerun()