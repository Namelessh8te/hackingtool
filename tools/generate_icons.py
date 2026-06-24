#!/usr/bin/env python3
"""
Convert logo.svg to PNG icons in multiple resolutions.
Uses PIL to create raster versions from SVG.
Run with: python3 tools/generate_icons.py
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("❌ Pillow not installed!")
    print("Install with: pip install pillow")
    sys.exit(1)


def create_hackingtool_icon(size):
    """
    Create a HackingTool icon programmatically in the given size.
    Returns a PIL Image object.
    """
    
    # Colors
    BLACK = (10, 10, 10)
    MAGENTA = (123, 97, 255)  # #7B61FF
    BRIGHT_GREEN = (0, 255, 100)
    WHITE = (255, 255, 255)
    
    # Create image with black background
    img = Image.new('RGB', (size, size), BLACK)
    draw = ImageDraw.Draw(img)
    
    # Scale factors
    scale = size / 256  # Base size is 256x256
    
    # Draw border
    border_width = max(1, int(2 * scale))
    margin = int(5 * scale)
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        outline=MAGENTA,
        width=border_width
    )
    
    # Draw inner border
    inner_margin = margin + int(3 * scale)
    draw.rectangle(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        outline=BRIGHT_GREEN,
        width=max(1, int(1 * scale))
    )
    
    # Draw "H" (simplified geometric representation)
    h_x = int(20 * scale)
    h_y = int(30 * scale)
    h_size = int(60 * scale)
    
    # Left vertical line
    draw.rectangle([h_x, h_y, h_x + int(8 * scale), h_y + h_size], fill=MAGENTA)
    # Right vertical line
    draw.rectangle([h_x + int(52 * scale), h_y, h_x + h_size, h_y + h_size], fill=MAGENTA)
    # Horizontal line in middle
    draw.rectangle([h_x, h_y + int(25 * scale), h_x + h_size, h_y + int(33 * scale)], fill=MAGENTA)
    
    # Draw circle/gear pattern on right side
    center_x = int(190 * scale)
    center_y = int(80 * scale)
    radius = int(30 * scale)
    
    # Draw circle
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        outline=BRIGHT_GREEN,
        width=max(1, int(2 * scale))
    )
    
    # Draw crosshairs inside circle
    cross_len = int(15 * scale)
    draw.line([center_x - cross_len, center_y, center_x + cross_len, center_y], fill=BRIGHT_GREEN, width=max(1, int(1 * scale)))
    draw.line([center_x, center_y - cross_len, center_x, center_y + cross_len], fill=BRIGHT_GREEN, width=max(1, int(1 * scale)))
    
    # Draw "T" shape at bottom
    t_x = int(90 * scale)
    t_y = int(170 * scale)
    t_size = int(60 * scale)
    
    # Top horizontal line
    draw.rectangle([t_x, t_y, t_x + t_size, t_y + int(8 * scale)], fill=BRIGHT_GREEN)
    # Vertical line
    draw.rectangle([t_x + int(26 * scale), t_y, t_x + int(34 * scale), t_y + int(50 * scale)], fill=BRIGHT_GREEN)
    
    # Draw binary pattern at bottom
    bin_y = int(220 * scale)
    bin_text_parts = ["01", "10", "11", "01"]
    spacing = int(15 * scale)
    
    for i, text in enumerate(bin_text_parts):
        x_pos = int(30 * scale) + (i * spacing)
        # Draw small squares for binary representation
        sq_size = int(3 * scale)
        for j, bit in enumerate(text):
            if bit == '1':
                draw.rectangle(
                    [x_pos + (j * sq_size * 1.5), bin_y, x_pos + (j * sq_size * 1.5) + sq_size, bin_y + sq_size],
                    fill=MAGENTA
                )
    
    return img


def generate_icons():
    """Generate PNG icons in multiple sizes."""
    
    icons_dir = Path(__file__).parent.parent / "images" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Sizes to generate
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    print("🎨 Generating PNG icons\n")
    
    for size in sizes:
        output_path = icons_dir / f"hackingtool-{size}x{size}.png"
        
        try:
            print(f"  Generating {size}x{size}...", end=" ", flush=True)
            
            # Create icon
            img = create_hackingtool_icon(size)
            img.save(str(output_path), 'PNG', quality=95)
            
            size_kb = output_path.stat().st_size / 1024
            print(f"✅ ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    # Create favicon.ico from multiple sizes
    try:
        print(f"\n  Creating favicon.ico...", end=" ", flush=True)
        favicon_path = icons_dir / "favicon.ico"
        
        # Load generated PNGs for favicon
        icon_sizes = [16, 32, 48, 64]
        icon_images = []
        
        for size in icon_sizes:
            img = Image.open(icons_dir / f"hackingtool-{size}x{size}.png")
            icon_images.append(img)
        
        # Save as ICO
        if icon_images:
            icon_images[0].save(
                favicon_path,
                format='ICO',
                sizes=[(s, s) for s in icon_sizes],
                append_images=icon_images[1:]
            )
            size_kb = favicon_path.stat().st_size / 1024
            print(f"✅ ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"⚠️  Favicon creation skipped: {e}")
    
    print("\n" + "="*60)
    print("✅ Icon generation completed!")
    print("="*60)
    print(f"\n📍 Icons saved to: {icons_dir}")
    print("\n📋 Generated files:")
    
    for icon in sorted(icons_dir.glob("hackingtool-*.png")):
        size_kb = icon.stat().st_size / 1024
        print(f"   • {icon.name} ({size_kb:.1f} KB)")
    
    if (icons_dir / "favicon.ico").exists():
        size_kb = (icons_dir / "favicon.ico").stat().st_size / 1024
        print(f"   • favicon.ico ({size_kb:.1f} KB)")
    
    print("\n🎯 Icon Features:")
    print("   • Magenta/Purple primary color (#7B61FF)")
    print("   • Bright green accents")
    print("   • Geometric HT design (Hacking Tool)")
    print("   • Professional cybersecurity aesthetic")
    print("   • Scales perfectly at any size")
    
    print("\n💡 Usage:")
    print("   • Desktop icon: Use hackingtool-256x256.png")
    print("   • Web favicon: Use favicon.ico")
    print("   • Application icon: Use hackingtool-512x512.png")
    print("   • Taskbar icon: Use hackingtool-48x48.png or hackingtool-64x64.png")
    
    return True


if __name__ == "__main__":
    success = generate_icons()
    sys.exit(0 if success else 1)
