import React, { useState } from 'react';
import { Camera, Loader2, UserCircle2, User, Upload, RefreshCw } from 'lucide-react';

const ColorPalette = ({ colors = [] }) => (
  <div className="flex flex-wrap gap-6">
    {colors.length > 0 ? colors.map((color, index) => (
      <div key={index} className="group relative">
        <div
          className="w-24 h-24 rounded-2xl shadow-lg transform transition-all duration-200 
            group-hover:scale-110 group-hover:shadow-xl ring-2 ring-white"
          style={{ backgroundColor: color }}
        />
        <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 px-3 py-1 bg-gray-900 
          text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
          {color}
        </span>
      </div>
    )) : (
      <p className="text-gray-500">Upload an image to see color analysis</p>
    )}
  </div>
);

const TextureAnalysis = ({ data = {} }) => (
  <div className="grid grid-cols-3 gap-6">
    {Object.keys(data).length > 0 ? Object.entries(data).map(([key, value]) => (
      <div key={key} className="text-center">
        <div className="text-2xl font-bold text-gray-900">
          {(value * 100).toFixed(0)}%
        </div>
        <div className="text-sm text-gray-500 capitalize">{key.replace(/_/g, ' ')}</div>
      </div>
    )) : <p>Texture analysis data not available</p>}
  </div>
);

const ProductCard = ({ product }) => {
  if (!product) return null;

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 group">
      <div className="relative w-full h-72">
        <img
          src={product.image_url}
          alt={product.title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = `/api/placeholder/400/600?text=${encodeURIComponent(product.category)}`;
          }}
        />
      </div>
      <div className="p-6">
        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
          {product.title}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 capitalize px-3 py-1 bg-gray-100 rounded-full">
            {product.category}
          </span>
          <span className="text-blue-600 font-bold">
            ${product.price?.current?.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
};

const OutfitSection = ({ outfit }) => (
  <div className="border-b border-gray-200 pb-12 last:border-0">
    <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
      <span>{outfit.type}</span>
      <div className="h-px flex-1 bg-gray-200" />
    </h3>
    <p className="text-gray-600 mb-8">{outfit.description}</p>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {outfit.pieces?.map((piece, index) => (
        <ProductCard key={index} product={piece} />
      ))}
    </div>
  </div>
);

export default function ImageAnalysis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [gender, setGender] = useState('women');
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    processFile(selectedFile);
  };

  const processFile = (selectedFile) => {
    if (selectedFile) {
      if (!selectedFile.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }

      setFile(selectedFile);
      setError(null);
      setAnalysis(null);
      
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result);
      reader.onerror = () => setError('Failed to read image file');
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('gender', gender);

      const response = await fetch('http://localhost:8000/api/analyze-image', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analysis failed (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      setAnalysis(result);
      
    } catch (err) {
      setError(err.message || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Main Container with Animated Background */}
      <div className="relative bg-gradient-to-r from-blue-600 to-blue-700 rounded-3xl shadow-2xl overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[length:20px_20px]"></div>
          <div className="absolute inset-0 animate-pulse bg-gradient-to-r from-blue-500/20 to-blue-600/20"></div>
        </div>

        {/* White Content Area */}
        <div className="relative bg-white/95 m-1 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-blue-600 mb-2">Fashion Outfit Analyzer</h2>
          <p className="text-gray-600 mb-6">Upload your fashion image and discover your style</p>
          
          {/* Gender Selector */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setGender('women')}
              className={`flex-1 py-3 px-6 rounded-xl transition-all ${
                gender === 'women'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Women's
            </button>
            <button
              onClick={() => setGender('men')}
              className={`flex-1 py-3 px-6 rounded-xl transition-all ${
                gender === 'men'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Men's
            </button>
          </div>

          {/* Upload Area */}
          <div 
            className={`relative border-2 border-dashed rounded-xl p-8 transition-all
              ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
              ${error ? 'border-red-300' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept="image/*"
              onChange={handleFileChange}
            />
            
            <div className="space-y-4 text-center">
              {preview ? (
                <div className="relative max-w-md mx-auto">
                  <img
                    src={preview}
                    alt="Preview"
                    className="mx-auto max-h-80 rounded-xl object-contain"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                      setPreview('');
                    }}
                    className="absolute top-2 right-2 p-2 bg-blue-100 rounded-full hover:bg-blue-200 transition-colors"
                  >
                    <RefreshCw className="w-5 h-5 text-blue-600" />
                  </button>
                </div>
              ) : (
                <div className="py-12">
                  <div className="w-20 h-20 bg-blue-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <Upload className="w-10 h-10 text-blue-600" />
                  </div>
                  <p className="text-lg font-medium text-gray-700">Drop your image here</p>
                  <p className="text-sm text-gray-500">or click to browse</p>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600">
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full mt-6 py-3 px-6 bg-blue-600 text-white rounded-xl font-medium
              hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                Analyzing...
              </span>
            ) : (
              'Analyze Image'
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {analysis && (
        <div className="space-y-8">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-1 rounded-3xl shadow-2xl">
            <div className="bg-white/95 rounded-[1.4rem] p-8">
              <h3 className="text-2xl font-bold text-blue-600 mb-6">Color Analysis</h3>
              <ColorPalette colors={analysis.dominant_colors} />
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-1 rounded-3xl shadow-2xl">
            <div className="bg-white/95 rounded-[1.4rem] p-8">
              <h3 className="text-2xl font-bold text-blue-600 mb-6">
                {gender === 'men' ? "Men's" : "Women's"} Outfit Recommendations
              </h3>
              <div className="space-y-12">
                {analysis.outfit_recommendations?.map((outfit, index) => (
                  <OutfitSection key={index} outfit={outfit} />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}