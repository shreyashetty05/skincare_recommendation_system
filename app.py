import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from mtcnn.mtcnn import MTCNN
import google.generativeai as genai

# --- Model Loading ---
try:
    model = load_model('skin_type_model.h5')
    print("Skin type classification model loaded successfully!")
    detector = MTCNN()
    print("Face detection model (MTCNN) loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    detector = None

CLASS_NAMES = ['Combination', 'Dry', 'Normal', 'Oily', 'Sensitive']

# --- Gemini Configuration ---
genai.configure(api_key="AIzaSyAWPIh-l0frWlUFUye5pSMb7zxY-yE4AhA")
gemini_model = genai.GenerativeModel('gemini-flash-latest')

app = Flask(__name__)

# --- EXPANDED PRODUCT DATABASE WITH STATIC LINKS FOR ALL CATEGORIES ---
product_database = {
    "Oily": {
        "cleanser": {
            "name": "CeraVe Foaming Cleanser", "description": "Helps control excess oil and unclog pores without over-drying.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/cerave-foaming-cleanser/p/10668065"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/CeraVe-Foaming-Cleanser-Normal-Oily/dp/B003Y3CJEQ"}
            ]
        },
        "serum": {
            "name": "The Ordinary Niacinamide 10% + Zinc 1%", "description": "Reduces blemishes, redness, and enlarged pores.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/the-ordinary-niacinamide-10-zinc-1/p/5003157"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Ordinary-Niacinamide-10-Zinc-30ml/dp/B01N2V4B2Z"}
            ]
        },
        "moisturizer": {
            "name": "Neutrogena Hydro Boost Water Gel", "description": "Provides oil-free hydration that won't feel heavy or greasy.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/neutrogena-hydro-boost-water-gel/p/23547"},
                {"retailer": "Flipkart", "url": "https://www.flipkart.com/neutrogena-hydro-boost-water-gel-fresh-stock/p/itmf8b58a12e8b0a"}
            ]
        },
        "sunscreen": {
            "name": "La Roche-Posay Anthelios UVMUNE 400", "description": "Protects from the sun with a non-shiny, mattifying effect.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/la-roche-posay-anthelios-uvmune-400-oil-control-fluid-spf50/p/10668078"},
                {"retailer": "Apollo Pharmacy", "url": "https://www.apollopharmacy.in/otc/la-roche-posay-anthelios-invisible-fluid-spf-50-50ml"}
            ]
        }
    },
    "Dry": {
        "cleanser": {
            "name": "Cetaphil Gentle Skin Cleanser", "description": "Gently cleanses while replenishing moisture.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/cetaphil-gentle-skin-cleanser/p/27597"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Cetaphil-Gentle-Skin-Cleanser-125ml/dp/B01CCGWG3C"}
            ]
        },
        "moisturizer": {
            "name": "CeraVe Moisturising Cream", "description": "A thick, nourishing cream to restore the skin's moisture barrier.",
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/cerave-moisturising-cream-for-dry-to-very-dry-skin/p/10668060"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/CeraVe-Moisturizing-Cream-Daily-Moisturizer/dp/B00TTD9BRC"}
            ]
        },
        "serum": {
            "name": "L'Oréal Paris Revitalift 1.5% Hyaluronic Acid Serum", "description": "Attracts moisture to the skin for multi-depth hydration.",
             "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/l-oreal-paris-revitalift-1-5-hyaluronic-acid-serum/p/1013498"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/LOr%C3%A9al-Paris-Revitalift-Hyaluronic-variant/dp/B086384B9H"}
            ]
        },
        "sunscreen": {
             "name": "Minimalist Sunscreen SPF 50", "description": "Protects and provides a radiant, moisturized finish.",
             "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/minimalist-spf-50-pa-sunscreen-for-all-skin-types/p/1927708"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Minimalist-Sunscreen-SPF-PA-Multi-Vitamin/dp/B09152298P"}
            ]
        }
    },
    "Combination": {
        "cleanser": {
            "name": "Simple Kind to Skin Refreshing Facial Wash", 
            "description": "Cleanses thoroughly without stripping.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/simple-kind-to-skin-refreshing-facial-wash/p/349484"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Simple-Kind-Skin-Refreshing-Facial/dp/B078G65L31"}
            ]
        },
        "serum": {
            "name": "The Ordinary Hyaluronic Acid 2% + B5", 
            "description": "Provides balanced hydration to all areas.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/the-ordinary-hyaluronic-acid-2-b5/p/5003164"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Ordinary-Hyaluronic-Acid-B5-30ml/dp/B07N71B2T4"}
            ]
        },
        "moisturizer": {
            "name": "Ponds Super Light Gel Moisturiser", 
            "description": "A lightweight cream that hydrates dry patches.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/ponds-super-light-gel-oil-free-moisturiser-with-hyaluronic-acid-vitamin-e/p/579340"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Ponds-Super-Light-Moisturiser-73/dp/B07J342555"}
            ]
        },
        "sunscreen": {
            "name": "Re'equil Ultra Matte Dry Touch Sunscreen", 
            "description": "A non-greasy formula suitable for all areas.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/re-equil-ultra-matte-dry-touch-sunscreen-gel-spf-50-pa/p/406856"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/RE-EQUIL-Ultra-Matte-Touch-Sunscreen/dp/B079Z51X6H"}
            ]
        }
    },
    "Normal": {
        "cleanser": {
            "name": "Kiehl's Ultra Facial Cleanser", 
            "description": "A gentle cleanser that removes impurities effectively.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/kiehl-s-ultra-facial-cleanser/p/2623"}, 
                {"retailer": "Kiehls.in", "url": "https://kiehls.in/ultra-facial-cleanser.html"}
            ]
        },
        "serum": {
            "name": "Minimalist Vitamin C 10% Serum", 
            "description": "An antioxidant serum to improve radiance.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/minimalist-10-vitamin-c-face-serum-for-glowing-skin/p/1154291"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Minimalist-Vitamin-Face-Serum-Women/dp/B08P121SY8"}
            ]
        },
        "moisturizer": {
            "name": "Clinique Moisture Surge 100H", 
            "description": "A non-greasy cream that offers surface hydration.",
             "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/clinique-moisture-surge-100h-auto-replenishing-hydrator/p/2436735"}, 
                {"retailer": "Sephora.in", "url": "https://sephora.in/product/clinique-moisture-surge-100h-auto-replenishing-hydrator-15ml"}
            ]
        },
        "sunscreen": {
            "name": "Supergoop! Unseen Sunscreen SPF 40", 
            "description": "Provides broad-spectrum protection with a natural finish.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/supergoop-unseen-sunscreen-spf-40/p/10668085"}
            ]
        }
    },
    "Sensitive": {
        "cleanser": {
            "name": "Avene Tolerance Extremely Gentle Cleanser", 
            "description": "A soap-free, no-rinse cleanser that soothes and calms.", 
            "links": [
                {"retailer": "CareToBeauty", "url": "https://www.caretobeauty.com/in/avene-tolerance-extremely-gentle-cleanser-400ml/"},
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Avene-Tolerance-Extremely-Gentle-Cleanser/dp/B01N0683L7"}
            ]
        },
        "serum": {
            "name": "La Roche-Posay Cicaplast B5 Serum", 
            "description": "Reduces redness and irritation while strengthening the barrier.", 
            "links": [
                {"retailer": "CareToBeauty", "url": "https://www.caretobeauty.com/in/la-roche-posay-cicaplast-b5-serum-30ml/"}
            ]
        },
        "moisturizer": {
            "name": "Aveeno Calm + Restore Oat Gel Moisturizer", 
            "description": "A calming, nourishing cream designed to reduce redness.", 
            "links": [
                {"retailer": "Nykaa", "url": "https://www.nykaa.com/aveeno-calm-restore-oat-gel-moisturizer/p/12345678"}, 
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/Aveeno-Restore-Moisturizer-Prebiotic-Lightweight/dp/B08D43G11L"}
            ]
        },
        "sunscreen": {
            "name": "ISDIN Eryfotona Actinica Mineral Sunscreen", 
            "description": "A gentle, non-irritating 100% mineral formula.",
             "links": [
                {"retailer": "Amazon.in", "url": "https://www.amazon.in/ISDIN-Eryfotona-Actinica-Sunscreen-Fluid/dp/B00L2K5L1I"},
                {"retailer": "Ubuy.co.in", "url": "https://www.ubuy.co.in/product/14N88T-isdin-eryfotona-actinica-zinc-oxide-and-100-mineral-sunscreen-broad-spectrum-spf-50-zinc-oxide-facial-sunscreen-3-4-fl-oz"}
            ]
        }
    }
}


