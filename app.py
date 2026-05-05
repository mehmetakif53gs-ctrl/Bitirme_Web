import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# --- AYARLAR VE MODEL YÜKLEME ---
MODEL_PATH = 'static/models/convnextbase_densenet121.keras'
if os.path.exists(MODEL_PATH):
    print("--- Model Yükleniyor, Bekle Kanka... ---")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("--- Model Başarıyla Yüklendi! ---")
else:
    print(f"--- HATA: {MODEL_PATH} bulunamadı! ---")

# Klasör isimlerinin alfabetik sırasına göre etiketler (dermatit, liken, mf, psoriazis)
LABELS = ["Atopik Dermatit", "Liken Planus", "Mikozis Fungoides (MF)", "Sedef Hastalığı (Psoriazis)"]

def prepare_image(img):
    # Bu fonksiyon artık doğrudan imread yapmıyor, gelen image objesini işliyor
    # OpenCV BGR okur, modele RGB lazım
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Makaleye uygun boyutlandırma (384x384)
    img_resized = cv2.resize(img_rgb, (384, 384))
    
    # NORMALİZASYON: En kritik yer. Makaleye göre 0-1 arasına çekiyoruz.
    img_normalized = img_resized.astype('float32') / 255.0  
    
    img_final = np.expand_dims(img_normalized, axis=0)
    return img_final

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'label': 'Dosya seçilmedi', 'score': 0}), 400
    
    file = request.files['file']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({'label': 'Geçersiz resim formatı', 'score': 0}), 400
    
    # Ön işleme fonksiyonunu çağıralım
    processed_img = prepare_image(img)
    
    # Gerçek Tahmin
    prediction = model.predict(processed_img)
    target_index = np.argmax(prediction[0])
    confidence = float(prediction[0][target_index])
    
    # Terminale log basalım ki ne bulduğunu görelim kanka
    print(f"Tahmin: {LABELS[target_index]} - Güven: %{confidence*100:.2f}")
    
    return jsonify({
        'label': LABELS[target_index],
        'score': confidence
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)