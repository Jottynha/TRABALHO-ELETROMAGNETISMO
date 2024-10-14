import pygame
import math
import tkinter as tk
from tkinter import simpledialog, messagebox

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulador da Lei de Coulomb")
font = pygame.font.SysFont("Arial", 20)

LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Constantes
k = 8.99e9  # Constante de Coulomb
SCALE = 20  # Escala para o desenho (1 unidade no plano = SCALE pixels)
VECTOR_LENGTH = 50  # Comprimento máximo dos vetores em pixels

# Lista para armazenar as cargas
charges = []
simulation_running = False

# Função para calcular a força entre duas cargas
def calculate_force(q1, q2):
    dx = q2['pos'][0] - q1['pos'][0]
    dy = q2['pos'][1] - q1['pos'][1]
    distance = math.sqrt(dx**2 + dy**2)

    if distance < 10:  # Evitar que as partículas colidam completamente
        distance = 10

    force_magnitude = k * abs(q1['charge'] * q2['charge']) / distance**2
    angle = math.atan2(dy, dx)

    force_x = math.cos(angle) * force_magnitude
    force_y = math.sin(angle) * force_magnitude

    # Se as cargas forem do mesmo sinal, força de repulsão (afasta)
    if q1['charge'] * q2['charge'] > 0:
        return [-force_x, -force_y]  # Repulsão
    else:
        return [force_x, force_y]  # Atração


def draw_grid():
    for x in range(0, width, SCALE):
        pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, height))
    for y in range(0, height, SCALE):
        pygame.draw.line(screen, DARK_GRAY, (0, y), (width, y))
    pygame.draw.line(screen, BLACK, (width // 2, 0), (width // 2, height), 2)  # Eixo Y
    pygame.draw.line(screen, BLACK, (0, height // 2), (width, height // 2), 2)  # Eixo X


def draw_charges():
    for charge in charges:
        # Converte a posição para o centro do plano
        pos_x = int(charge['pos'][0] * SCALE + width // 2)
        pos_y = int(height // 2 - charge['pos'][1] * SCALE)
        
        # Define a cor com base no sinal da carga
        color = RED if charge['charge'] > 0 else BLUE
        
        # Desenha a carga (círculo)
        pygame.draw.circle(screen, color, (pos_x, pos_y), 20)
        
        # Desenha o número da carga dentro do círculo
        charge_number_text = font.render(str(charge['number']), True, WHITE)
        screen.blit(charge_number_text, (pos_x - charge_number_text.get_width() // 2, pos_y - charge_number_text.get_height() // 2))


def draw_force_vector(q1, q2):
    pos_x1 = int(q1['pos'][0] * SCALE + width // 2)
    pos_y1 = int(height // 2 - q1['pos'][1] * SCALE)
    pos_x2 = int(q2['pos'][0] * SCALE + width // 2)
    pos_y2 = int(height // 2 - q2['pos'][1] * SCALE)

    # Calcula a força entre as duas cargas
    force = calculate_force(q1, q2)

    # Desenha o vetor de força partindo de q1 em direção à força calculada
    force_magnitude = math.sqrt(force[0]**2 + force[1]**2)

    # Normaliza o vetor para que tenha um comprimento máximo de VECTOR_LENGTH
    unit_fx = force[0] / force_magnitude
    unit_fy = force[1] / force_magnitude

    # Ajusta o tamanho do vetor para ser proporcional, mas limitado
    scaled_length = min(force_magnitude * 0.0001, VECTOR_LENGTH)

    # Calcula o ponto final da seta baseado na direção da força
    end_x = pos_x1 + unit_fx * scaled_length
    end_y = pos_y1 - unit_fy * scaled_length

    # Desenhar a linha do vetor
    pygame.draw.line(screen, GREEN, (pos_x1, pos_y1), (end_x, end_y), 2)

    # Desenhar a seta na extremidade do vetor
    arrow_length = 10
    arrow_angle = math.pi / 6  # Ângulo da seta
    angle = math.atan2(-unit_fy, unit_fx)  # Ângulo baseado na direção do vetor de força

    # Posição dos dois pontos que formam a seta
    arrow_point1 = (
        end_x - arrow_length * math.cos(angle + arrow_angle),
        end_y - arrow_length * math.sin(angle + arrow_angle)
    )
    arrow_point2 = (
        end_x - arrow_length * math.cos(angle - arrow_angle),
        end_y - arrow_length * math.sin(angle - arrow_angle)
    )

    # Desenha a seta
    pygame.draw.polygon(screen, GREEN, [arrow_point1, arrow_point2, (end_x, end_y)])


def show_forces(q):
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter
    forces = []
    for other_charge in charges:
        if other_charge != q:
            force = calculate_force(q, other_charge)
            forces.append(f"Força entre carga {q['number']} e carga {other_charge['number']}: "
              f"Fx = {force[0]:.2e} N, Fy = {force[1]:.2e} N")

    
    messagebox.showinfo("Forças Atuantes", "\n".join(forces))
    root.destroy()


def add_charge_interface():
    charge = simpledialog.askfloat("Adicionar Carga", "Insira o valor da carga (C):")
    if charge is not None:
        position = simpledialog.askstring("Adicionar Carga", "Insira a posição (x,y):")
        if position:
            try:
                x, y = map(float, position.split(","))
                # Verifica se a nova carga colide com alguma carga existente
                for existing_charge in charges:
                    distance = math.sqrt((existing_charge['pos'][0] - x)**2 + (existing_charge['pos'][1] - y)**2)
                    if distance < 2:  # A distância mínima deve ser maior que o raio (20 pixels, então 2 é o limite)
                        messagebox.showerror("Erro", "A nova carga colide com uma carga existente. Tente outra posição.")
                        return  # Retorna sem adicionar a carga
                
                charge_number = len(charges) + 1
                charges.append({'charge': charge, 'pos': [x, y], 'number': charge_number})
            except ValueError:
                messagebox.showerror("Erro", "Posição inválida. Use o formato x,y.")

# Função para detectar cliques na carga
def handle_click(pos):
    for charge in charges:
        pos_x = int(charge['pos'][0] * SCALE + width // 2)
        pos_y = int(height // 2 - charge['pos'][1] * SCALE)
        distance = math.sqrt((pos_x - pos[0])**2 + (pos_y - pos[1])**2)
        if distance < 10:
            show_forces(charge)


# Loop principal
running = True
clock = pygame.time.Clock()

while running:
    if not simulation_running:
        screen.fill(WHITE)
        title_text = font.render("Simulador da Lei de Coulomb", True, BLACK)
        start_text = font.render("Pressione 'Enter' para Iniciar", True, BLACK)
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 3))
        screen.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 2))
    else:
        screen.fill(WHITE)
        draw_grid()
        draw_charges()
        for i in range(len(charges)):
            for j in range(len(charges)):
                if i != j:
                    draw_force_vector(charges[i], charges[j])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not simulation_running:
                simulation_running = True
            elif event.key == pygame.K_ESCAPE and simulation_running:
                simulation_running = False
            elif event.key == pygame.K_a and simulation_running:
                add_charge_interface()
        elif event.type == pygame.MOUSEBUTTONDOWN and simulation_running:
            handle_click(pygame.mouse.get_pos())

    pygame.display.update()
    clock.tick(60)

pygame.quit()
