import React, { useState, useRef } from 'react';
import ReactCropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';
import axios from 'axios';

function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const cropperRef = useRef(null);

  // Dosya seçildiğinde çalışan fonksiyon
  const onChange = (e) => {
    const files = e.target.files;
    const reader = new FileReader();
    reader.onload = () => {
      setImage(reader.result);
    };
    reader.readAsDataURL(files[0]);
  };

  // Analizi başlatan ve Flask'a gönderen fonksiyon
  const onAnalyze = async () => {
    const cropper = cropperRef.current?.cropper;
    if (!cropper) return;

    // Makalene (3.2.5) sadık kalarak tam 384x384 boyutunda kırpıyoruz
    const canvas = cropper.getCroppedCanvas({
      width: 384,
      height: 384,
    });

    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('file', blob, 'cropped_image.jpg');

      try {
        const response = await axios.post('http://127.0.0.1:5001/predict', formData);
        setResult(response.data);
      } catch (error) {
        console.error("Hata oluştu:", error);
      }
    });
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center', fontFamily: 'Arial' }}>
      <h1 style={{ color: '#2c3e50' }}>Cilt Hastalığı Analiz Portalı</h1>
      
      <input type="file" onChange={onChange} style={{ marginBottom: '20px' }} />

      {image && (
        <div style={{ maxWidth: '500px', margin: '0 auto' }}>
          <ReactCropper
            src={image}
            style={{ height: 400, width: '100%' }}
            initialAspectRatio={1} // 1:1 Kare oran (Makale 3.2.5)
            aspectRatio={1}
            guides={true}
            ref={cropperRef}
            viewMode={1}
          />
          <button 
            onClick={onAnalyze}
            style={{ marginTop: '20px', padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
          >
            Analizi Başlat
          </button>
        </div>
      )}

      {result && (
        <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '10px' }}>
          <h3>Tahmin Sonucu: {result.label}</h3>
          <p>Güven Skoru: %{ (result.score * 100).toFixed(2) }</p>
        </div>
      )}
    </div>
  );
}

export default App;