import numpy as np
import random

def distanza(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def rssi_from_distance(d, A=-50, n=2, noise_std=2):
    """
    Modello RSSI log-distance + rumore gaussiano
    """
    if d <= 0: 
        d = 0.1
    rssi = A - 10 * n * np.log10(d)
    rssi += random.gauss(0, noise_std)  # rumore
    return rssi

def distance_from_rssi(rssi, A=-50, n=2):
    return 10 ** ((A - rssi) / (10 * n))

# Posizioni dei ricevitori (in metri)
receivers = [(0, 0), (5, 0), (2.5, 5)]

# Posizione della pallina (puoi cambiarla a ogni test)
ball = (3, 2)

# Simuliamo RSSI misurati con rumore
rssi_values = [rssi_from_distance(distanza(r, ball)) for r in receivers]

print("RSSI misurati:", rssi_values)

# Convertiamo RSSI -> distanze stimate
d_stimati = [distance_from_rssi(rssi) for rssi in rssi_values]

print("Distanze stimate:", d_stimati)

# Trilaterazione
def trilaterazione(receivers, d_stimati):
    def error(point):
        return sum((distanza(point, r) - d) ** 2 for r, d in zip(receivers, d_stimati))
    best = min(
        [(x, y) for x in np.linspace(0, 5, 50) for y in np.linspace(0, 5, 50)],
        key=error
    )
    return best

stima = trilaterazione(receivers, d_stimati)
print("Posizione stimata:", stima)
print("Posizione reale:", ball)
