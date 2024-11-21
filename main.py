import pygame
import math
import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog, messagebox
import threading

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

width, height = 1300, 700
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

#BOTÕES

button_rect = pygame.Rect(10, 10, 120, 30)  
button_color = (0, 128, 255)
button_text = font.render("Informações", True, BLACK)

#INTERFACE DE ADICIONAR CARGA

input_active = [False, False]
input_texts = ["", ""]
input_box_width = 200
input_box_height = 30
margin_top = 20
margin_right = 20
input_start_x = width - input_box_width - margin_right
input_start_y = margin_top
input_boxes = [
    pygame.Rect(input_start_x, input_start_y, input_box_width, input_box_height),
    pygame.Rect(input_start_x, input_start_y + 50, input_box_width, input_box_height)
]
add_button = pygame.Rect(input_start_x, input_start_y + 110, 100, 30)
input_labels = ["Valor da Carga (C)", "Posição (x, y)"]
label_surfaces = [font.render(label, True, (0, 0, 0)) for label in input_labels]

#INTERFACES

def show_info_window():
    def open_window():
        root = tk.Tk()
        root.title("Informações do Programa")

        message = (
            "Simulador da Lei de Coulomb\n\n"
            "Este programa simula a interação entre cargas elétricas segundo a Lei de Coulomb.\n"
            "Você pode adicionar, editar e visualizar as forças atuantes entre as cargas.\n\n"
            "Comandos:\n"
            "Pressione 'A' para adicionar uma carga\n"
            "Pressione 'C' para editar uma carga\n"
            "Pressione 'D' para deletar uma carga.\n"
            "Clique em uma carga para ver as forças\n"
            "Pressione 'R' para reiniciar a simulação.\n"
            "Pressione 'U' para aumentar o tamanho da régua em uma unidade.\n"
            "Pressione 'E' para diminuir o tamanho da régua em uma unidade.\n"
        )
        
        label = tk.Label(root, text=message, padx=10, pady=10)
        label.pack()

        # Botão para importar cargas
        import_button = tk.Button(root, text="Importar Cargas", command=lambda: importar_cargas('cargas.txt'))
        import_button.pack(pady=10)  # Adiciona o botão com espaçamento vertical

        def visualizar_arquivo():
            try:
                with open('cargas.txt', 'r') as file:
                    conteudo = file.read()

                # Criar nova janela para exibir o conteúdo do arquivo
                file_window = tk.Toplevel(root)
                file_window.title("Visualizar Arquivo cargas.txt")
                file_text = scrolledtext.ScrolledText(file_window, wrap=tk.WORD, width=40, height=10, padx=10, pady=10)
                file_text.insert(tk.END, conteudo)
                file_text.config(state=tk.DISABLED)
                file_text.pack()
            except FileNotFoundError:
                error_label = tk.Label(root, text="Arquivo cargas.txt não encontrado!", fg="red")
                error_label.pack()
        def visualizar_cargas():
            if not charges:
                error_label = tk.Label(root, text="Nenhuma carga presente no sistema!", fg="red")
                error_label.pack()
            else:
                charges_window = tk.Toplevel(root)
                charges_window.title("Cargas Presentes no Sistema")
                charges_text = scrolledtext.ScrolledText(charges_window, wrap=tk.WORD, width=40, height=10, padx=10, pady=10)
                
                # Montando o texto com as cargas
                for idx, charge in enumerate(charges):
                    pos = charge['pos']
                    charge_value = charge['charge']
                    charge_info = f"Carga {idx+1}: Posição = {pos}, Valor da Carga = {charge_value}\n"
                    charges_text.insert(tk.END, charge_info)

                charges_text.config(state=tk.DISABLED)
                charges_text.pack()        

        visualizar_btn = tk.Button(root, text="Visualizar cargas.txt", command=visualizar_arquivo)
        visualizar_btn.pack(pady=10)

        visualizar_cargas_btn = tk.Button(root, text="Visualizar Cargas no Sistema", command=visualizar_cargas)
        visualizar_cargas_btn.pack(pady=11)

        root.mainloop()

    # Abrir janela de Tkinter em uma nova thread
    threading.Thread(target=open_window).start()

