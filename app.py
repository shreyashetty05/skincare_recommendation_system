import os
import random
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io

# Initialize the Flask application
app = Flask(__name__)

# --- Mock Product Database ---
# In a real application, this would likely be in a separate database.
product_database = {
    "Oily": {
        "cleanser": {"name": "Foaming Salicylic Acid Cleanser", "description": "Helps control excess oil and unclog pores without over-drying."},
        "serum": {"name": "Niacinamide 10% + Zinc 1%", "description": "Reduces the appearance of blemishes, redness, and enlarged pores."},
        "moisturizer": {"name": "Lightweight Gel Moisturizer", "description": "Provides oil-free hydration that won't feel heavy or greasy."},
        "sunscreen": {"name": "Matte Finish Mineral Sunscreen SPF 40", "description": "Protects from the sun with a non-shiny, mattifying effect."}
    },
    "Dry": {
        "cleanser": {"name": "Hydrating Cream-to-Foam Cleanser", "description": "Gently cleanses while replenishing moisture with hyaluronic acid."},
        "serum": {"name": "Hyaluronic Acid 2% + B5 Serum", "description": "Attracts moisture to the skin for multi-depth hydration."},
        "moisturizer": {"name": "Rich Barrier Repair Cream", "description": "A thick, nourishing cream to restore the skin's moisture barrier and soothe dryness."},
        "sunscreen": {"name": "Dewy Finish Hydrating Sunscreen SPF 50", "description": "Protects and provides a radiant, moisturized finish."}
    },
    "Combination": {
        "cleanser": {"name": "Gentle Balancing Cleanser", "description": "Cleanses thoroughly without stripping, ideal for both oily and dry areas."},
        "serum": {"name": "Hyaluronic Acid 2% + B5 Serum", "description": "Provides hydration to dry areas without making oily zones greasier."},
        "moisturizer": {"name": "Oil-Free Water Cream", "description": "A lightweight cream that hydrates dry patches while feeling weightless on oily T-zones."},
        "sunscreen": {"name": "Invisible Fluid Sunscreen SPF 50+", "description": "A lightweight, non-greasy formula suitable for all areas of the face."}
    },
     "Normal": {
        "cleanser": {"name": "Squalane Cleanser", "description": "A gentle, moisturizing cleanser that removes makeup and impurities effectively."},
        "serum": {"name": "Vitamin C Brightening Serum", "description": "An antioxidant serum to protect the skin and improve overall radiance."},
        "moisturizer": {"name": "Natural Moisturizing Factors + HA", "description": "A non-greasy cream that offers surface hydration and supports the skin barrier."},
        "sunscreen": {"name": "Sheer Mineral Sunscreen SPF 30", "description": "Provides broad-spectrum protection with a lightweight, natural finish."}
    },
    "Sensitive": {
        "cleanser": {"name": "Ultra-Gentle Hydrating Milky Cleanser", "description": "A soap-free, pH-balanced cleanser that soothes and calms irritated skin."},
        "serum": {"name": "Centella Asiatica (Cica) Calming Serum", "description": "Reduces redness and irritation while strengthening the skin barrier."},
        "moisturizer": {"name": "Soothing Oat and Peptide Moisturizer", "description": "A calming, nourishing cream designed to reduce redness and sensitivity."},
        "sunscreen": {"name": "100% Mineral Sunscreen for Sensitive Skin SPF 50", "description": "A gentle, non-irritating formula that provides physical sun protection."}
    }
}


def analyze_skin_type(image_bytes):
    """
    !!! IMPORTANT ML MODEL PLACEHOLDER !!!
    This is where you would integrate your actual machine learning model.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        print(f"Image received and opened successfully. Size: {image.size}")
    except Exception as e:
        print(f"Could not process image: {e}")
        return None

    # --- MODEL SIMULATION ---
    skin_types = ["Oily", "Dry", "Combination", "Normal", "Sensitive"]
    predicted_type = random.choice(skin_types)
    # --- END SIMULATION ---
    
    return predicted_type


@app.route('/')
def homepage():
    """Renders the new homepage."""
    return render_template('homepage.html')


@app.route('/analyze')
def index():
    """Renders the main analysis page."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Receives an image, predicts skin type, and returns recommendations."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    if file:
        image_bytes = file.read()
        
        skin_type = analyze_skin_type(image_bytes)

        if skin_type is None:
            return jsonify({'error': 'Could not analyze image'}), 500
            
        recommendations = product_database.get(skin_type, {})
        
        return jsonify({
            'skin_type': skin_type,
            'recommendations': recommendations
        })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

