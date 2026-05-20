import streamlit as st
import requests

# पेज की शुरुआती सेटिंग (मोबाइल जैसा लुक)
st.set_page_config(page_title="BhagyaRekha - App", page_icon="✨", layout="centered")

# स्टाइलिंग (एस्ट्रोलॉजी थीम)
st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #FF9933; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #888888; text-align: center; margin-bottom: 30px; }
    .horoscope-card { background-color: #1E1E2F; padding: 20px; border-radius: 15px; border-left: 5px solid #FF9933; margin-top: 20px; }
    .wallet-box { background-color: #2D2D44; padding: 10px 15px; border-radius: 10px; text-align: right; font-weight: bold; color: #00FFCC; }
    .chat-bubble-user { background-color: #0B8043; padding: 10px 15px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; color: white; }
    .chat-bubble-astro { background-color: #2D2D44; padding: 10px 15px; border-radius: 15px 15px 15px 0px; margin: 10px 0; text-align: left; color: white; border-left: 3px solid #FF9933; }
    </style>
""", unsafe_allow_html=True)

# 1. सेशन्स को मैनेज करना (State Management)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "signup" # (signup, home, chat)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "astro", "message": "प्रणाम! मैं आचार्य आनंद। आज आपके सितारे क्या कहते हैं? अपना सवाल पूछें। 🙏"}
    ]

# हेडर हर पेज पर दिखेगा
st.markdown("<div class='main-title'>✨ BhagyaRekha ✨</div>", unsafe_allow_html=True)

# --- स्क्रीन 1: साइनअप स्क्रीन ---
if st.session_state.current_page == "signup" and not st.session_state.logged_in:
    st.markdown("<div class='sub-title'>अपनी किस्मत की लकीरों को पहचानें</div>", unsafe_allow_html=True)
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
            payload = {"name": name, "phone_number": phone_number, "birth_date": str(birth_date), "birth_time": birth_time, "birth_place": birth_place}
            
            with st.spinner("क्लाउड सर्वर से जुड़ रहे हैं..."):
                try:
                    response = requests.post(LIVE_BACKEND_URL, json=payload)
                    if response.status_code == 200:
                        st.session_state.user_data = response.json()
                        st.session_state.logged_in = True
                        st.session_state.current_page = "home"
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ सर्वर एरर: {response.json().get('detail', 'Unknown Error')}")
                except Exception as e:
                    st.error(f"🔌 कनेक्ट नहीं हो पाए: {str(e)}")

# --- स्क्रीन 2: होम स्क्रीन (लॉगिन के बाद) ---
elif st.session_state.current_page == "home":
    user = st.session_state.user_data
    user_name = user.get('name', 'User')
    
    # टॉप बार: नाम और वॉलेट
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 🪐 नमस्ते, {user_name} जी!")
    with col2:
        st.markdown(f"<div class='wallet-box'>👛 ₹{user.get('wallet_balance', 50.0)}</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    # आज का राशिफल
    st.subheader("📆 आपका आज का राशिफल")
    HOROSCOPE_URL = "https://bhagyarekha-backend.onrender.com/get_horoscope/2"
    
    with st.spinner("सितारों की गणना की जा रही है..."):
        try:
            horo_response = requests.get(HOROSCOPE_URL)
            if horo_response.status_code == 200:
                horo_data = horo_response.json()
                st.markdown(f"""
                    <div class='horoscope-card'>
                        <h4 style='color: #FF9933; margin-top:0;'>🌟 राशि: {horo_data.get('rashi_name', 'Mesh')}</h4>
                        <p style='color: #E0E0E0; font-size: 16px;'>{horo_data.get('prediction', 'आज का दिन आपके लिए शुभ रहेगा।')}</p>
                    </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.warning("⚠️ राशिफल लोड नहीं हो पाया।")
            
    st.write("---")
    
    # मुख्य सेवाएं (अब बटन काम करेंगे)
    st.subheader("🔮 हमारी मुख्य सेवाएं")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 ज्योतिषी से चैट करें (₹19/min)", use_container_width=True, type="primary"):
            st.session_state.current_page = "chat"
            st.rerun()
    with c2:
        st.button("✋ हाथ की रेखाएं स्कैन करें", use_container_width=True, disabled=True)
        
    if st.button("🚪 लॉगआउट करें", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.current_page = "signup"
        st.rerun()

# --- स्क्रीन 3: लाइव चैट स्क्रीन ---
elif st.session_state.current_page == "chat":
    user = st.session_state.user_data
    
    # चैट स्क्रीन का हेडर
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("⬅️ होम पेज पर जाएं"):
            st.session_state.current_page = "home"
            st.rerun()
    with col2:
        st.markdown(f"<div class='wallet-box'>👛 ₹{user.get('wallet_balance', 50.0)}</div>", unsafe_allow_html=True)
        
    st.subheader("💬 आचार्य आनंद जी से लाइव चैट")
    st.caption("⚡ दर: ₹19/मिनट | आपका फ्री बैलेंस एक्टिव है")
    
    st.write("---")
    
    # पुरानी चैट हिस्ट्री दिखाना
    for chat in st.session_state.chat_history:
        if chat["sender"] == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>आप:</b><br>{chat['message']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-astro'><b>आचार्य जी:</b><br>{chat['message']}</div>", unsafe_allow_html=True)
            
    # नया मैसेज इनपुट करने का बॉक्स
    with st.form("chat_input_form", clear_on_submit=True):
        user_message = st.text_input("अपना सवाल यहाँ टाइप करें...", placeholder="जैसे: मेरी नौकरी कब लगेगी?")
        send_button = st.form_submit_button("पूंछें 🚀")
        
    if send_button and user_message:
        # यूज़र का मैसेज स्क्रीन पर जोड़ना
        st.session_state.chat_history.append({"sender": "user", "message": user_message})
        
        # (अस्थायी तौर पर ज्योतिषी का एक ऑटो-जवाब जोड़ रहे हैं, शाम को इसमें असली AI जोड़ेंगे)
        astro_reply = "आपकी कुंडली में सूर्य मजबूत स्थिति में आ रहा है। थोड़ा धैर्य रखें, जल्द ही शुभ समाचार मिलेगा।"
        st.session_state.chat_history.append({"sender": "astro", "message": astro_reply})
        st.rerun()