def analyze_skin_type(image_bytes):
    if model is None or detector is None: return "Model not loaded"
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(image_rgb)
        if not faces: return "No person detected"
        img_resized = cv2.resize(image_bgr, (150, 150))
        img_rgb_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_array = np.array(img_rgb_resized) / 255.0
        image_batch = np.expand_dims(img_array, axis=0)
        predictions = model.predict(image_batch)
        predicted_index = np.argmax(predictions[0])
        predicted_class = CLASS_NAMES[predicted_index]
        return predicted_class
    except Exception as e:
        print(f"Error during image prediction: {e}")
        return None

# --- Routes ---
@app.route('/')
def homepage(): return render_template('homepage.html')

@app.route('/analyze')
def index(): return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files: return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({'error': 'No image selected'}), 400

    if file:
        image_bytes = file.read()
        skin_type = analyze_skin_type(image_bytes)
        if skin_type is None: return jsonify({'error': 'Could not analyze image'}), 500
        if skin_type == "No person detected": return jsonify({'error': 'No person detected. Please ensure your face is clearly visible.'}), 400
        
        recommendations = product_database.get(skin_type, {})
        
        # --- Gemini AI Suggestions ---
        ai_suggestions = "<li>Drink plenty of water!</li><li>Wear sunscreen daily.</li>" # Fallback
        try:
            prompt = f"The user has {skin_type} skin. Provide 3 short, punchy lifestyle or habit tips to improve their skin health. Return ONLY 3 bullet points wrapped in HTML <li> tags. Do not include <ul> tags."
            response = gemini_model.generate_content(prompt)
            if response.text:
                ai_suggestions = response.text
        except Exception as e:
            print(f"Gemini Suggestion Error: {e}")
        
        # MODIFIED: Directly use the links from our database
        enriched_recommendations = {}
        for category, product_info in recommendations.items():
            enriched_recommendations[category] = {
                "name": product_info.get('name', 'N/A'),
                "description": product_info.get('description', ''),
                "links": product_info.get('links', []) # Get links from the database
            }
            
        return jsonify({ 
            'skin_type': skin_type, 
            'recommendations': enriched_recommendations,
            'ai_suggestions': ai_suggestions 
        })


# --- Chatbot Endpoint ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': "I didn't catch that. Could you please repeat?"})

    try:
        # Contextual Prompt for the AI
        system_context = (
            "You are SkinWise, an expert AI dermatologist assistant. "
            "You provide helpful, safe, and concise advice about skincare, skin types (Oily, Dry, Normal, Combination, Sensitive), "
            "and products (Cleansers, Serums, Moisturizers, Sunscreens). "
            "If asked about medical conditions, advise visiting a doctor. "
            "Keep answers friendly and under 3 sentences if possible."
        )
        
        # specific prompt construction
        full_prompt = f"{system_context}\n\nUser: {user_message}\nSkinWise:"
        
        response = gemini_model.generate_content(full_prompt)
        bot_reply = response.text
        
        # Fallback if empty
        if not bot_reply:
            bot_reply = "I'm having a little trouble thinking right now. Ask me again in a moment!"
            
    except Exception as e:
        print(f"Gemini API Error: {e}")
        bot_reply = "I'm currently offline (API Error). Please try again later."

    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    app.run(debug=True)

