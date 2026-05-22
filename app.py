from supabase import create_client, Client
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# 1. Supabase कनेक्शन सेटिंग्स
url: str = "https://tqtjnfcqjkjkpuohecgu.supabase.co"  
key: str = "sb_publishable_tNnZffaa-thTX1SSDr7G9w_1iXJjzEI"  

# क्लाउड डेटाबेस से कनेक्शन चालू करें
supabase: Client = create_client(url, key)

# 2. 🔑 यहाँ अपनी असली Gemini API Key पेस्ट करें (Google AI Studio वाली)
GEMINI_API_KEY = "AIzaSyA_EmO5lhzeJWcf66EzQuCI0EqEGhlBaYo"  # <-- "AIzaSy..." वाली अपनी असली चाबी यहाँ डालें

# जेमिनी एआई को कॉन्फ़िगर करना
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI को शुरू करना
app = FastAPI()

# CORS Settings (ताकि Streamlit फ्रंटएंड बिना किसी एरर के कनेक्ट हो सके)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- डेटा का ढांचा (Schemas / Pydantic Models) ---

class UserRegister(BaseModel):
    name: str
    phone_number: str
    birth_date: str  # Format: YYYY-MM-DD
    birth_time: str  # Format: HH:MM:SS
    birth_place: str

class WalletRecharge(BaseModel):
    user_id: int
    amount: float  
    description: str = "Wallet Recharge via Gateway"

class ChatDeduction(BaseModel):
    user_id: int
    chat_cost: float = 19.00  

class ChatMessage(BaseModel):
    user_message: str
    user_name: str

class SendMessage(BaseModel):
    user_id: int
    sender: str  # 'USER' या 'ASTROLOGER'
    message_text: str


# --- सभी लाइव API एंडपॉइंट्स (Endpoints) ---

@app.get("/")
def home():
    return {"message": "Welcome to BhagyaRekha Backend is Live with Gemini AI!"}


# 1. यूजर रजिस्टर करने की लाइव API (Supabase)
@app.post("/register_user")
def register_user(user: UserRegister):
    try:
        data = supabase.table("users").insert({
            "name": user.name,
            "phone_number": user.phone_number,
            "birth_date": user.birth_date,
            "birth_time": user.birth_time,
            "birth_place": user.birth_place,
            "wallet_balance": 50.00,       # नया यूजर ₹50 फ्री बैलेंस से शुरू होगा
            "is_first_chat_free": True     # पहली चैट फ्री रहेगी
        }).execute()
        
        # फ्रंटएंड को सीधे यूजर डेटा भेजने के लिए ताकि एरर न आए
        return {
            "status": "Success", 
            "message": "User registered successfully!", 
            "wallet_balance": 50.00,
            "name": user.name,
            "data": data.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 2. वॉलेट रिचार्ज करने की लाइव API (Supabase)
@app.post("/recharge_wallet")
def recharge_wallet(recharge: WalletRecharge):
    try:
        user_data = supabase.table("users").select("wallet_balance").eq("user_id", recharge.user_id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found!")
            
        current_balance = float(user_data.data[0]["wallet_balance"])
        new_balance = current_balance + recharge.amount
        
        supabase.table("users").update({"wallet_balance": new_balance}).eq("user_id", recharge.user_id).execute()
        
        supabase.table("wallet_transactions").insert({
            "user_id": recharge.user_id,
            "amount": recharge.amount,
            "transaction_type": "RECHARGE",
            "description": recharge.description
        }).execute()
        
        return {
            "status": "Success",
            "message": f"An amount of ₹{recharge.amount} successfully added!",
            "new_balance": new_balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 3. चैट डिडक्शन (पैसे कटने या फ्री चेक करने) की लाइव API (Supabase)
@app.post("/start_chat")
def start_chat(chat: ChatDeduction):
    try:
        user_data = supabase.table("users").select("wallet_balance", "is_first_chat_free").eq("user_id", chat.user_id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found!")
            
        user_record = user_data.data[0]
        current_balance = float(user_record["wallet_balance"])
        is_free = user_record["is_first_chat_free"]
        
        if is_free:
            supabase.table("users").update({"is_first_chat_free": False}).eq("user_id", chat.user_id).execute()
            
            supabase.table("wallet_transactions").insert({
                "user_id": chat.user_id,
                "amount": 0.00,
                "transaction_type": "CONSULTATION",
                "description": "First Chat Free Promo availed"
            }).execute()
            
            return {
                "status": "Success",
                "message": "Chat started for FREE! First chat promotion applied.",
                "wallet_balance": current_balance
            }
            
        else:
            if current_balance < chat.chat_cost:
                raise HTTPException(
                    status_code=400,  
                    detail=f"Insufficient balance! Chat costs ₹{chat.chat_cost}. Please recharge."
                )
                
            new_balance = current_balance - chat.chat_cost
            supabase.table("users").update({"wallet_balance": new_balance}).eq("user_id", chat.user_id).execute()
            
            supabase.table("wallet_transactions").insert({
                "user_id": chat.user_id,
                "amount": -chat.chat_cost, 
                "transaction_type": "CONSULTATION",
                "description": f"Paid Chat Consultation fee of ₹{chat.chat_cost}"
            }).execute()
            
            return {
                "status": "Success",
                "message": "Chat started successfully!",
                "new_balance": new_balance
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 📆 राशि और प्रेडिक्शन निकालने का मददगार फंक्शन
def get_zodiac_and_prediction(birth_date_str: str):
    try:
        parts = birth_date_str.split("-")
        month = int(parts[1])
        day = int(parts[2])
    except:
        return "Unknown", "अपनी बर्थ डेट का फॉर्मेट सही करें।"

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        sign = "Mesh (Aries)"
        pred = "आज का दिन आपके लिए नई ऊर्जा लेकर आएगा। व्यापार में लाभ के योग हैं।"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        sign = "Vrishabha (Taurus)"
        pred = "आर्थिक स्थिति मजबूत होगी। परिवार के साथ अच्छा समय बीतेगा"
