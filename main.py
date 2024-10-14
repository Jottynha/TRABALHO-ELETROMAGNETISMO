import pygame
import math
import tkinter as tk
from tkinter import simpledialog, messagebox

pygame.init()

#CORES
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
#TELA
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulador da Lei de Coulomb")
#FONTES
font = pygame.font.SysFont("Times New Roman", 20)
bold_font = pygame.font.SysFont("Times New Roman", 20, bold=True) 
underline_font = pygame.font.SysFont("Times New Roman", 50, italic=True)
#IMAGENS
background_image = pygame.image.load("fig/background.jpg").convert()
law_image = pygame.image.load("fig/CoulombsLaw.png") 
image_size = (512, 410)
law_image = pygame.transform.scale(law_image, image_size)
image_rect = law_image.get_rect()
image_rect.center = (width // 2, height // 2)
#BOTÔES
button_rect = pygame.Rect(10, 10, 120, 30)  
button_color = (0, 128, 255)
button_text = font.render("Informações", True, BLACK)
#INTERFACES
def show_info_window():
    root = tk.Tk()
    root.title("Informações do Programa")
    message = (
        "Simulador da Lei de Coulomb\n\n"
        "Este programa simula a interação entre cargas elétricas segundo a Lei de Coulomb.\n"
        "Você pode adicionar, editar e visualizar as forças atuantes entre as cargas.\n\n"
        "Comandos:\n"
        "Pressione 'A' para adicionar uma carga\n"
        "Pressione 'C' para editar uma carga\n"
        "Clique em uma carga para ver as forças\n"
        "Pressione 'R' para reiniciar a simulação."
    )
    label = tk.Label(root, text=message, padx=10, pady=10)
    label.pack()
    root.mainloop()



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
        pygame.draw.line(screen, BLACK, (x, 0), (x, height))
    for y in range(0, height, SCALE):
        pygame.draw.line(screen, BLACK, (0, y), (width, y))
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
        pygame.draw.circle(screen, BLACK, (pos_x, pos_y), 20, 2)  # Contorno

        
        # Desenha o número da carga dentro do círculo
        charge_number_text = font.render(str(charge['number']), True, WHITE)
        screen.blit(charge_number_text, (pos_x - charge_number_text.get_width() // 2, pos_y - charge_number_text.get_height() // 2))


def draw_force_vectors():
    for i in range(len(charges)):
        total_force_x = 0
        total_force_y = 0
        
        for j in range(len(charges)):
            if i != j:
                force = calculate_force(charges[i], charges[j])
                total_force_x += force[0]
                total_force_y += force[1]

        # Calcula a magnitude total da força
        total_force_magnitude = math.sqrt(total_force_x**2 + total_force_y**2)
        
        pos_x1 = int(charges[i]['pos'][0] * SCALE + width // 2)
        pos_y1 = int(height // 2 - charges[i]['pos'][1] * SCALE)

        # Normaliza o vetor para que tenha um comprimento máximo proporcional ao total da força
        if total_force_magnitude > 0:
            unit_fx = total_force_x / total_force_magnitude
            unit_fy = total_force_y / total_force_magnitude
            # Aumenta o comprimento do vetor proporcionalmente à força total
            scaled_length = min(total_force_magnitude * 0.0001, VECTOR_LENGTH)
        else:
            continue 

        # Calcula o ponto final da seta baseado na direção da força
        end_x = pos_x1 + unit_fx * scaled_length
        end_y = pos_y1 - unit_fy * scaled_length
        
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
    total_force_x = 0
    total_force_y = 0

    for other_charge in charges:
        if other_charge != q:
            force = calculate_force(q, other_charge)
            forces.append(
                f"Força entre carga {q['number']} e carga {other_charge['number']}:\n"
                f"  Fx = {force[0]:.2e} N\n"
                f"  Fy = {force[1]:.2e} N\n"
            )
            total_force_x += force[0]
            total_force_y += force[1]

    # Calcular a magnitude total da força uma vez
    total_force_magnitude = math.sqrt(total_force_x**2 + total_force_y**2)

    # Adiciona a força total na lista de forças
    if forces:  # Verifica se há forças atuantes
        forces.append(
            f"Força Total atuante na carga {q['number']}:\n"
            f"  Fx_total = {total_force_x:.2e} N\n"
            f"  Fy_total = {total_force_y:.2e} N\n"
            f"  Magnitude_total = {total_force_magnitude:.2e} N\n"
        )
    else:
        forces.append("Sem Forças Atuantes")

    # Exibe as forças em uma janela
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
        if distance < 20:
            show_forces(charge)


# Loop principal
running = True
clock = pygame.time.Clock()
# Variável para controlar a tela inicial
show_intro = True

# Função para desenhar a tela inicial
def draw_intro():
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))
    title_text = underline_font.render("Simulador da Lei de Coulomb", True, BLACK)
    instructions_text = bold_font.render("Pressione 'Enter' para Iniciar", True, BLACK)
    commands_text = bold_font.render("Comandos:", True, BLACK)
    command1_text = font.render("Pressione 'A' para adicionar uma carga", True, BLACK)
    command2_text = font.render("Pressione 'C' para editar uma carga", True, BLACK)
    command3_text = font.render("Clique em uma carga para ver as forças", True, BLACK)

    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 4))
    screen.blit(instructions_text, (width // 2 - instructions_text.get_width() // 2, height // 2))
    screen.blit(commands_text, (width // 2 - commands_text.get_width() // 2, height // 2 + 30))
    screen.blit(command1_text, (width // 2 - command1_text.get_width() // 2, height // 2 + 60))
    screen.blit(command2_text, (width // 2 - command2_text.get_width() // 2, height // 2 + 90))
    screen.blit(command3_text, (width // 2 - command2_text.get_width() // 2, height // 2 + 120))

def edit_charge_interface():
    charge_number = simpledialog.askinteger("Editar Carga", "Insira o número da carga:")
    if charge_number is not None:
        if 1 <= charge_number <= len(charges):
            charge = charges[charge_number - 1]  # Obtém a carga correspondente ao número

            new_charge = simpledialog.askfloat("Editar Carga", "Insira o novo valor da carga (C):", initialvalue=charge['charge'])
            if new_charge is not None:
                charge['charge'] = new_charge  # Atualiza a carga

            new_position = simpledialog.askstring("Editar Carga", "Insira a nova posição (x,y):", initialvalue=f"{charge['pos'][0]},{charge['pos'][1]}")
            if new_position:
                try:
                    x, y = map(float, new_position.split(","))
                    # Verifica se a nova carga colide com alguma carga existente
                    for existing_charge in charges:
                        if existing_charge != charge:  # Não verifica a própria carga
                            distance = math.sqrt((existing_charge['pos'][0] - x)**2 + (existing_charge['pos'][1] - y)**2)
                            if distance < 2:  # A distância mínima deve ser maior que o raio (20 pixels, então 2 é o limite)
                                messagebox.showerror("Erro", "A nova posição colide com uma carga existente. Tente outra posição.")
                                return  # Retorna sem atualizar a carga

                    charge['pos'] = [x, y]  # Atualiza a posição
                except ValueError:
                    messagebox.showerror("Erro", "Posição inválida. Use o formato x,y.")
        else:
            messagebox.showerror("Erro", "Número da carga inválido.")


while running:
    if show_intro:
        draw_intro()  # Chama a nova função para desenhar a tela inicial
    elif not simulation_running:
        screen.fill(LIGHT_GRAY)
        screen.blit(background_image, (0, 0))  
        title_text = font.render("Lei de Coulomb", True, BLACK)
        screen.blit(law_image, image_rect.topleft)
        outline_rect = image_rect.inflate(10, 10) 
        pygame.draw.rect(screen, BLACK, outline_rect, 2)
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height - 550))        
        pygame.display.update()
    else:
        screen.fill(DARK_GRAY)
        draw_grid()
        draw_charges()
        draw_force_vectors()
        pygame.draw.rect(screen, button_color, button_rect)
        outline_rect = button_rect.inflate(5, 5)
        pygame.draw.rect(screen, BLACK, outline_rect, 2)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))  # Centraliza o texto no botão
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if show_intro and event.key == pygame.K_RETURN:
                show_intro = False  # Oculta a tela inicial
            elif event.key == pygame.K_RETURN and not simulation_running:
                simulation_running = True
            elif event.key == pygame.K_ESCAPE and simulation_running:
                simulation_running = False
            elif event.key == pygame.K_a and simulation_running:
                add_charge_interface()
            elif event.key == pygame.K_c and simulation_running:
                edit_charge_interface()  
            elif event.key == pygame.K_r:  
                charges.clear()
        elif event.type == pygame.MOUSEBUTTONDOWN and simulation_running:
            handle_click(pygame.mouse.get_pos())
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):  # Verifica se o botão foi clicado
                show_info_window()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
