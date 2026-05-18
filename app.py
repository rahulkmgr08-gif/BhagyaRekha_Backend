from supabase import create_client, Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. यहाँ अपनी असली डिटेल्स पेस्ट करें
url: str = "https://tqtjnfcqjkjkpuohecgu.supabase.co"  
key: str = "sb_publishable_tNnZffaa-thTX1SSDr7G9w_1iXJjzEI"  

# क्लाउड डेटाबेस से कनेक्शन चालू करें
supabase: Client = create_client(url, key)



# FastAPI को शुरू करें
app = FastAPI()

# यूजर रजिस्ट्रेशन का ढांचा (डेटा वैलिडेशन के लिए)
class UserRegister(BaseModel):
    name: str
    phone_number: str
    birth_date: str  # Format: YYYY-MM-DD
    birth_time: str  # Format: HH:MM:SS
    birth_place: str

@app.get("/")
def home():
    return {"message": "Welcome to BhagyaRekha Backend is Live!"}

# यूजर रजिस्टर करने की लाइव API
@app.post("/register_user")
def register_user(user: UserRegister):
    try:
        data = supabase.table("users").insert({
            "name": user.name,
            "phone_number": user.phone_number,
            "birth_date": user.birth_date,
            "birth_time": user.birth_time,
            "birth_place": user.birth_place,
            "wallet_balance": 0.00,        # नया यूजर 0 बैलेंस से शुरू होगा
            "is_first_chat_free": True     # पहली चैट फ्री रहेगी
        }).execute()
        
        return {"status": "Success", "message": "User registered successfully!", "data": data.data}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # वॉलेट रिचार्ज के लिए डेटा का ढांचा
class WalletRecharge(BaseModel):
    user_id: int
    amount: float  # जैसे: 19.00 या 49.00
    description: str = "Wallet Recharge via Gateway"

