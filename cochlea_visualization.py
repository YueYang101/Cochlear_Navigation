"""
Cochlea Visualization Module
Handles all plotting and visualization for cochlea models
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


class CochleaVisualizer:
    """Handles visualization of cochlea models."""
    
    def __init__(self, model):
        """
        Initialize visualizer with a cochlea model.
        
        Args:
            model: CochleaModel instance
        """
        self.model = model
        
    def plot_parameters(self, geometry=None):
        """Plot parameter estimations and model characteristics."""
        if geometry is None:
            geometry = self.model.generate_geometry()
        
        fig = plt.figure(figsize=(12, 5))
        
        # Plot 1: Distance from Modiolus
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.plot(geometry['turns'], geometry['r_modiolus'], 'b-', linewidth=2)
        ax1.plot([0, 0.25, 0.5, 0.75], self.model.A, 'ro', markersize=8)
        ax1.set_xlabel('Turns')
        ax1.set_ylabel('Distance from Modiolus (mm)')
        ax1.set_title('Radial Distance vs. Turns')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.25, np.ceil(geometry['turns'][-1]))
        
        # Plot 2: Height Profile
        ax2 = fig.add_subplot(1, 2, 2)
        height = self.model._height_poly(geometry['phi'])
        ax2.plot(geometry['turns'], height, 'g-', linewidth=2)
        ax2.set_xlabel('Turns')
        ax2.set_ylabel('Height (mm)')
        ax2.set_title('Height Profile')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(-0.25, np.ceil(geometry['turns'][-1]))
        
        plt.tight_layout()
        return fig
    
    def plot_3d_model(self, show_modiolus=True, show_scala=True, 
                      show_centerline=True, view_angle=(15, 15)):
        """
        Create 3D visualization of the cochlea.
        
        Args:
            show_modiolus: Display central axis
            show_scala: Display scala surface
            show_centerline: Display centerline curve
            view_angle: Tuple of (elevation, azimuth) angles
        """
        geometry = self.model.generate_geometry()
        
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot modiolus (central axis)
        if show_modiolus:
            z_min = geometry['centerline'][2, 0] - 1
            z_max = geometry['centerline'][2, -1] + 1
            ax.plot([0, 0], [0, 0], [z_min, z_max],
                   color='gray', linewidth=5, alpha=0.6, label='Modiolus')
        
        # Plot scala surface
        if show_scala:
            surf = ax.plot_surface(geometry['scala']['x'], 
                                 geometry['scala']['y'], 
                                 geometry['scala']['z'],
                                 alpha=0.3, cmap='winter', 
                                 edgecolor='none', label='Scala')
        
        # Plot centerline
        if show_centerline:
            ax.plot(geometry['centerline'][0], 
                   geometry['centerline'][1], 
                   geometry['centerline'][2],
                   'k-', linewidth=3, label='Centerline')
        
        # Set labels and title
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('3D Cochlea Model')
        
        # Set equal aspect ratio
        max_range = np.array([
            geometry['centerline'][0].max() - geometry['centerline'][0].min(),
            geometry['centerline'][1].max() - geometry['centerline'][1].min(),
            geometry['centerline'][2].max() - geometry['centerline'][2].min()
        ]).max() / 2.0
        
        mid_x = (geometry['centerline'][0].max() + geometry['centerline'][0].min()) * 0.5
        mid_y = (geometry['centerline'][1].max() + geometry['centerline'][1].min()) * 0.5
        mid_z = (geometry['centerline'][2].max() + geometry['centerline'][2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        # Set viewing angle
        ax.view_init(elev=view_angle[0], azim=view_angle[1])
        
        # Add legend
        ax.legend()
        
        plt.tight_layout()
        return fig, ax
    
    def plot_cross_sections(self, cross_sections=None):
        """Plot cross-sectional views of the cochlea."""
        if cross_sections is None:
            cross_sections = self.model.generate_cross_sections()
        
        fig = plt.figure(figsize=(12, 8))
        
        # Plot all cross sections in 3D
        ax1 = fig.add_subplot(121, projection='3d')
        
        for i, section in enumerate(cross_sections):
            points = np.array(section['points'])
            ax1.plot(points[:, 0], points[:, 1], points[:, 2], 
                    'b-', linewidth=2, alpha=0.7)
            ax1.scatter(*section['center'], c='r', s=50)
        
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_zlabel('Z (mm)')
        ax1.set_title('Cross Sections')
        
        # Plot cross section shapes in 2D
        ax2 = fig.add_subplot(122)
        
        for i, section in enumerate(cross_sections):
            # Project onto plane perpendicular to centerline
            points = np.array(section['points'])
            center = section['center']
            
            # Simple 2D projection
            local_x = points[:, 0] - center[0]
            local_y = points[:, 2] - center[2]
            
            color = plt.cm.viridis(i / len(cross_sections))
            ax2.plot(local_x, local_y, color=color, 
                    label=f'Turn {section["phi"]/(2*np.pi):.2f}')
        
        ax2.set_xlabel('Width (mm)')
        ax2.set_ylabel('Height (mm)')
        ax2.set_title('Cross Section Shapes')
        ax2.axis('equal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        return fig
    
    def create_animation(self, filename='cochlea_rotation.gif', duration=10):
        """
        Create rotating animation of the 3D model.
        
        Args:
            filename: Output filename
            duration: Animation duration in seconds
        """
        geometry = self.model.generate_geometry()
        
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Set up the plot
        ax.plot([0, 0], [0, 0], 
               [geometry['centerline'][2, 0] - 1, geometry['centerline'][2, -1] + 1],
               color='gray', linewidth=5, alpha=0.6)
        
        ax.plot_surface(geometry['scala']['x'], 
                       geometry['scala']['y'], 
                       geometry['scala']['z'],
                       alpha=0.3, cmap='winter', edgecolor='none')
        
        ax.plot(geometry['centerline'][0], 
               geometry['centerline'][1], 
               geometry['centerline'][2],
               'k-', linewidth=3)
        
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title('3D Cochlea Model')
        
        # Animation function
        def rotate(frame):
            ax.view_init(elev=15, azim=frame)
            return ax,
        
        # Create animation
        frames = np.linspace(0, 360, int(duration * 30))
        anim = animation.FuncAnimation(fig, rotate, frames=frames, 
                                     interval=1000/30, blit=False)
        
        # Save animation
        anim.save(filename, writer='pillow', fps=30)
        plt.close()
        
        print(f"Animation saved to {filename}")
    
    def plot_complete_analysis(self):
        """Create comprehensive visualization with all plots."""
        fig = plt.figure(figsize=(16, 12))
        
        geometry = self.model.generate_geometry()
        
        # Calculate lengths
        length_with_height = self.model.calculate_length(with_height=True)
        length_without_height = self.model.calculate_length(with_height=False)
        
        # Text summary
        ax_text = fig.add_subplot(3, 3, 1)
        ax_text.axis('off')
        summary_text = (
            f"Cochlea Model Summary\n"
            f"{'='*30}\n"
            f"Parameters:\n"
            f"  A1 = {self.model.A[0]:.3f} mm\n"
            f"  B1 = {self.model.A[1]:.3f} mm\n"
            f"  A2 = {self.model.A[2]:.3f} mm\n"
            f"  B2 = {self.model.A[3]:.3f} mm\n\n"
            f"Derived Values:\n"
            f"  Turns: {self.model.n_turns:.3f}\n"
            f"  Length (with height): {length_with_height:.2f} mm\n"
            f"  Length (no height): {length_without_height:.2f} mm"
        )
        ax_text.text(0.1, 0.5, summary_text, fontsize=12, 
                    verticalalignment='center', fontfamily='monospace')
        
        # Parameter plots
        ax1 = fig.add_subplot(3, 3, 2)
        ax1.plot(geometry['turns'], geometry['r_modiolus'], 'b-', linewidth=2)
        ax1.plot([0, 0.25, 0.5, 0.75], self.model.A, 'ro', markersize=8)
        ax1.set_xlabel('Turns')
        ax1.set_ylabel('Distance (mm)')
        ax1.set_title('Radial Distance')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(3, 3, 3)
        height = self.model._height_poly(geometry['phi'])
        ax2.plot(geometry['turns'], height, 'g-', linewidth=2)
        ax2.set_xlabel('Turns')
        ax2.set_ylabel('Height (mm)')
        ax2.set_title('Height Profile')
        ax2.grid(True, alpha=0.3)
        
        # 3D views
        ax3 = fig.add_subplot(3, 3, (4, 8), projection='3d')
        ax3.plot([0, 0], [0, 0], 
                [geometry['centerline'][2, 0] - 1, geometry['centerline'][2, -1] + 1],
                color='gray', linewidth=5, alpha=0.6)
        ax3.plot_surface(geometry['scala']['x'], 
                        geometry['scala']['y'], 
                        geometry['scala']['z'],
                        alpha=0.3, cmap='winter', edgecolor='none')
        ax3.plot(geometry['centerline'][0], 
                geometry['centerline'][1], 
                geometry['centerline'][2],
                'k-', linewidth=3)
        ax3.set_xlabel('X (mm)')
        ax3.set_ylabel('Y (mm)')
        ax3.set_zlabel('Z (mm)')
        ax3.set_title('3D Model')
        ax3.view_init(elev=15, azim=45)
        
        # Cross sections
        ax4 = fig.add_subplot(3, 3, 9)
        cross_sections = self.model.generate_cross_sections(geometry, num_sections=5)
        for i, section in enumerate(cross_sections):
            points = np.array(section['points'])
            center = section['center']
            local_x = points[:, 0] - center[0]
            local_y = points[:, 2] - center[2]
            color = plt.cm.viridis(i / len(cross_sections))
            ax4.plot(local_x, local_y, color=color, linewidth=2,
                    label=f'{section["phi"]/(2*np.pi):.1f} turns')
        ax4.set_xlabel('Width (mm)')
        ax4.set_ylabel('Height (mm)')
        ax4.set_title('Cross Sections')
        ax4.axis('equal')
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=8)
        
        plt.suptitle('Complete Cochlea Analysis', fontsize=16)
        plt.tight_layout()
        return fig