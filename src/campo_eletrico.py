import numpy as np
import matplotlib.pyplot as plt
import os
import json 

def load_charges(txt_filename="cargas.txt", json_filename="charges.json"):
    if not os.path.exists(json_filename):
        if not os.path.exists(txt_filename):
            raise FileNotFoundError(f"O arquivo '{txt_filename}' não existe.")
        if os.path.getsize(txt_filename) == 0:
            raise ValueError(f"O arquivo '{txt_filename}' está vazio.")
        charges = []
        with open(txt_filename, "r") as txt_file:
            for line in txt_file:
                try:
                    line = line.strip()
                    parts = line.split(" ")
                    pos_part = next((p for p in parts if p.startswith("pos:")), None)
                    if pos_part is None:
                        raise ValueError(f"Faltando campo 'pos' na linha: {line}")
                    pos_values = pos_part.split(":")[1].split(",")
                    pos = [float(val) for val in pos_values]
                    charge_part = next((p for p in parts if p.startswith("charge:")), None)
                    if charge_part is None:
                        raise ValueError(f"Faltando campo 'charge' na linha: {line}")
                    charge = float(charge_part.split(":")[1])
                    charges.append({"pos": pos, "charge": charge})
                except Exception as e:
                    raise ValueError(f"Erro ao processar a linha '{line}': {e}")
        with open(json_filename, "w") as json_file:
            json.dump(charges, json_file, indent=4)
        print(f"Arquivo '{txt_filename}' convertido para '{json_filename}'.")
    with open(json_filename, "r") as json_file:
        try:
            return json.load(json_file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar o JSON: {e}")

k = 8.9875517923e9  # Constante de Coulomb (em unidades apropriadas) N·m²/C²

def electric_field(q, r_pos, r_point):
    r = r_point - r_pos
    r_magnitude = np.linalg.norm(r)
    if r_magnitude == 0:
        return np.array([0, 0])
    return k * q * r / r_magnitude**3

def calculate_field(charges, x_range=(-20, 20), y_range=(-20, 20), resolution=50):
    x = np.linspace(*x_range, resolution)
    y = np.linspace(*y_range, resolution)
    X, Y = np.meshgrid(x, y)
    Ex, Ey = np.zeros(X.shape), np.zeros(Y.shape)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            point = np.array([X[i, j], Y[i, j]])
            for charge in charges:
                E = electric_field(charge["charge"], np.array(charge["pos"]), point)
                Ex[i, j] += E[0]
                Ey[i, j] += E[1]
    return X, Y, Ex, Ey

def plot_field(charges, X, Y, Ex, Ey):
    plt.figure(figsize=(8, 8))
    magnitude = np.sqrt(Ex**2 + Ey**2)
    # Encontrando o valor mínimo e máximo da magnitude do campo
    min_magnitude = np.min(magnitude)
    max_magnitude = np.max(magnitude)
    scale_factor = 2
    # Normalizando as setas de acordo com a magnitude
    Ex_norm = Ex * scale_factor / magnitude
    Ey_norm = Ey * scale_factor / magnitude
    quiver = plt.quiver(X, Y, Ex_norm, Ey_norm, magnitude, pivot='middle', cmap='coolwarm', scale=50)
    for charge in charges:
        color = 'red' if charge["charge"] > 0 else 'blue'
        plt.scatter(*np.array(charge["pos"]), color=color, s=150, label=f"q = {charge['charge']} C")  # Sem a divisão por 100
    plt.xlim(X.min(), X.max())
    plt.ylim(Y.min(), Y.max())
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title('Campo Elétrico Gerado por Cargas Pontuais')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    cbar = plt.colorbar(quiver, label='Magnitude do Campo Elétrico (N/C)')
    cbar.set_ticks([min_magnitude, (min_magnitude + max_magnitude) / 2, max_magnitude])  
    cbar.ax.tick_params(labelsize=10) 
    cbar.ax.invert_yaxis()  
    plt.legend()
    plt.grid()
    plt.show()

