import math

class ElectrostaticsSimulation:
    def __init__(self, charges):
        self.charges = charges

    def calculate_force(self, q1, q2):
        k = 8.99e9  # Constante eletrostática (N·m²/C²)
        dx = q2['pos'][0] - q1['pos'][0]
        dy = q2['pos'][1] - q1['pos'][1]
        distance = math.sqrt(dx**2 + dy**2)

        min_distance = 1.0e-10  # Distância mínima para evitar infinito
        if distance < min_distance:
            distance = min_distance  

        force_magnitude = k * abs(q1['charge'] * q2['charge']) / distance**2    
        angle = math.atan2(abs(dy),abs(dx))
        force_x = math.cos(angle) * force_magnitude
        force_y = math.sin(angle) * force_magnitude


        # Repulsão para cargas iguais, atração para cargas opostas
        sign_x = math.copysign(1,dx)
        sign_y = math.copysign(1,dy)
        if q1['charge'] * q2['charge'] > 0:
            return [sign_x*force_x, sign_y*force_y]  # Repulsão
        if q1['charge'] * q2['charge'] > 0:
            return [-force_x, -force_y]  # Repulsão
        else:
            return [force_x, force_y]  # Atração

    def compute_forces(self):
        forces = []
        for i in range(len(self.charges)):
            total_force_x = 0
            total_force_y = 0

            for j in range(len(self.charges)):
                if i != j:
                    force = self.calculate_force(self.charges[i], self.charges[j])
                    total_force_x += force[0]
                    total_force_y += force[1]
                    print(force,total_force_x,total_force_y)
            forces.append((total_force_x, total_force_y))
        return forces

# Definição das cargas
charges = [
    {'pos': (0.0, 0.0), 'charge': 0.000000002},
    {'pos': (1.0, 0.0), 'charge': 0.000000003},
    {'pos': (0.4494897428, 0.0), 'charge': 2.0}
]

# Criando a simulação
simulation = ElectrostaticsSimulation(charges)
forces = simulation.compute_forces()

# Exibindo os resultados
for i, (fx, fy) in enumerate(forces):
    print(f"Força resultante sobre a carga {i + 1}: Fx = {fx:.2e} N, Fy = {fy:.2e} N")
