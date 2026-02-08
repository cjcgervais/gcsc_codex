#!/usr/bin/env python3
"""
Gemini Visual Verification Script
GCSC2 Constitution Article IV.6 - Dual-AI Visual Verification Protocol

Usage:
    python gemini_verify.py --image path/to/render.png --query "Describe geometry"

Purpose:
    Independent AI visual verification of GCSC2 renders to prevent
    geometry errors like the frame slot bug (Feb 2026).

Authority:
    GCSC2_Constitution.md v2.0.0, Article IV.6
    claude.md - Dual-AI Visual Verification Protocol
"""
import os
import sys
import argparse
from pathlib import Path

# Import Gemini API
try:
    import google.generativeai as genai
    from PIL import Image
except ImportError as e:
    print(f"ERROR: Required module not installed: {e}")
    print("Run: pip install google-generativeai pillow")
    sys.exit(1)

# Load API key from .env in GCSC2 root
def load_api_key():
    """Load GEMINI_API_KEY from .env file in GCSC2 root directory."""
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        print("Create .env with: GEMINI_API_KEY=your_key_here")
        sys.exit(1)

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('GEMINI_API_KEY='):
                api_key = line.split('=', 1)[1]
                if api_key:
                    return api_key

    print("ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

# Main script
def main():
    # Configure Gemini
    api_key = load_api_key()
    genai.configure(api_key=api_key)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Gemini visual verification of GCSC2 renders',
        epilog='Part of GCSC2 dual-AI verification protocol (Article IV.6)'
    )
    parser.add_argument('--image', required=True, help='Path to render image')
    parser.add_argument('--query', required=True, help='Verification query')
    args = parser.parse_args()

    # Verify image exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    # Load image
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"ERROR: Cannot load image: {e}")
        sys.exit(1)

    # Generate analysis using Gemini 1.5 Flash
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([args.query, img])
    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        print("Check: 1) API key valid, 2) Network connectivity, 3) API quota")
        sys.exit(1)

    # Output results
    print("=" * 60)
    print("GEMINI VISUAL ANALYSIS")
    print("=" * 60)
    print(f"Image: {image_path}")
    print(f"Query: {args.query}")
    print("-" * 60)
    print(response.text)
    print("=" * 60)

if __name__ == '__main__':
    main()
