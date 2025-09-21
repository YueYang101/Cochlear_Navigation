"""
Cochlea Export Module - Simplified Version
Exports only full circle cross sections for easy import with Fusion 360 ImportSplineCSV
"""

import numpy as np
from pathlib import Path
import json
import shutil


class CochleaExporter:
    """Handles export of cochlea models to CSV format."""
    
    def __init__(self, model):
        """Initialize exporter with a cochlea model."""
        self.model = model
        
    def export_all(self, export_dir='cochlea_output', replace_existing=True):
        """
        Export centerline and full circle cross sections.
        
        Args:
            export_dir: Directory for exported files
            replace_existing: If True, remove existing directory before export
        """
        export_path = Path(export_dir)
        
        # Handle existing directory
        if export_path.exists() and replace_existing:
            shutil.rmtree(export_path)
            print(f"Removed existing directory: {export_path}")
        
        export_path.mkdir(exist_ok=True)
        
        # Ask user for export options
        print("\n" + "="*60)
        print("EXPORT OPTIONS")
        print("="*60)
        
        # Get centerline mode
        while True:
            print("\nSelect centerline export mode:")
            print("  1 - Full 3D centerline (spiral with height)")
            print("  2 - 2D centerline (XY projection)")
            
            choice = input("\nEnter your choice (1 or 2): ").strip()
            
            if choice == '1':
                centerline_mode = '3D'
                break
            elif choice == '2':
                centerline_mode = '2D'
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        # Get number of cross sections
        while True:
            num_input = input("\nEnter number of cross sections (2-20, default=5): ").strip()
            
            if not num_input:  # Default
                num_cross_sections = 5
                break
            
            try:
                num_cross_sections = int(num_input)
                if 2 <= num_cross_sections <= 20:
                    break
                else:
                    print("Please enter a number between 2 and 20.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        print(f"\nExporting with {centerline_mode} centerline and {num_cross_sections} cross sections...")
        
        # Generate geometry with high resolution
        geometry = self.model.generate_geometry(resolution=0.05)
        
        # Export files
        results = {}
        results['csv'] = self.export_csv(export_dir, geometry, centerline_mode, num_cross_sections)
        results['json'] = self.export_json(export_dir, centerline_mode, num_cross_sections)
        
        self._print_export_summary(export_dir, results, centerline_mode, num_cross_sections)
        return results
    
    def export_csv(self, export_dir, geometry, centerline_mode, num_cross_sections):
        """Export centerline and cross-section points as CSV files."""
        export_path = Path(export_dir)
        
        # Export centerline - ALWAYS use X,Y,Z format for Fusion 360 compatibility
        centerline_data = []
        n_points = 100  # Optimal for smooth curves
        indices = np.linspace(0, len(geometry['centerline'][0])-1, n_points, dtype=int)
        
        for i in indices:
            x = geometry['centerline'][0, i] * 0.1  # mm to cm
            y = geometry['centerline'][1, i] * 0.1
            
            if centerline_mode == '3D':
                z = geometry['centerline'][2, i] * 0.1
            else:  # 2D mode - set Z to 0
                z = 0.0
            
            # Always export as X,Y,Z for Fusion 360 compatibility
            centerline_data.append(f"{x:.6f},{y:.6f},{z:.6f}")
        
        centerline_file = export_path / 'centerline.csv'
        with open(centerline_file, 'w') as f:
            f.write('\n'.join(centerline_data))
        
        # Generate cross sections with user-specified count
        section_positions = np.linspace(0, 1, num_cross_sections)
        cross_section_files = []
        
        for section_idx, position in enumerate(section_positions):
            # Get position along centerline
            idx = int(position * (len(geometry['phi']) - 1))
            phi = geometry['phi'][idx]
            
            # Center point
            center = np.array([
                geometry['centerline'][0, idx],
                geometry['centerline'][1, idx],
                geometry['centerline'][2, idx]
            ])
            
            # Calculate radius (decreases from base to apex)
            radius = (self.model.c_length - phi) / self.model.c_length * 0.5 + 0.6
            
            # Calculate orientation vectors
            if idx < len(geometry['phi']) - 1:
                next_idx = idx + 1
            else:
                next_idx = idx
                idx = idx - 1
            
            # Calculate tangent vector
            if centerline_mode == '3D':
                # Full 3D tangent
                tangent = np.array([
                    geometry['centerline'][0, next_idx] - geometry['centerline'][0, idx],
                    geometry['centerline'][1, next_idx] - geometry['centerline'][1, idx],
                    geometry['centerline'][2, next_idx] - geometry['centerline'][2, idx]
                ])
            else:  # 2D mode
                # Use only XY tangent, but create 3D perpendicular planes
                tangent = np.array([
                    geometry['centerline'][0, next_idx] - geometry['centerline'][0, idx],
                    geometry['centerline'][1, next_idx] - geometry['centerline'][1, idx],
                    0.0  # No Z component for 2D tangent
                ])
            
            tangent = tangent / np.linalg.norm(tangent)
            
            # Create perpendicular vectors
            if abs(tangent[2]) < 0.9:
                perp1 = np.cross([0, 0, 1], tangent)
            else:
                perp1 = np.cross([1, 0, 0], tangent)
            perp1 = perp1 / np.linalg.norm(perp1)
            perp2 = np.cross(tangent, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            
            # Generate filename
            filename = f'cross_section_{section_idx+1}.csv'
            cross_section_file = export_path / filename
            cross_section_files.append(str(cross_section_file))
            
            # Write cross section - perpendicular to centerline
            with open(cross_section_file, 'w') as f:
                n_circle_points = 60  # Smooth circle
                angles = np.linspace(0, 2*np.pi, n_circle_points+1)  # Include endpoint
                
                for angle in angles:
                    local_x = radius * np.cos(angle)
                    local_y = radius * np.sin(angle)
                    
                    # Generate perpendicular cross section
                    if centerline_mode == '2D':
                        # For 2D mode: center at XY position with Z=0, but cross section is still perpendicular
                        center_2d = np.array([center[0], center[1], 0.0])
                        point = center_2d + local_x * perp1 + local_y * perp2
                    else:
                        # For 3D mode: normal positioning
                        point = center + local_x * perp1 + local_y * perp2
                    
                    # Convert to cm
                    f.write(f"{point[0]*0.1:.6f},{point[1]*0.1:.6f},{point[2]*0.1:.6f}\n")
        
        return {
            'centerline': str(centerline_file), 
            'cross_sections': cross_section_files
        }
    
    def export_json(self, export_dir, centerline_mode, num_cross_sections):
        """Export model parameters and metadata as JSON."""
        export_path = Path(export_dir)
        
        # Calculate cross section positions
        positions = np.linspace(0, 1, num_cross_sections).tolist()
        positions = [round(p, 3) for p in positions]
        
        data = {
            'parameters': {
                'A1': float(self.model.A[0]),
                'B1': float(self.model.A[1]),
                'A2': float(self.model.A[2]),
                'B2': float(self.model.A[3])
            },
            'derived': {
                'turns': float(self.model.n_turns),
                'length_with_height': float(self.model.calculate_length(True)),
                'length_without_height': float(self.model.calculate_length(False))
            },
            'export_info': {
                'centerline_mode': centerline_mode,
                'centerline_points': 100,
                'cross_sections': num_cross_sections,
                'cross_section_positions': positions,
                'points_per_circle': 61,
                'units': 'centimeters',
                'coordinate_system': f'{centerline_mode} coordinates (always exported as X,Y,Z)'
            }
        }
        
        json_file = export_path / 'cochlea_parameters.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(json_file)
    
    def _print_export_summary(self, export_dir, results, centerline_mode, num_cross_sections):
        """Print summary of exported files."""
        print(f"\n{'='*60}")
        print(f"Export Complete - Files saved to: {Path(export_dir).absolute()}")
        print(f"{'='*60}")
        
        print(f"\nExport Configuration:")
        print(f"  - Centerline Mode: {centerline_mode}")
        print(f"  - Number of Cross Sections: {num_cross_sections}")
        print(f"  - Format: X,Y,Z coordinates (Fusion 360 compatible)")
        
        if 'csv' in results:
            print("\nCSV Files:")
            print(f"  - Centerline: centerline.csv")
            print(f"  - Cross sections: cross_section_1.csv to cross_section_{num_cross_sections}.csv")
        
        if 'json' in results:
            print(f"\nParameters: cochlea_parameters.json")
        
        print(f"\n{'='*60}")
        print("\nImport Instructions for Fusion 360:")
        print("1. Open Fusion 360 and create a new design")
        print("2. Go to UTILITIES > Scripts and Add-Ins > ImportSplineCSV")
        print("3. Select and import each CSV file:")
        print("   - First import centerline.csv")
        print(f"   - Then import each cross_section_N.csv (1 to {num_cross_sections})")
        
        if centerline_mode == '2D':
            print("\nNote: 2D Export Mode")
            print("- Centerline is projected onto XY plane (Z=0)")
            print("- Cross sections are perpendicular circles positioned along the centerline")
            print("- Cross sections maintain proper 3D orientation for lofting")
        else:
            print("\nNote: 3D Export Mode")
            print("- Full 3D spiral centerline exported")
            print("- Cross sections are positioned in 3D space")
            
        print("\n4. Use CREATE > Loft to create the 3D shape")
        print("   - Select cross sections in order from base to apex")
            
        print(f"{'='*60}\n")