def calculate_polynomial(soc: float) -> float:
    if soc <= 1.0:
        soc = soc * 100.0

    coeffs = [2.74e-13, -8.39e-11, 8.38e-9,
              -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
    result = 0.0
    for i, coeff in enumerate(coeffs):
        result += coeff * (soc ** (7 - i))

    return max(0.0, result)
    
def calculate_stress_amplitude(avg_soc: float, avg_dod: float) -> float:
    soc_min = max(0.0, avg_soc - avg_dod / 2.0)
    soc_max = min(1.0, avg_soc + avg_dod / 2.0)
    
    poly_max = calculate_polynomial(soc_max)
    poly_min = calculate_polynomial(soc_min)
    
    result = poly_max - poly_min
    
    if avg_dod >= 0.99:
        print(
            f"Stress Debug: soc_min={soc_min:.3f}, soc_max={soc_max:.3f}")
        print(
            f"Stress Debug: poly_min={poly_min:.8f}, poly_max={poly_max:.8f}, result={result:.8f}")
    
    return result
    
test_cases = [
    (20, 0.05),  
    (40, 0.05),  
    (80, 0.05), 
    (50, 0.20),  
    (50, 0.50),  
]

for soc_pct, dod in test_cases:
    stress = calculate_stress_amplitude(soc_pct/100.0, dod)
    print(f"SoC {soc_pct}%, DoD {dod*100}%: σ = {stress:.6f}")


def test_expansion_function():
    test_points = [37.5, 40, 42.5, 50, 80]
    for soc in test_points:
        poly_val = calculate_polynomial(soc/100.0)
        print(f"SoC {soc}%: f_exp = {poly_val:.6f}")
    
    f_42_5 = calculate_polynomial(0.425)
    f_37_5 = calculate_polynomial(0.375) 
    stress_manual = f_42_5 - f_37_5
    print(f"Manual calculation: f_exp(42.5%) - f_exp(37.5%) = {f_42_5:.6f} - {f_37_5:.6f} = {stress_manual:.6f}")

def find_minimum_slope():
    test_range = range(30, 60, 2)  # 30% to 58% in 2% steps
    
    for soc in test_range:
        soc_low = (soc - 1) / 100.0
        soc_high = (soc + 1) / 100.0
        
        poly_low = calculate_polynomial(soc_low)
        poly_high = calculate_polynomial(soc_high)
        
        slope = (poly_high - poly_low) / 0.02  # 2% increment
        print(f"SoC {soc}%: slope = {slope:.6f}")


def find_actual_minimum():
    min_slope = float('inf')
    min_soc = 0
    
    for soc_pct in range(350, 450, 1):  # 35.0% to 44.9% in 0.1% steps
        soc_low = (soc_pct - 0.5) / 1000.0
        soc_high = (soc_pct + 0.5) / 1000.0
        
        poly_low = calculate_polynomial(soc_low)
        poly_high = calculate_polynomial(soc_high)
        slope = (poly_high - poly_low) / 0.001
        
        if slope < min_slope:
            min_slope = slope
            min_soc = soc_pct / 10.0
    
    print(f"Minimum slope at SoC {min_soc}%: slope = {min_slope:.6f}")
    
    stress_at_min = calculate_stress_amplitude(min_soc/100.0, 0.05)
    print(f"Stress amplitude at my minimum: {stress_at_min:.6f}")



def test_different_scaling():
    soc_40_fraction = 0.40
    soc_40_percent = 40.0
    
    result1 = calculate_polynomial(soc_40_fraction)
    
    coeffs = [2.74e-13, -8.39e-11, 8.38e-9, -2.39e-7, -5.05e-6, 9.70e-5, 0.02, -6.19e-3]
    result2 = 0.0
    for i, coeff in enumerate(coeffs):
        result2 += coeff * (soc_40_percent ** (7 - i))
    result2 = max(0.0, result2)
    
    print(f"Method 1 : {result1:.6f}")
    print(f"Method 2 : {result2:.6f}")
    print(f"Ratio: {result1/result2:.2f}")


