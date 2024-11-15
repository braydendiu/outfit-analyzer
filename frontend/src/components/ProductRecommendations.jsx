const ProductCard = ({ product }) => {
    if (!product) return null;
  
    return (
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        <div className="relative w-full h-64">
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = `https://via.placeholder.com/400x600.png?text=${encodeURIComponent(product.category)}`;
            }}
          />
          {/* Removed the brand div that was here */}
        </div>
        <div className="p-4">
          <h3 className="font-medium text-gray-900 mb-1 line-clamp-2">{product.title}</h3>
          <div className="flex items-center justify-between mt-2">
            <span className="text-sm text-gray-600 capitalize">{product.category}</span>
            <span className="text-blue-600 font-bold">
              ${product.price?.current?.toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    );
  };