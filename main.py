"""
Main Script for Cochlea Model Generation - Simplified Version
Creates cochlea model with full circle cross sections only
"""

import argparse
import sys
from pathlib import Path

from cochlea_model import CochleaModel
from cochlea_visualization import CochleaVisualizer
from cochlea_export import CochleaExporter


def main():
    """Main function to run cochlea model generation."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate 3D cochlea model for CAD')
    parser.add_argument('--mode', choices=['mean', 'random', 'custom'], default='mean',
                      help='Parameter generation mode')
    parser.add_argument('--parameters', nargs=4, type=float, metavar=('A1', 'B1', 'A2', 'B2'),
                      help='Custom parameters (requires --mode custom)')
    parser.add_argument('--export-dir', default='cochlea_output',
                      help='Directory for exported files')
    parser.add_argument('--no-plot', action='store_true',
                      help='Skip visualization plots')
    parser.add_argument('--save-plots', action='store_true',
                      help='Save plots as PNG files')
    parser.add_argument('--keep-existing', action='store_true',
                      help='Keep existing files instead of replacing them')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'custom' and args.parameters is None:
        parser.error("--mode custom requires --parameters")
    if args.mode != 'custom' and args.parameters is not None:
        parser.error("--parameters can only be used with --mode custom")
    
    print("="*60)
    print("COCHLEA MODEL GENERATOR - SIMPLIFIED VERSION")
    print("="*60)
    
    try:
        # Create model
        if args.mode == 'custom':
            model = CochleaModel(parameters=args.parameters)
        else:
            model = CochleaModel(mode=args.mode)
        
        # Visualization
        if not args.no_plot:
            print("\nGenerating visualizations...")
            visualizer = CochleaVisualizer(model)
            
            # Create plots
            fig1 = visualizer.plot_parameters()
            fig2, ax = visualizer.plot_3d_model()
            fig3 = visualizer.plot_cross_sections()
            
            if args.save_plots:
                plot_dir = Path(args.export_dir) / 'plots'
                plot_dir.mkdir(parents=True, exist_ok=True)
                
                fig1.savefig(plot_dir / 'parameters.png', dpi=150, bbox_inches='tight')
                fig2.savefig(plot_dir / '3d_model.png', dpi=150, bbox_inches='tight')
                fig3.savefig(plot_dir / 'cross_sections.png', dpi=150, bbox_inches='tight')
                print(f"Plots saved to {plot_dir}")
            
            # Show plots
            import matplotlib.pyplot as plt
            plt.show()
        
        # Export files
        print("\nExporting files...")
        exporter = CochleaExporter(model)
        # Use replace_existing based on --keep-existing flag
        results = exporter.export_all(args.export_dir, replace_existing=not args.keep_existing)
        
        # Print lengths
        print(f"\nModel Statistics:")
        print(f"  Number of turns: {model.n_turns:.2f}")
        print(f"  Length with height: {model.calculate_length(True):.2f} mm")
        print(f"  Length without height: {model.calculate_length(False):.2f} mm")
        
        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    
    return 0


def quick_generate(parameters=None, mode='mean', export_dir='cochlea_output', replace_existing=True):
    """
    Quick generation function for script usage.
    
    Args:
        parameters: Custom parameters [A1, B1, A2, B2]
        mode: 'mean' or 'random' if parameters is None
        export_dir: Output directory
        replace_existing: If True, replace existing files
    
    Example:
        from main import quick_generate
        quick_generate(mode='random')
        # or to keep existing files:
        quick_generate(mode='mean', replace_existing=False)
    """
    # Create model
    model = CochleaModel(parameters=parameters, mode=mode)
    
    # Visualize
    visualizer = CochleaVisualizer(model)
    visualizer.plot_3d_model()
    
    # Export
    exporter = CochleaExporter(model)
    exporter.export_all(export_dir, replace_existing)
    
    # Show plots
    import matplotlib.pyplot as plt
    plt.show()
    
    return model


if __name__ == "__main__":
    sys.exit(main())