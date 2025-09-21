"""
Simple Cochlea Export Script
Generates CSV files compatible with Fusion 360's ImportSplineCSV script
"""

import numpy as np
from pathlib import Path
from cochlea_model import CochleaModel

def export_for_fusion360_simple(output_dir='fusion360_import'):
    """Generate simple CSV files for Fusion 360 import."""
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create model
    model = CochleaModel(mode='mean')
    print(f"Created cochlea model with {model.n_turns:.2f} turns")
    
    # Generate geometry with fine resolution
    geometry = model.generate_geometry(resolution=0.1)
    
    # Export centerline as CSV (X,Y,Z format with no headers)
    print("\nExporting centerline...")
    centerline_file = Path(output_dir) / 'cochlea_centerline.csv'
    
    # Sample points evenly along the centerline
    n_points = 100  # Fusion 360 works well with ~100 points
    indices = np.linspace(0, len(geometry['centerline'][0])-1, n_points, dtype=int)
    
    with open(centerline_file, 'w') as f:
        for i in indices:
            x = geometry['centerline'][0, i]
            y = geometry['centerline'][1, i]
            z = geometry['centerline'][2, i]
            f.write(f"{x:.6f},{y:.6f},{z:.6f}\n")
    
    print(f"Saved: {centerline_file}")
    
    # Generate and export cross sections
    print("\nExporting cross sections...")
    cross_sections_file = Path(output_dir) / 'cochlea_cross_sections.csv'
    cross_sections = model.generate_cross_sections(geometry, num_sections=10)
    
    with open(cross_sections_file, 'w') as f:
        for i, section in enumerate(cross_sections):
            if i > 0:
                f.write('\n')  # Blank line between sections
            for point in section['points']:
                f.write(f"{point[0]:.6f},{point[1]:.6f},{point[2]:.6f}\n")
    
    print(f"Saved: {cross_sections_file}")
    
    # Create instructions file
    instructions_file = Path(output_dir) / 'FUSION360_INSTRUCTIONS.txt'
    with open(instructions_file, 'w') as f:
        f.write("""FUSION 360 IMPORT INSTRUCTIONS
==============================

Method 1: Using Built-in ImportSplineCSV Script
-----------------------------------------------
1. Open Fusion 360
2. Go to: UTILITIES tab > Add-Ins > Scripts and Add-Ins (or press Shift+S)
3. Find "ImportSplineCSV" in the scripts list
4. Click "Run"
5. Select 'cochlea_centerline.csv'
6. The centerline will be imported as a smooth 3D spline

Method 2: Using Insert Menu (if available)
------------------------------------------
1. Open Fusion 360
2. Go to: INSERT > Insert CSV Points
3. Select 'cochlea_centerline.csv'
4. Choose "Spline" as the style
5. Click OK

Method 3: Manual Creation
-------------------------
1. Create a new sketch
2. Use "Create > Spline > Fit Point Spline"
3. Import the CSV points manually or use a script

For Cross Sections:
-------------------
- Use 'cochlea_cross_sections.csv'
- Each blank line separates a different cross section
- Import using the same methods above

Tips:
-----
- The centerline has been optimized to ~100 points for smooth import
- All coordinates are in millimeters
- The spline starts at the base and spirals to the apex
- Use the centerline for loft/sweep operations
""")
    
    print(f"\nSaved: {instructions_file}")
    print("\n" + "="*50)
    print("Export complete!")
    print(f"Files saved to: {Path(output_dir).absolute()}")
    print("\nFollow the instructions in FUSION360_INSTRUCTIONS.txt")
    print("="*50)

if __name__ == "__main__":
    export_for_fusion360_simple()