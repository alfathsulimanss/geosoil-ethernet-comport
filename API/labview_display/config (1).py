# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'projectdata'
}

# Test Type Configuration - Column mappings
TEST_TYPE_COLUMNS = {
    1: {
        'name': 'Triaxial Compression Test (Drained)',
        'columns': ['Cell Pressure', 'Back Pressure', 'Volume Change', 'Load', 'Displacement', 
                   'Pore Pressure', 'Change of Pore Pressure', 'Change in Volume', 
                   'Axial Load Change', 'Change in Length', 'Deviator Stress', 'Axial Strain']
    },
    2: {
        'name': 'Triaxial Compression Test (Undrained)',
        'columns': ['Cell Pressure', 'Vertical Load', 'Displacement', 'Pore Pressure', 
                   'Change Pore Pressure', 'Axial Load Change', 'Change in Length', 
                   'Deviator Stress', 'Axial Strain']
    },
    3: {
        'name': 'Direct Shear Test',
        'columns': ['Vertical Load', 'Vertical Displacement', 'Horizontal Load', 
                   'Horizontal Displacement', 'S Length Change', 'Shear Strain', 
                   'H Load Change', 'Normal Stress', 'Shear Stress']
    },
    4: {
        'name': 'Permeability Test',
        'columns': ['Cell Pressure', 'Back Pressure', 'Inlet Volume', 'Pore Pressure', 
                   'Back Pressure 2', 'Outlet Volume', 'Inlet Volume Change', 
                   'Outlet Volume Change', 'Gradient Pressure', 'Inlet Flow', 'Outlet Flow', 'Mean Volume']
    },
    5: {
        'name': 'Consolidation Test',
        'columns': ['Load', 'Displacement', 'Vertical Stress', 'Height Settlement', 'Total Height Settlement']
    },
    6: {
        'name': 'B-Value Test',
        'columns': ['Cell Pressure', 'Back Pressure', 'Volume Change', 'Pore Pressure', 
                   'B-Value', 'Change Pore Pressure', 'Change in Volume']
    },
    7: {
        'name': 'Hollow Cylinder Test',
        'columns': ['Cell Pressure', 'Pore Water Pressure', 'Back Pressure', 'Volume Change 1', 
                   'Back Pressure 2', 'Volume Change 2', 'Vertical Load', 'Vertical Displacement', 
                   'Horizontal Load', 'Horizontal Displacement']
    },
    8: {
        'name': 'Unconfined Compression Test',
        'columns': ['Load', 'Displacement', 'Vertical Stress', 'Load Change', 'Change in Length', 'Deviator Stress', 'Axial Strain']
    },
    9: {
        'name': 'Pore Pressure Dissipation Test',
        'columns': ['Cell Pressure', 'Back Pressure', 'Volume Change', 'Pore Pressure', 
                   'Change Pore Pressure', 'Pore Pressure Dissipation', 'Change in Volume']
    },
    10: {
        'name': 'Direct Tension Test',
        'columns': ['Vertical Load', 'Vertical Stress']
    }
}