# 3. वॉलेट रिचार्ज करने की लाइव API
@app.post("/recharge_wallet")
def recharge_wallet(recharge: WalletRecharge):
    try:
        # 1. पहले चेक करें कि क्या यह यूजर सच में डेटाबेस में है?
        user_data = supabase.table("users").select("wallet_balance").eq("user_id", recharge.user_id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found!")
            
        current_balance = float(user_data.data[0]["wallet_balance"])
        new_balance = current_balance + recharge.amount
        
        # 2. 'users' table में बैलेंस को अपडेट (Update) करें
        supabase.table("users").update({"wallet_balance": new_balance}).eq("user_id", recharge.user_id).execute()
        
        # 3. 'wallet_transactions' table में इस रिचार्ज की हिस्ट्री (Log) सेव करें
        supabase.table("wallet_transactions").insert({
            "user_id": recharge.user_id,
            "amount": recharge.amount,
            "transaction_type": "RECHARGE",
            "description": recharge.description
        }).execute()
        
        return {
            "status": "Success",
            "message": f"₹{recharge.amount} successfully added to wallet!",
            "new_balance": new_balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # चैट शुरू करने के लिए रिक्वेस्ट का ढांचा
class ChatDeduction(BaseModel):
    user_id: int
    chat_cost: float = 19.00  # डिफ़ॉल्ट चैट की कीमत ₹19 मान लेते हैं

# 4. चैट डिडक्शन (पैसे कटने या फ्री चेक करने) की लाइव API
@app.post("/start_chat")
def start_chat(chat: ChatDeduction):
    try:
        # 1. यूज़र का मौजूदा डेटाबेस रिकॉर्ड निकालें
        user_data = supabase.table("users").select("wallet_balance", "is_first_chat_free").eq("user_id", chat.user_id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found!")
            
        user_record = user_data.data[0]
        current_balance = float(user_record["wallet_balance"])
        is_free = user_record["is_first_chat_free"]
        
        # लॉजिक PART A: अगर पहली चैट फ्री है
        if is_free:
            # बैलेंस नहीं कटेगा, बस फ्री फ्लैग को FALSE कर देंगे
            supabase.table("users").update({"is_first_chat_free": False}).eq("user_id", chat.user_id).execute()
            
            # ट्रांजैक्शन हिस्ट्री में रिकॉर्ड दर्ज करें (₹0 का ट्रैक)
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
            
        # लॉजिक PART B: अगर पहली चैट फ्री नहीं है (यानी पहले यूज़ हो चुकी है)
        else:
            # चेक करें कि क्या यूज़र के पास पर्याप्त बैलेंस है?
            if current_balance < chat.chat_cost:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient balance! Chat costs ₹{chat.chat_cost}, but your balance is ₹{current_balance}. Please recharge."
                )
                
            # बैलेंस डिडक्ट करें
            new_balance = current_balance - chat.chat_cost
            supabase.table("users").update({"wallet_balance": new_balance}).eq("user_id", chat.user_id).execute()
            
            # ट्रांजैक्शन हिस्ट्री में रिकॉर्ड दर्ज करें
            supabase.table("wallet_transactions").insert({
                "user_id": chat.user_id,
                "amount": -chat.chat_cost, # माइनस साइन ताकि पता चले पैसे कटे हैं
                "transaction_type": "CONSULTATION",
                "description": f"Paid Chat Consultation fee of ₹{chat.chat_cost}"
            }).execute()
            
            return {
                "status": "Success",
                "message": f"₹{chat.chat_cost} deducted. Chat started successfully!",
                "new_balance": new_balance
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # राशि और प्रेडिक्शन निकालने का एक मददगार फंक्शन (Helper Function)
def get_zodiac_and_prediction(birth_date_str: str):
    # birth_date_str का फॉर्मेट: YYYY-MM-DD (जैसे: 1995-05-15)
    try:
        parts = birth_date_str.split("-")
        month = int(parts[1])
        day = int(parts[2])
    except:
        return "Unknown", "अपनी बर्थ डेट का फॉर्मेट सही करें।"

    # महीनों और दिनों के आधार पर राशि का निर्धारण
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        sign = "Aries (मेष)"
        pred = "आज का दिन आपके लिए नई ऊर्जा लेकर आएगा। व्यापार में लाभ के योग हैं।"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        sign = "Taurus (वृषभ)"
        pred = "आर्थिक स्थिति मजबूत होगी। परिवार के साथ अच्छा समय बीतेगा, धैर्य बनाए रखें।"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        sign = "Gemini (मिथुन)"
        pred = "वाणी पर संयम रखें। नए मित्र बन सकते हैं जो भविष्य में मददगार होंगे।"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        sign = "Cancer (कर्क)"
        pred = "भावुकता में कोई बड़ा फैसला न लें। नौकरी में तरक्की के नए रास्ते खुलेंगे।"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        sign = "Leo (सिंह)"
        pred = "नेतृत्व क्षमता बढ़ेगी। समाज में मान-सम्मान मिलेगा। सेहत का ध्यान रखें।"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        sign = "Virgo (कन्या)"
        pred = "रुके हुए काम पूरे होंगे। धन लाभ की स्थिति बन रही है। यात्रा के योग हैं।"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        sign = "Libra (तुला)"
        pred = "जीवन में संतुलन बनाने का समय है। कानूनी मामलों में सफलता मिल सकती है।"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        sign = "Scorpio (वृश्चिक)"
        pred = "रहस्यमयी चीज़ों के प्रति झुकाव बढ़ेगा। मेहनत का पूरा फल आज आपको मिलेगा।"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        sign = "Sagittarius (धनु)"
        pred = "लंबे समय से सोचे हुए काम पूरे होंगे। भाग्य का पूरा साथ मिलेगा।"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        sign = "Capricorn (मकर)"
        pred = "करियर में स्थिरता आएगी। वरिष्ठ अधिकारियों से सहयोग मिलेगा।"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        sign = "Aquarius (कुंभ)"
        pred = "नए विचारों से लाभ होगा। सामाजिक कार्यों में रुचि बढ़ेगी।"
    else:
        sign = "Pisces (मीन)"
        pred = "आध्यात्मिक सुख मिलेगा। खर्चों पर थोड़ा नियंत्रण रखने की आवश्यकता है।"

    return sign, pred


# 5. यूज़र की राशि और राशिफल देखने की लाइव API
@app.get("/get_horoscope/{user_id}")
def get_horoscope(user_id: int):
    try:
        # यूज़र की बर्थ डेट डेटाबेस से निकालें
        user_data = supabase.table("users").select("birth_date", "name").eq("user_id", user_id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found!")
            
        birth_date_str = user_data.data[0]["birth_date"]
        user_name = user_data.data[0]["name"]
        
        # राशि और प्रेडिक्शन फंक्शन को कॉल करें
        zodiac_sign, prediction = get_zodiac_and_prediction(birth_date_str)
        
        return {
            "status": "Success",
            "name": user_name,
            "zodiac_sign": zodiac_sign,
            "daily_horoscope": prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # मैसेज भेजने के लिए डेटा का ढांचा
class SendMessage(BaseModel):
    user_id: int
    sender: str  # 'USER' या 'ASTROLOGER'
    message_text: str

# 6. चैट का मैसेज डेटाबेस में सेव करने की API
@app.post("/send_message")
def send_message(msg: SendMessage):
    try:
        data = supabase.table("chat_messages").insert({
            "user_id": msg.user_id,
            "sender": msg.sender,
            "message_text": msg.message_text
        }).execute()
        
        return {"status": "Success", "message": "Message saved successfully!", "data": data.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. पुरानी पूरी चैट हिस्ट्री निकालने की API (Get Chat History)
@app.get("/get_chat_history/{user_id}")
def get_chat_history(user_id: int):
    try:
        # उस यूज़र के सारे मैसेजेस समय के अनुसार (पुराने से नए) निकालें
        data = supabase.table("chat_messages").select("*").eq("user_id", user_id).order("created_at").execute()
        return {"status": "Success", "chat_history": data.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    