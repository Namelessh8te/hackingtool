#!/usr/bin/env python3
"""
Convert logo.svg to PNG icons in multiple resolutions.
Run with: python3 tools/generate_icons.py
"""

import sys
from pathlib import Path

# Try to import required libraries
try:
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg
except ImportError:
    print("❌ Required libraries not installed!")
    print("\nInstall with:")
    print("  pip install pillow cairosvg")
    sys.exit(1)


def generate_icons():
    """Convert SVG logo to PNG icons in multiple sizes."""
    
    svg_path = Path(__file__).parent.parent / "images" / "logo.svg"
    icons_dir = Path(__file__).parent.parent / "images" / "icons"
    
    if not svg_path.exists():
        print(f"❌ SVG logo not found: {svg_path}")
        return False
    
    # Create icons directory
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Sizes to generate
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    print(f"🎨 Generating PNG icons from {svg_path}\n")
    
    for size in sizes:
        output_path = icons_dir / f"hackingtool-{size}x{size}.png"
        
        try:
            print(f"  Generating {size}x{size}...", end=" ", flush=True)
            
            # Convert SVG to PNG using cairosvg
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(output_path),
                output_width=size,
                output_height=size
            )
            
            print(f"✅ {output_path}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    # Also create favicon.ico from the smallest icon
    try:
        print(f"\n  Creating favicon.ico...", end=" ", flush=True)
        favicon_path = icons_dir / "favicon.ico"
        
        # Load 256x256 PNG and create smaller versions for ICO
        img_256 = Image.open(icons_dir / "hackingtool-256x256.png")
        
        # Create ICO with multiple sizes
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        icon_images = [img_256.resize(size, Image.Resampling.LANCZOS) for size in icon_sizes]
        
        icon_images[0].save(
            favicon_path,
            format='ICO',
            sizes=icon_sizes,
            append_images=icon_images[1:]
        )
        
        print(f"✅ {favicon_path}")
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
    
    print("\n🎯 Usage:")
    print("   • Desktop icon: Use hackingtool-256x256.png")
    print("   • Web favicon: Use favicon.ico")
    print("   • Application icon: Use hackingtool-512x512.png")
    print("   • Taskbar icon: Use hackingtool-64x64.png or hackingtool-48x48.png")
    
    return True


if __name__ == "__main__":
    success = generate_icons()
    sys.exit(0 if success else 1)
