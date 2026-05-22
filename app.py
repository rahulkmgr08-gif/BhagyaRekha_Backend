from supabase import create_client, Client
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. Supabase कनेक्शन सेटिंग्स
url: str = "https://tqtjnfcqjkjkpuohecgu.supabase.co"  
key: str = "sb_publishable_tNnZffaa-thTX1SSDr7G9w_1iXJjzEI"  
supabase: Client = create_client(url, key)

# FastAPI को शुरू करना
app = FastAPI()

# CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# डेटा का ढांचा (Schemas)
class UserRegister(BaseModel):
    name: str
    phone_number: str
    birth_date: str  
    birth_time: str  
    birth_place: str

class ChatMessage(BaseModel):
    user_message: str
    user_name: str

@app.get("/")
def home():
    return {"message": "BhagyaRekha Backend is Live without AI!"}

# 1. यूजर रजिस्टर करने की API
@app.post("/register_user")
def register_user(user: UserRegister):
    try:
        data = supabase.table("users").insert({
            "name": user.name,
            "phone_number": user.phone_number,
            "birth_date": user.birth_date,
            "birth_time": user.birth_time,
            "birth_place": user.birth_place,
            "wallet_balance": 50.00,       
            "is_first_chat_free": True     
        }).execute()
        return {"status": "Success", "message": "User registered successfully!", "wallet_balance": 50.00, "name": user.name, "data": data.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. आज का राशिफल देखने की API
@app.get("/get_horoscope/{user_id}")
def get_horoscope(user_id: int):
    return {
        "rashi_name": "Mesh (Aries)",
        "prediction": "आज का दिन आपके लिए नई ऊर्जा लेकर आएगा। आर्थिक स्थिति मजबूत होगी और सोचे हुए काम पूरे होंगे।"
    }

# 🔮 3. नॉर्मल सवालों के सीधे जवाब देने वाली चैट API (NO AI)
@app.post("/chat_with_astrologer")
def chat_with_astrologer(chat: ChatMessage):
    msg = chat.user_message.lower() # छोटे अक्षरों में बदलना ताकि चेकिंग आसान हो
    
    # सवाल: नौकरी (Job) से जुड़ा हो
    if "naukri" in msg or "job" in msg or "career" in msg:
        reply = f"प्रणाम {chat.user_name} जी। आपके ग्रहों की स्थिति बता रही है कि आने वाले 6 महीनों में आपके करियर में बड़ा सुधार होगा। दशम भाव में सूर्य की दृष्टि से सरकारी या अच्छी प्राइवेट नौकरी के मजबूत योग बन रहे हैं। प्रतिदिन सूर्य देव को जल अर्पित करें।"
    
    # सवाल: शादी (Marriage / Saadi) से जुड़ा हो
    elif "saadi" in msg or "shadi" in msg or "marriage" in msg or "wife" in msg:
        reply = f"{chat.user_name} जी, आपकी कुंडली के अनुसार विवाह के मार्ग में आ रही रुकावटें अब दूर हो रही हैं। अगले वर्ष के मध्य तक आपके विवाह के अत्यंत शुभ और मंगलकारी योग बन रहे हैं। गुरुवार के दिन पीले वस्त्र धारण करें, लाभ होगा।"
        
    # सवाल: व्यापार (Business) से जुड़ा हो
    elif "business" in msg or "vyapar" in msg or "kaam" in msg:
        reply = f"{chat.user_name} जी, व्यापार के दृष्टिकोण से समय धीरे-धीरे अनुकूल हो रहा है। साझेदारी (Partnership) के कामों में थोड़ी सावधानी बरतें, परंतु खुद का नया काम शुरू करने के लिए समय बहुत ही उत्तम है।"
        
    # कोई भी अन्य सामान्य सवाल हो
    else:
        reply = f"नमस्ते {chat.user_name} जी। आपका सवाल मुझे प्राप्त हुआ। वर्तमान गोचर के अनुसार आपका भाग्य पक्ष मजबूत है। धैर्य बनाए रखें, आपके जीवन में सुख और समृद्धि के द्वार जल्द ही खुलेंगे। कोई विशेष उपाय जानने के लिए अपना मुख्य प्रश्न दोबारा स्पष्ट लिखें।"

    return {"astro_reply": reply}
