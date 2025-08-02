#!/usr/bin/env python3
"""
Martin Icon Generator
Creates PNG icons from SVG for the Chrome extension
"""

import os
import sys

# Try to import required libraries
try:
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg
    print("✅ Using cairosvg for high-quality icon generation")
    USE_CAIRO = True
except ImportError:
    print("⚠️  cairosvg not found, using basic PIL generation")
    print("   Install with: pip install cairosvg pillow")
    USE_CAIRO = False
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("❌ PIL/Pillow not found. Install with: pip install pillow")
        sys.exit(1)

def create_martin_icon_svg():
    """Create Martin logo SVG"""
    return '''<svg width="128" height="128" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="128" height="128" rx="24" fill="#3B82F6"/>
  
  <!-- Martin Logo - Layered Design -->
  <g transform="translate(64, 64)">
    <!-- Bottom layer -->
    <path d="M0 -28 L-32 -8 L0 12 L32 -8 Z" fill="rgba(255,255,255,0.3)" transform="translate(0, 16)"/>
    
    <!-- Middle layer -->
    <path d="M0 -28 L-32 -8 L0 12 L32 -8 Z" fill="rgba(255,255,255,0.6)" transform="translate(0, 0)"/>
    
    <!-- Top layer -->
    <path d="M0 -28 L-32 -8 L0 12 L32 -8 Z" fill="white" transform="translate(0, -16)"/>
    
    <!-- M Letter -->
    <text x="0" y="8" font-family="Arial, sans-serif" font-size="48" font-weight="bold" text-anchor="middle" fill="#3B82F6">M</text>
  </g>
</svg>'''

def create_martin_icon_pil(size):
    """Create Martin icon using PIL (fallback method)"""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background
    padding = int(size * 0.1)
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=int(size * 0.15),
        fill=(59, 130, 246, 255)  # #3B82F6
    )
    
    # Center point
    center = size // 2
    
    # Draw layered diamond shapes
    diamond_width = int(size * 0.5)
    diamond_height = int(size * 0.35)
    
    # Define diamond points
    def get_diamond_points(offset_y):
        return [
            (center, center - diamond_height // 2 + offset_y),  # Top
            (center - diamond_width // 2, center + offset_y),    # Left
            (center, center + diamond_height // 2 + offset_y),   # Bottom
            (center + diamond_width // 2, center + offset_y),    # Right
        ]
    
    # Draw three layers
    offsets = [int(size * 0.1), 0, -int(size * 0.1)]
    alphas = [77, 153, 255]  # 30%, 60%, 100% opacity
    
    for offset, alpha in zip(offsets, alphas):
        points = get_diamond_points(offset)
        draw.polygon(points, fill=(255, 255, 255, alpha))
    
    # Draw M in the center
    try:
        # Try to use a font
        font_size = int(size * 0.3)
        from PIL import ImageFont
        # Try different font paths for different systems
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "arial.ttf"  # Current directory
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        
        if font:
            # Draw text with font
            text = "M"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = center - text_width // 2
            text_y = center - text_height // 2
            draw.text((text_x, text_y), text, fill=(59, 130, 246, 255), font=font)
    except:
        # Fallback: draw a simple M shape
        m_width = int(size * 0.25)
        m_height = int(size * 0.2)
        m_points = [
            (center - m_width//2, center + m_height//2),
            (center - m_width//2, center - m_height//2),
            (center, center),
            (center + m_width//2, center - m_height//2),
            (center + m_width//2, center + m_height//2),
        ]
        draw.line(m_points, fill=(59, 130, 246, 255), width=max(2, size//16))
    
    return img

def generate_icons():
    """Generate all required icon sizes"""
    sizes = [16, 48, 128]
    output_dir = "extension/dist_v2/icons"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎨 Generating Martin icons...")
    
    if USE_CAIRO:
        # Generate high-quality icons using cairosvg
        svg_content = create_martin_icon_svg()
        
        for size in sizes:
            output_path = os.path.join(output_dir, f"icon{size}.png")
            print(f"  Creating {size}x{size} icon...")
            
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=output_path,
                output_width=size,
                output_height=size
            )
            
            print(f"  ✅ Saved to {output_path}")
    else:
        # Use PIL fallback
        for size in sizes:
            output_path = os.path.join(output_dir, f"icon{size}.png")
            print(f"  Creating {size}x{size} icon...")
            
            img = create_martin_icon_pil(size)
            img.save(output_path, "PNG")
            
            print(f"  ✅ Saved to {output_path}")
    
    print("\n✨ Icon generation complete!")
    print("\nNext steps:")
    print("1. Check the generated icons in extension/dist_v2/icons/")
    print("2. Load the extension in Chrome")
    print("3. Start the backend server")

if __name__ == "__main__":
    generate_icons()