def draw_input_fields():
    """Desenha os campos de entrada e o botão no canto superior direito."""
    for i, box in enumerate(input_boxes):
        color = DARK_GRAY if input_active[i] else LIGHT_GRAY
        pygame.draw.rect(screen, color, box, 0)  # Caixa preenchida
        pygame.draw.rect(screen, BLACK, box, 2)  # Contorno da caixa

        # Renderiza o texto digitado ou o placeholder
        if input_texts[i]:  # Se houver texto no campo
            text_surface = font.render(input_texts[i], True, BLACK)
        else:  # Campo vazio: renderiza o placeholder
            text_surface = font.render(input_labels[i], True, LIGHT_GRAY)

        # Renderiza o texto (digitado ou placeholder)
        screen.blit(text_surface, (box.x + 5, box.y + 5))

    # Botão "Adicionar"
    pygame.draw.rect(screen, BLUE, add_button)
    add_text = font.render("Adicionar", True, WHITE)
    screen.blit(add_text, (add_button.x + 10, add_button.y + 5))

# Função para adicionar uma nova carga
def add_charge():
    try:
        charge_value = float(input_texts[0])
        position = eval(input_texts[1])  # Avalia a posição como uma tupla
        if isinstance(position, tuple) and len(position) == 2:
            new_charge = {"charge": charge_value, "pos": position, "number": len(charges) + 1}
            charges.append(new_charge)
            print(f"Carga adicionada: {new_charge}")
        else:
            raise ValueError("A posição deve ser uma tupla (x, y).")
    except Exception as e:
        print(f"Erro ao adicionar carga: {e}")

# Atualizar evento principal
def handle_input_events(event):
    global input_active

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Verificar se algum campo foi clicado
        for i, box in enumerate(input_boxes):
            if box.collidepoint(event.pos):
                input_active[i] = True
            else:
                input_active[i] = False
        # Verificar clique no botão "Adicionar"
        if add_button.collidepoint(event.pos):
            add_charge()

    elif event.type == pygame.KEYDOWN:
        for i in range(len(input_boxes)):
            if input_active[i]:  # Apenas processar texto no campo ativo
                if event.key == pygame.K_RETURN:
                    input_active[i] = False  # Desativa o campo ao pressionar Enter
                elif event.key == pygame.K_BACKSPACE:
                    input_texts[i] = input_texts[i][:-1]  # Remove o último caractere
                else:
                    input_texts[i] += event.unicode  # Adiciona o caractere digitado



# Constantes
k = 8.99e9  # Constante de Coulomb
SCALE = 20  # Escala para o desenho (1 unidade no plano = SCALE pixels)
VECTOR_LENGTH = 50  # Comprimento máximo dos vetores em pixels

# Lista para armazenar as cargas
charges = []
simulation_running = False

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
    if q1['charge'] * q2['charge'] > 0:
        return [-force_x, -force_y]  # Repulsão
    else:
        return [force_x, force_y]  # Atração


