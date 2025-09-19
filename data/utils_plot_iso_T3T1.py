import numpy as np

def mass_flow_per_area_from_M(pt, Tt, M, gamma, R):
    f_M = np.sqrt(gamma) * M * ( 1 + (gamma - 1) / 2 * M ** 2 ) ** ( - ( ( gamma + 1 ) / ( 2 * (gamma - 1) ) ) )
    mf = pt / np.sqrt(R * Tt) * f_M
    return mf, f_M

def p_over_pt_from_M(M, gamma):
    """
    total pressure definition
    """
    return (1 + (gamma-1)/2 * M**2)**(-gamma/(gamma-1))

def M_from_p_over_pt(p_over_pt, gamma):
    p_over_pt = np.asarray(p_over_pt)
    if np.any(p_over_pt <= 0) or np.any(p_over_pt > 1):
        raise ValueError("p_over_pt must be in the interval (0, 1].")
    M_squared = (2 / (gamma - 1)) * (p_over_pt**(-(gamma - 1)/gamma) - 1)
    M = np.sqrt(M_squared)
    M = np.where(M < 1.0, M, np.nan)
    return M