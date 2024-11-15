from PIL import Image
import numpy as np
from typing import Dict, List, Union, Any
import io
from sklearn.cluster import KMeans
import cv2
import traceback
import colorsys
from .shein_service import SheinAPIService
from .base_service import BaseFashionService

class EnhancedImageProcessor:
    def __init__(self):
        print("[DEBUG] Initializing EnhancedImageProcessor")
        self.fashion_service = SheinAPIService()
        self.color_names = {
            'red': ([0, 50, 50], [10, 255, 255]),
            'pink': ([145, 30, 150], [175, 255, 255]),
            'orange': ([10, 100, 20], [25, 255, 255]),
            'yellow': ([25, 50, 50], [35, 255, 255]),
            'green': ([35, 50, 50], [85, 255, 255]),
            'blue': ([85, 50, 50], [130, 255, 255]),
            'purple': ([130, 50, 50], [145, 255, 255]),
            'brown': ([10, 50, 20], [20, 255, 200]),
            'white': ([0, 0, 200], [180, 30, 255]),
            'black': ([0, 0, 0], [180, 255, 50]),
            'gray': ([0, 0, 50], [180, 50, 200])
        }

    def _analyze_style_features(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze style features of the clothing."""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges for pattern analysis
        edges = cv2.Canny(gray, 50, 150)
        pattern_density = float(np.mean(edges) / 255.0)  # Convert to float
        
        # Detect lines for pattern analysis
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                               minLineLength=100, maxLineGap=10)
        
        has_stripes = bool(lines is not None and len(lines) > 5)  # Convert to bool
        is_solid = bool(pattern_density < 0.1)  # Convert to bool
        
        return {
            "pattern_density": float(pattern_density),
            "has_stripes": has_stripes,
            "is_solid": is_solid,
            "complexity": float(min(1.0, pattern_density * 2)),
            "uniformity": float(1.0 - min(1.0, pattern_density * 2))
        }

    async def analyze(self, file, gender: str = 'women') -> Dict[str, Any]:
        try:
            print(f"[DEBUG] Starting image analysis for {gender}'s clothing")
            image_content = await file.read()
            image = Image.open(io.BytesIO(image_content))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract features and convert numpy types to Python types
            dominant_colors = self._extract_dominant_colors(image)
            print(f"[DEBUG] Extracted colors: {dominant_colors}")
            
            style_features = self._analyze_style_features(image)
            print(f"[DEBUG] Style features: {style_features}")
            
            category = self._detect_clothing_category(image)
            print(f"[DEBUG] Detected category: {category}")
            
            # Get recommendations
            main_color = self._get_main_color_name(dominant_colors[0])
            recommendations = await self._generate_recommendations(
                main_color=main_color,
                category=category,
                style_features=style_features,
                additional_colors=dominant_colors[1:],
                gender=gender
            )

            # Ensure all values are JSON serializable
            return {
                "dominant_colors": list(dominant_colors),  # Convert to list
                "style_features": {
                    k: float(v) if isinstance(v, (np.float32, np.float64)) else v
                    for k, v in style_features.items()
                },
                "detected_category": str(category),
                "outfit_recommendations": recommendations,
                "gender": str(gender)
            }

        except Exception as e:
            print(f"[ERROR] Analysis error: {str(e)}")
            print(traceback.format_exc())
            raise

    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from the image using k-means clustering."""
        # Resize image for faster processing
        image = image.copy()
        image.thumbnail((150, 150))
        
        # Convert to numpy array
        pixels = np.float32(image).reshape(-1, 3)
        
        # Use k-means to find dominant colors
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        colors = kmeans.cluster_centers_
        
        # Convert to HSV for better color matching
        hsv_colors = []
        for color in colors:
            rgb_normalized = color / 255.0
            hsv = colorsys.rgb_to_hsv(*rgb_normalized)
            hsv_colors.append(hsv)
        
        # Sort by saturation and value to prioritize more vivid colors
        hsv_colors.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Convert back to hex colors
        hex_colors = []
        for hsv in hsv_colors:
            rgb = colorsys.hsv_to_rgb(*hsv)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            hex_colors.append(hex_color)
        
        return hex_colors

    # def _analyze_style_features(self, image: Image.Image) -> Dict[str, Any]:
    #     """Analyze style features of the clothing."""
    #     cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #     gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
    #     # Detect edges for pattern analysis
    #     edges = cv2.Canny(gray, 50, 150)
    #     pattern_density = np.mean(edges) / 255.0
        
    #     # Detect lines for pattern analysis
    #     lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
    #                            minLineLength=100, maxLineGap=10)
        
    #     has_stripes = lines is not None and len(lines) > 5
    #     is_solid = pattern_density < 0.1
        
    #     return {
    #         "pattern_density": float(pattern_density),
    #         "has_stripes": has_stripes,
    #         "is_solid": is_solid,
    #         "complexity": min(1.0, pattern_density * 2),
    #         "uniformity": 1.0 - min(1.0, pattern_density * 2)
    #     }

    def _detect_clothing_category(self, image: Image.Image) -> str:
        """Detect the clothing category based on image features."""
        # Get image dimensions
        width, height = image.size
        aspect_ratio = height / width
        
        # Basic category detection based on aspect ratio and shape analysis
        if aspect_ratio > 1.8:  # Long garment
            return "dresses"
        elif aspect_ratio > 1.2:  # Medium length
            return "tops"
        elif aspect_ratio < 0.8:  # Wide garment
            return "bottoms"
        else:
            return "tops"  # Default to tops if uncertain

    def _get_main_color_name(self, hex_color: str) -> str:
        """Convert hex color to closest named color."""
        # Convert hex to RGB
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert RGB to HSV for better color matching
        hsv = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
        
        # Match HSV values to color names
        h, s, v = hsv[0] * 180, hsv[1] * 255, hsv[2] * 255
        
        color_match = "black"  # default color
        min_difference = float('inf')
        
        for color_name, (lower, upper) in self.color_names.items():
            # Check if color falls within the defined ranges
            if (lower[0] <= h <= upper[0] and
                lower[1] <= s <= upper[1] and
                lower[2] <= v <= upper[2]):
                
                # Calculate how well it matches
                difference = abs(h - lower[0]) + abs(s - lower[1]) + abs(v - lower[2])
                if difference < min_difference:
                    min_difference = difference
                    color_match = color_name
        
        return color_match

    async def _generate_recommendations(
        self,
        main_color: str,
        category: str,
        style_features: Dict[str, Any],
        additional_colors: List[str],
        gender: str = 'women'
    ) -> List[Dict[str, Any]]:
        """Generate outfit recommendations based on analyzed features."""
        try:
            recommendations = []
            
            # Adjust categories based on gender
            if gender == 'men':
                categories = ["tops", "bottoms", "outerwear", "shoes"]
            else:
                categories = ["tops", "bottoms", "dresses", "outerwear", "shoes"]
            
            # Monochromatic outfit
            print(f"[DEBUG] Generating {gender}'s monochromatic outfit")
            mono_pieces = []
            for cat in categories:
                if cat != category:  # Don't recommend the same category
                    pieces = await self.fashion_service.search_products(
                        category=cat,
                        color=main_color,
                        gender=gender,
                        limit=1
                    )
                    if pieces:
                        mono_pieces.extend(pieces)
            
            if mono_pieces:
                recommendations.append({
                    "type": "Monochromatic Outfit",
                    "description": f"A sophisticated {main_color} ensemble for {gender}'s wear",
                    "pieces": mono_pieces
                })

            # Contrasting outfit
            if additional_colors:
                contrast_color = self._get_main_color_name(additional_colors[0])
                print(f"[DEBUG] Generating {gender}'s contrasting outfit")
                
                contrast_pieces = []
                for idx, cat in enumerate(categories):
                    if cat != category:
                        color = main_color if idx % 2 == 0 else contrast_color
                        pieces = await self.fashion_service.search_products(
                            category=cat,
                            color=color,
                            gender=gender,
                            limit=1
                        )
                        if pieces:
                            contrast_pieces.extend(pieces)
                
                if contrast_pieces:
                    recommendations.append({
                        "type": "Color Contrast Outfit",
                        "description": f"A bold combination of {main_color} and {contrast_color} for {gender}'s wear",
                        "pieces": contrast_pieces
                    })

            return recommendations

        except Exception as e:
            print(f"[ERROR] Error generating recommendations: {str(e)}")
            print(traceback.format_exc())
            return []

    def _get_texture_name(self, features: Dict[str, Any]) -> str:
        """Determine the texture type based on analyzed features."""
        if features["is_solid"]:
            return "solid"
        elif features["has_stripes"]:
            return "striped"
        elif features["pattern_density"] > 0.5:
            return "patterned"
        else:
            return "textured"
        
    