# Definições da régua
class Ruler:
    def __init__(self, length=200, scale=SCALE):
        self.length = length            # Comprimento da régua em pixels
        self.scale = scale              # Escala em pixels por unidade
        self.angle = 0                  # Ângulo inicial da régua em graus
        self.position = (400, 300)      # Posição inicial (centro da régua)
        self.is_dragging = False        # Estado de arraste da régua

    def draw(self, screen):
        # Calcula os pontos de extremidade da régua com base no ângulo
        x1 = self.position[0] + (self.length / 2) * math.cos(math.radians(self.angle))
        y1 = self.position[1] + (self.length / 2) * math.sin(math.radians(self.angle))
        x2 = self.position[0] - (self.length / 2) * math.cos(math.radians(self.angle))
        y2 = self.position[1] - (self.length / 2) * math.sin(math.radians(self.angle))

        # Desenha a linha principal da régua
        pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 3)

        # Definir o número de marcas e o intervalo em unidades de Coulomb
        num_ticks = 10  # Número de marcas
        tick_distance = self.length / num_ticks
        unit_distance = tick_distance / self.scale  # Distância em unidades de Coulomb

        # Desenha as marcas de escala e os rótulos
        for i in range(num_ticks + 1):
            # Calcula a posição da marca
            tick_ratio = i / num_ticks
            tick_x = x2 + tick_ratio * (x1 - x2)
            tick_y = y2 + tick_ratio * (y1 - y2)
            tick_length = 12 if i % 2 == 0 else 6  # Marcas maiores a cada 20 pixels

            # Calcula a orientação da marca com base no ângulo da régua
            offset_x = tick_length * math.sin(math.radians(self.angle))
            offset_y = -tick_length * math.cos(math.radians(self.angle))

            # Desenha a marca
            pygame.draw.line(screen, (0, 0, 0), 
                             (tick_x - offset_x, tick_y - offset_y), 
                             (tick_x + offset_x, tick_y + offset_y), 2)

            # Adiciona os rótulos nas marcas principais
            if i % 2 == 0:
                font = pygame.font.SysFont("Times New Roman", 13)  
                label_text = f"{i * unit_distance:.1f} m"  # Valor em unidades de Coulomb
                label_surface = font.render(label_text, True, (0, 0, 0))
                label_x = tick_x + offset_x * 1.5
                label_y = tick_y + offset_y * 1.5
                screen.blit(label_surface, (label_x, label_y))

    def rotate(self, angle_change):
        # Atualiza o ângulo da régua
        self.angle = (self.angle + angle_change) % 360

    def set_position(self, position):
        # Atualiza a posição da régua
        self.position = position

    def start_drag(self):
        self.is_dragging = True

    def stop_drag(self):
        self.is_dragging = False

    def update_drag(self, mouse_position):
        if self.is_dragging:
            self.set_position(mouse_position)

    def increase_scale(self):
        self.length += 20
    
    def decrease_scale(self):
        self.length -= 20


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
    forces.append(f"Carga {q['number']} com valor de {q['charge']} C.")
    
    for other_charge in charges:
        if other_charge != q:
            force = calculate_force(q, other_charge)
            
            # Verificar se as cargas têm a mesma posição no eixo X ou Y
            if q['pos'][0] == other_charge['pos'][0]:  # Mesma posição no eixo X
                force[0] = 0  # Força em X será zero
            if q['pos'][1] == other_charge['pos'][1]:  # Mesma posição no eixo Y
                force[1] = 0  # Força em Y será zero

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

    messagebox.showinfo("Forças Atuantes", "\n".join(forces))
    root.destroy()


def importar_cargas(arquivo):
    global charges
    try:
        with open(arquivo, 'r') as file:
            charges.clear()  # Limpa as cargas atuais
            for idx, line in enumerate(file):
                parts = line.split()  # Divide a linha em partes
                pos_part = parts[1].split(',')
                pos_x, pos_y = int(pos_part[0]), int(pos_part[1])
                
                charge_value = float(parts[3])
                
                charge = {
                    'pos': (pos_x, pos_y),
                    'charge': charge_value,
                    'number': idx + 1  # Adiciona um número sequencial à carga
                }
                charges.append(charge)
        print("Cargas importadas com sucesso!")
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")


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
show_intro = True

