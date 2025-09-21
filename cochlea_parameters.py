"""
Cochlea Parameters Module
Handles parameter generation and patient data for cochlea modeling
"""

import numpy as np


class CochleaParameters:
    """Manages cochlea parameters and coefficient matrices."""
    
    def __init__(self):
        self.coefs = self._initialize_coefficients()
    
    def _initialize_coefficients(self):
        """Initialize coefficient matrices for the cochlea model."""
        coefs = {}
        
        coefs['height'] = np.array([
            [-2.025562262381, 0.308684774745994, -0.0245970612199774, 0.00093743547596123, -6.49142944919421e-06],
            [-0.483933701821246, 0.150263587271025, -0.0249700764778651, 0.00184112837255666, -4.68696577096306e-05],
            [0.0936906993853392, 0.0485929242340616, -0.0111388827166082, 0.000852542615496957, -2.39666478178502e-05],
            [0.437215616236419, -0.609467318753365, 0.147019129524084, -0.012345472153677, 0.000341806092537278],
            [0.19884386428529, 0.0706538846984097, -0.0490269768729332, 0.00553612473205947, -0.000178036145575138]
        ])
        
        coefs['modiolus'] = np.array([
            [-0.0972007477234853, 0.0652777719428317, 0.00579010295961996, -0.000410053336041606],
            [0.745407586062517, -0.297795950930632, 0.0353079060718429, -0.00125774660897636],
            [0.349940654425921, -0.0488173880945223, 0.00235713329581525, -3.38189250648794e-05],
            [0.0567728210841444, 0.115930983938798, -0.0170603835499829, 0.000605305012135639],
            [-0.0613995454924607, 0.170502985259421, -0.0267552502171719, 0.00111572946871731]
        ])
        
        coefs['turns'] = np.array([963.166310413576, 6.37772934525638, -26.9585473096045, 
                                  -36.3953582023656, 66.9416454453684])
        
        return coefs
    
    def generate_parameters(self, mode='mean'):
        """
        Generate cochlea parameters based on specified type.
        
        Args:
            mode: 'mean' for average values or 'random' for randomized values
            
        Returns:
            numpy array with 4 parameters [A1, B1, A2, B2]
        """
        if mode == 'mean':
            return np.array([5.97, 3.95, 3.26, 2.85])
            
        elif mode == 'random':
            # Correlation matrix for realistic parameter relationships
            correlation_matrix = np.array([
                [1.0, 0.53476, -0.12441, -0.07296],
                [0.53476, 1.0, 0.11668, -0.43748],
                [-0.12441, 0.11668, 1.0, 0.57846],
                [-0.07296, -0.43748, 0.57846, 1.0]
            ])
            
            # Generate correlated random values
            mean_vector = np.ones(4)
            random_values = np.random.multivariate_normal(mean_vector, correlation_matrix)
            
            # Transform to proper distributions with realistic means and standard deviations
            means = [5.97, 3.95, 3.26, 2.85]
            stds = [0.36, 0.35, 0.28, 0.33]
            
            parameters = np.zeros(4)
            for i in range(4):
                # Use inverse normal CDF to get proper distribution
                uniform_value = np.random.normal(0, 1)
                parameters[i] = np.random.normal(means[i], stds[i])
            
            return parameters
        else:
            raise ValueError("Mode must be 'mean' or 'random'")
    
    def validate_parameters(self, parameters):
        """
        Validate that parameters are within reasonable bounds.
        
        Args:
            parameters: 4-element array [A1, B1, A2, B2]
            
        Returns:
            bool: True if valid, raises ValueError if not
        """
        if len(parameters) != 4:
            raise ValueError("Parameters must be a 4-element array")
        
        # Check reasonable bounds based on anatomical constraints
        bounds = {
            'A1': (4.0, 8.0),  # Base width
            'B1': (2.5, 5.5),  # Secondary base measurement  
            'A2': (2.0, 4.5),  # Mid-cochlea width
            'B2': (1.5, 4.0)   # Apical measurement
        }
        
        param_names = ['A1', 'B1', 'A2', 'B2']
        for i, (name, value) in enumerate(zip(param_names, parameters)):
            min_val, max_val = bounds[name]
            if not min_val <= value <= max_val:
                raise ValueError(f"{name} = {value} is outside reasonable bounds [{min_val}, {max_val}]")
        
        return True
    
    def get_patient_parameters(self, patient_id=None):
        """
        Load patient-specific parameters if available.
        
        Args:
            patient_id: Patient identifier (for future database integration)
            
        Returns:
            numpy array with 4 parameters or None if not found
        """
        # Placeholder for future patient database integration
        # For now, returns None to indicate no patient data
        return None
    
    def save_parameters(self, parameters, filename):
        """Save parameters to file."""
        np.savetxt(filename, parameters, fmt='%.6f', 
                   header='A1, B1, A2, B2', delimiter=',', comments='# ')
    
    def load_parameters(self, filename):
        """Load parameters from file."""
        return np.loadtxt(filename, delimiter=',')