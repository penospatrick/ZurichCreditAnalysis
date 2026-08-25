# Zurich Finance Corporation Logo as SVG
# This file stores the logo data

ZURICH_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="120" height="120">
  <!-- Background circle -->
  <circle cx="250" cy="250" r="240" fill="#001f3f" stroke="#ffd700" stroke-width="8"/>
  
  <!-- Yellow/Gold accent shapes (isometric cube style) -->
  <g fill="#FFD700">
    <!-- Top face -->
    <path d="M 120 180 L 250 100 L 380 180 L 250 260 Z"/>
    <!-- Right face -->
    <path d="M 250 260 L 380 180 L 380 320 L 250 400 Z"/>
    <!-- Left face -->
    <path d="M 250 260 L 120 180 L 120 320 L 250 400 Z"/>
  </g>
  
  <!-- Dark blue accent triangles -->
  <g fill="#001f3f" opacity="0.8">
    <!-- Left triangle -->
    <path d="M 120 180 L 180 240 L 120 320 Z"/>
    <!-- Right triangle -->
    <path d="M 380 180 L 320 240 L 380 320 Z"/>
  </g>
  
  <!-- Center "Z" initial -->
  <text x="250" y="300" font-size="80" font-weight="bold" fill="#FFD700" text-anchor="middle" font-family="Arial, sans-serif">Z</text>
</svg>
"""