def draw_intro():
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))
    title_text = underline_font.render("Simulador da Lei de Coulomb", True, BLACK)
    instructions_text = bold_font.render("Pressione 'Enter' para Iniciar", True, BLACK)
    commands_text = bold_font.render("Comandos:", True, BLACK)
    command1_text = font.render("Pressione 'A' para adicionar uma carga", True, BLACK)
    command2_text = font.render("Pressione 'C' para editar uma carga", True, BLACK)
    command3_text = font.render("Pressione 'D' para deletar uma carga", True, BLACK)
    command4_text = font.render("Pressione 'R' para reiniciar a simulação", True, BLACK)
    command5_text = font.render("Pressione 'Q' para reiniciar o programa", True, BLACK)
    command6_text = font.render("Clique em uma carga para ver as forças", True, BLACK)

    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 4))
    screen.blit(instructions_text, (width // 2 - instructions_text.get_width() // 2, height // 2))
    screen.blit(commands_text, (width // 2 - commands_text.get_width() // 2, height // 2 + 30))
    screen.blit(command1_text, (width // 2 - command1_text.get_width() // 2, height // 2 + 60))
    screen.blit(command2_text, (width // 2 - command2_text.get_width() // 2, height // 2 + 90))
    screen.blit(command3_text, (width // 2 - command3_text.get_width() // 2, height // 2 + 120))
    screen.blit(command4_text, (width // 2 - command4_text.get_width() // 2, height // 2 + 150))
    screen.blit(command5_text, (width // 2 - command5_text.get_width() // 2, height // 2 + 180))
    screen.blit(command6_text, (width // 2 - command6_text.get_width() // 2, height // 2 + 210))

def delete_charge():
    charge_number = simpledialog.askinteger("Deletar Carga", "Insira o número da carga:")
    if charge_number is not None:
        if 1 <= charge_number <= len(charges):
            charge = charges[charge_number - 1]
            charges.remove(charge)  # Remove da lista
            messagebox.showinfo("Sucesso", f"Carga {charge_number} deletada com sucesso.")
        else:
            messagebox.showerror("Erro", "Número da carga inválido.")

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
                                return  

                    charge['pos'] = [x, y]  # Atualiza a posição
                except ValueError:
                    messagebox.showerror("Erro", "Posição inválida. Use o formato x,y.")
        else:
            messagebox.showerror("Erro", "Número da carga inválido.")

def reset_simulation():
    global show_intro, simulation_running, charges
    show_intro = True
    simulation_running = False
    charges.clear()

ruler = Ruler()


while running:
    if show_intro:
        draw_intro()
    elif not simulation_running:
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))
        title_text = font.render("Lei de Coulomb", True, BLACK)
        screen.blit(law_image, image_rect.topleft)
        outline_rect = image_rect.inflate(10, 10)
        pygame.draw.rect(screen, BLACK, outline_rect, 2)
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height - 550))
        pygame.display.update()
    else:
        screen.fill(WHITE)
        ruler.draw(screen)
        draw_grid()
        draw_charges()
        draw_force_vectors()
        draw_input_fields()
        pygame.draw.rect(screen, button_color, button_rect)
        outline_rect = button_rect.inflate(5, 5)
        pygame.draw.rect(screen, BLACK, outline_rect, 2)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))  # Centraliza o texto no botão

    for event in pygame.event.get():
        handle_input_events(event)
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
            elif event.key == pygame.K_u:
                ruler.increase_scale()
            elif event.key == pygame.K_e:
                ruler.decrease_scale()
            elif event.key == pygame.K_d:
                delete_charge()
            elif event.key == pygame.K_q:
                reset_simulation()
            if event.key == pygame.K_LEFT:
                ruler.rotate(-5)  # Rotaciona a régua para a esquerda
            elif event.key == pygame.K_RIGHT:
                ruler.rotate(5)   # Rotaciona a régua para a direita
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                ruler.start_drag()
            mouse_pos = pygame.mouse.get_pos()
            if simulation_running:
                handle_click(mouse_pos)
            if button_rect.collidepoint(mouse_pos):  # Verifica se o botão de reinício foi clicado
                show_info_window()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                ruler.stop_drag()
    # Atualiza a posição de arraste
    mouse_pos = pygame.mouse.get_pos()
    ruler.update_drag(mouse_pos)
    pygame.display.update()
    clock.tick(60)

pygame.quit()

