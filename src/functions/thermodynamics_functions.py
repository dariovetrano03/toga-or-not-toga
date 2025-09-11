cp0 = 946

cp1 = 0.1884

cp_hot0 = 54.418

cp_hot1 = 0.07535

alpha_st = 14.7 # [-] stoichiometric air-to-fuel ratio

R = 287 # [J/kg/K]

eta_burner = 0.99 # [-] Combustion efficiency

H_i = 43.3e6 # [J/kg] Lower heating value of kerosene

alpha0 = 41.6 # [-] air-to-fuel ratio (from Ex. 4). Assumed constant


def calculate_cp(temp): # FOR AIR WITH gamma = 1.4

    cp = cp0 + cp1 * temp # [J/kg/K]

    return cp 

def calculate_R_hot(temp, alpha = alpha0): # FOR combustion gases with gamma = 1.4
    
    A = ( 1 + alpha_st ) / ( 1 + alpha ) 

    R_hot = R * (1 + 0.06 * A)

    return R_hot


def calculate_cp_hot(temp, alpha = alpha0): # FOR combustion gases WITH gamma = 1.4

    cp = calculate_cp(temp)

    A = ( 1 + alpha_st ) / ( 1 + alpha ) 

    cp_hot = cp + A * ( cp_hot0 + cp_hot1 * temp ) # [J/kg/K]

    return cp_hot 


def calculate_T2_tot(beta_c, T1_tot, eta_comp = 0.98 , gamma = 1.4, max_iter = 5, tol = 1e-4): # TODO eta_comp from compressor map

    T2_old = T1_tot
    T2_new = 0

    cp_start = calculate_cp(T1_tot)

    for _ in range(max_iter):

        cp_avg = calculate_cp((T2_old + T1_tot) / 2) # 

        L_comp = cp_start * T1_tot / eta_comp * (beta_c ** ((gamma - 1) / gamma / 0.85) - 1) / eta_comp

        T2_new = T1_tot + L_comp / cp_avg

        if abs(T2_new - T2_old) / abs(T2_old) < tol:

            break

        T2_old = T2_new
        
    return T2_new
 

def calculate_T3_tot(T2_tot, alpha = alpha0, max_iter = 5, tol = 1e-4):

    T3_old = T2_tot
    T3_new = 0

    f0 = 1 / alpha0

    cp_start = calculate_cp(T2_tot)

    for _ in range(max_iter):

        cp_hot_avg = calculate_cp_hot((T3_old + T2_tot) / 2, alpha = alpha0) 

        T3_new = cp_start / cp_hot_avg * T2_tot / ( 1 + f0 ) + H_i * eta_burner * f0 / ( 1 + f0 ) / cp_hot_avg 
        
        if abs(T3_new - T3_old) / abs(T3_old) < tol:
            break
        
        T3_old = T3_new
        
    return T3_new
