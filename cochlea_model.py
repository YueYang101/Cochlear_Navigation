"""
Cochlea Model Module
Core mathematical equations and geometry generation for cochlea modeling
"""

import numpy as np
from scipy.integrate import quad
from cochlea_parameters import CochleaParameters


class CochleaModel:
    """Core cochlea mathematical model."""
    
    def __init__(self, parameters=None, mode='mean'):
        """
        Initialize cochlea model with parameters.
        
        Args:
            parameters: 4-element array [A1, B1, A2, B2] or None
            mode: 'mean' or 'random' if parameters is None
        """
        self.param_manager = CochleaParameters()
        self.coefs = self.param_manager.coefs
        
        if parameters is None:
            self.A = self.param_manager.generate_parameters(mode)
            print(f"{mode.capitalize()} cochlea values selected")
        else:
            self.param_manager.validate_parameters(parameters)
            self.A = np.array(parameters)
        
        # Calculate derived parameters
        self.c_length = self._turn_number_estimation() * 2 * np.pi
        self.n_turns = self.c_length / (2 * np.pi)
        
        print(f"Parameters: A1 = {self.A[0]:.3f}, B1 = {self.A[1]:.3f}, "
              f"A2 = {self.A[2]:.3f}, B2 = {self.A[3]:.3f}")
        print(f"Estimated number of turns: {self.n_turns:.3f}")
    
    def _turn_number_estimation(self):
        """Estimate number of turns."""
        return np.dot(np.append(1, self.A), self.coefs['turns']) / 360
    
    def _radius_modiolus_poly(self, phi):
        """Calculate radius from modiolus at angle phi."""
        coeffs = []
        for i in range(4):
            coeffs.append(np.dot(np.append(1, self.A), self.coefs['modiolus'][:, i]))
        return np.polyval(coeffs[::-1], phi)
    
    def _height_poly(self, phi):
        """Calculate height at angle phi."""
        coeffs = []
        for i in range(5):
            coeffs.append(np.dot(np.append(1, self.A), self.coefs['height'][:, i]))
        return np.polyval(coeffs[::-1], phi)
    
    def get_radius_coeffs(self):
        """Get polynomial coefficients for radius."""
        coeffs = []
        for i in range(4):
            coeffs.append(np.dot(np.append(1, self.A), self.coefs['modiolus'][:, i]))
        return coeffs[::-1]
    
    def get_height_coeffs(self):
        """Get polynomial coefficients for height."""
        coeffs = []
        for i in range(5):
            coeffs.append(np.dot(np.append(1, self.A), self.coefs['height'][:, i]))
        return coeffs[::-1]
    
    def calculate_length(self, with_height=True):
        """Calculate the length of the cochlea spiral."""
        def integrand(z):
            r = self._radius_modiolus_poly(z)
            dr_dz = np.polyder(np.poly1d(self.get_radius_coeffs()))(z)
            
            x_deriv = dr_dz * np.cos(z) - r * np.sin(z)
            y_deriv = dr_dz * np.sin(z) + r * np.cos(z)
            
            if with_height:
                dh_dz = np.polyder(np.poly1d(self.get_height_coeffs()))(z)
                return np.sqrt(x_deriv**2 + y_deriv**2 + dh_dz**2)
            else:
                return np.sqrt(x_deriv**2 + y_deriv**2)
        
        length, _ = quad(integrand, 0, self.c_length)
        return length
    
    def generate_geometry(self, resolution=0.1):
        """
        Generate the 3D geometry of the cochlea.
        
        Args:
            resolution: Angular resolution in radians
            
        Returns:
            dict with centerline, scala surface, phi angles, and turns
        """
        phi = np.arange(0, self.c_length, resolution)
        
        # Calculate centerline
        r_modiolus = self._radius_modiolus_poly(phi)
        centerline = np.array([
            r_modiolus * np.cos(phi),
            r_modiolus * np.sin(phi),
            self._height_poly(phi)
        ])
        
        # Generate scala surface
        v = np.arange(0, 2*np.pi, resolution)
        scala_x = np.zeros((len(v), len(phi)))
        scala_y = np.zeros((len(v), len(phi)))
        scala_z = np.zeros((len(v), len(phi)))
        
        for i, p in enumerate(phi):
            # Scala radius decreases from base to apex
            r_scala = (self.c_length - p) / self.c_length * 0.5 + 0.6
            
            for j, angle in enumerate(v):
                # Generate circular cross-section
                local_r = r_modiolus[i] + r_scala * (np.cos(angle) - 1)
                scala_x[j, i] = local_r * np.cos(p)
                scala_y[j, i] = local_r * np.sin(p)
                scala_z[j, i] = r_scala * np.sin(angle) + centerline[2, i]
        
        return {
            'centerline': centerline,
            'scala': {'x': scala_x, 'y': scala_y, 'z': scala_z},
            'phi': phi,
            'turns': phi / (2 * np.pi),
            'r_modiolus': r_modiolus
        }
    
    def generate_cross_sections(self, geometry=None, num_sections=10):
        """Generate cross sections for the cochlea."""
        if geometry is None:
            geometry = self.generate_geometry(resolution=5)
            
        half_idx = len(geometry['phi']) // 2
        section_indices = np.linspace(0, half_idx-1, num_sections, dtype=int)
        
        cross_sections = []
        
        for idx in section_indices:
            phi = geometry['phi'][idx]
            center = geometry['centerline'][:, idx]
            radius = (self.c_length - phi) / self.c_length * 0.5 + 0.6
            
            # Generate circular cross section
            n_points = 16  # Points for smooth curves
            angles = np.linspace(0, 2*np.pi, n_points+1)
            
            section = {
                'center': center,
                'radius': radius,
                'angle': phi * 180 / np.pi,
                'phi': phi,
                'points': []
            }
            
            for angle in angles:
                local_r = radius * (np.cos(angle) - 1)
                local_h = radius * np.sin(angle)
                
                x = center[0] + local_r * np.cos(phi)
                y = center[1] + local_r * np.sin(phi)
                z = center[2] + local_h
                
                section['points'].append([x, y, z])
            
            cross_sections.append(section)
        
        return cross_sections
    
    def get_point_at_position(self, turn_fraction):
        """
        Get 3D coordinates at a specific position along the cochlea.
        
        Args:
            turn_fraction: Position as fraction of total turns (0-1)
            
        Returns:
            dict with position, radius, and height
        """
        phi = turn_fraction * self.c_length
        r = self._radius_modiolus_poly(phi)
        
        return {
            'position': [r * np.cos(phi), r * np.sin(phi), self._height_poly(phi)],
            'radius_modiolus': r,
            'height': self._height_poly(phi),
            'phi': phi,
            'turns': phi / (2 * np.pi)
        }