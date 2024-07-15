PACE_COEFFICIENT = 48
UNKNOWN_STDDEV = 2.3
REPLACEMENT_PLAYER = -2.0

bpm_coefficients = {
    'Pos 1': {
        'AdjPt': 0.860,
        'FGA': -0.560,
        'FTA': -0.246,
        '3P': 0.389,
        'AST': 0.580,
        'TO':-0.964,
        'ORB':0.613,
        'DRB':0.116,
        'TRB':0.000,
        'STL':1.369,
        'BLK':1.327,
        'PF':-0.367
    },
                                                
    'Pos 5': {
        'AdjPt': 0.860,
        'FGA': -0.780,
        'FTA': -0.343,
        '3P': 0.389,
        'AST': 1.034,
        'TO':-0.964,
        'ORB':0.181,
        'DRB':0.181,
        'TRB':0.000,
        'STL':1.008,
        'BLK':0.703,
        'PF':-0.367
    }
}

obpm_coeffiecients = {
    'Pos 1': {
        'AdjPt': 0.605,
        'FGA': -0.330,
        'FTA': -0.145,
        '3P': 0.477,
        'AST': 0.476,
        'TO':-0.579,
        'ORB':0.606,
        'DRB':-0.112,
        'TRB':0.000,
        'STL':0.177,
        'BLK':0.725,
        'PF':-0.439
    },
                                                
    'Pos 5': {
        'AdjPt': 0.605,
        'FGA': -0.472,
        'FTA': -0.208,
        '3P': 0.477,
        'AST': 0.476,
        'TO':-0.882,
        'ORB':0.422,
        'DRB':0.103,
        'TRB':0.000,
        'STL':0.294,
        'BLK':0.097,
        'PF':-0.439
    }
}

pos_coefficients = {
    'INT':2.130,
    '%TRB':8.668,
    '%STL':-2.486,
    '%PF':0.992,
    '%AST':-3.536,
    '%BLK':1.667,
}

off_role_coefficients = {
    'INT':6.00,
    '%AST': -6.642,
    '%Thresh': -8.544,
    'PtThresh': -0.33
}

pos_constants = {
    'Pos 1': -0.818,
    'Pos 3': 0,
    'Pos 5': 0,
    'Slope': 1.387
}

off_pos_constants = {
    'Pos 1': -1.698,
    'Pos 3': 0,
    'Pos 5': 0,
    'Slope': 0.43 
}
    