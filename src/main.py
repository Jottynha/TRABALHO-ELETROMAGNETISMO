import sys
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont, QFontDatabase
import math
import campo_eletrico
import json

name_arquivo = "cargas.txt"


class PygameWidget(QWidget):
    def visualizar_campo_eletrico(self):
        """
        Salva as cargas atuais no arquivo JSON e plota o campo elétrico.
        """
        try:
            self.salvar_campo()
            charges = campo_eletrico.load_charges()
            X, Y, Ex, Ey = campo_eletrico.calculate_field(charges, x_range=(-20, 20), y_range=(-20, 20), resolution=50)
            campo_eletrico.plot_field(charges, X, Y, Ex, Ey)

        except Exception as e:
            print(f"Erro ao visualizar o campo elétrico: {e}")
    def visualizar_dados_cargas(self):
        """
        Exibe os dados de todas as cargas enquanto houverem cargas disponíveis.
        """
        try:
            charge_number = 1  # Começa com o número da primeira carga
            while True:
                charge = self.buscarCharge(charge_number)
                if charge is not None:
                    Interface.display_charge_data(charge_number)
                    charge_number += 1  # Incrementa o número da carga para buscar a próxima
                else:
                    # Se a carga não for encontrada, sai do loop
                    break
                    
        except Exception as e:
            print(f"Erro ao visualizar os dados das cargas: {e}")

            
    def __init__(self, largura_janela, altura_janela, parent=None):
        super().__init__(parent)
        self.width = largura_janela
        self.height = altura_janela

        # Inicializa Pygame
        pygame.init()
        self.screen = None  # Será configurado dinamicamente
        self.charges = []  # Lista para armazenar as cargas
        self.show_resultant_force = False   # Mostrar a força resultante ou as forças separadas

        # Coordenadas de interação
        self.list_reta = []

        # Timer para atualizar o Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(20)  

        # Label para exibir o conteúdo do Pygame
        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def resizeEvent(self, event):
        """Redimensiona a superfície Pygame ao redimensionar o widget."""
        self.screen = pygame.Surface((self.width*0.55, self.height*0.7))
        super().resizeEvent(event)

    def update_pygame(self):
        if not self.screen:
            return
        
        # Desenha o plano cartesiano
        self.screen.fill((255, 255, 255))  # Fundo branco
        width, height = self.screen.get_size()

        mid_x, mid_y = width // 2, height // 2

        spacing = 20

        # Desenha a grade alinhada
        for x in range(mid_x % spacing, width, spacing):  # Linhas verticais
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, height))
        for y in range(mid_y % spacing, height, spacing):  # Linhas horizontais
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (width, y))

        pygame.draw.line(self.screen, (0, 0, 0), (0, mid_y), (width, mid_y), 2)  # Eixo X
        pygame.draw.line(self.screen, (0, 0, 0), (mid_x, 0), (mid_x, height), 2)  # Eixo Y

        # Desenha as linhas de interação  ->> medir a distancia entre as cargas
        if self.list_reta:
            for i in self.list_reta:
                pygame.draw.line(self.screen,  (0,0,255), i["q1"], i["q2"], 3)
                font = pygame.font.SysFont(None, 24)
                charge_number_text = font.render(f"{i['distancia']:.2f}", True, (0,0,255))
                pos_x = (i["q1"][0] + i["q2"][0]-45) // 2
                pos_y = (i["q1"][1] + i["q2"][1]-45) // 2
                self.screen.blit(charge_number_text, (pos_x - charge_number_text.get_width() // 2, pos_y - charge_number_text.get_height() // 2))
                
        else:
            self.draw_force_vectors() # Desenha os vetores de força

        # Desenha as cargas
        for charge in self.charges:
            x, y = charge["pos"]
            x *=20
            y *=20
            charge_x = mid_x + x
            charge_y = mid_y - y  # Inverter Y para coordenadas cartesianas

            if float(charge["charge"]) > 0.0 or float(charge["charge"]) == 0.0:
                pygame.draw.circle(self.screen, (255, 0, 0), (charge_x, charge_y), 12)
            else:
                pygame.draw.circle(self.screen, (0,255,0), (charge_x, charge_y), 12)

            font = pygame.font.SysFont(None, 24)
            charge_number_text = font.render(charge['name'], True, (0, 0, 0))

            pos_x = charge_x
            pos_y = charge_y
            self.screen.blit(charge_number_text, (pos_x - charge_number_text.get_width() // 2, pos_y - charge_number_text.get_height() // 2))
      

        # Converte a tela do Pygame para QPixmap e exibe no QLabel
        image_data = pygame.image.tostring(self.screen, "RGB")
        qimage = QImage(image_data, width, height, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimage))

    def atualizarName(self):
        for i in range(len(self.charges)):
            self.charges[i]['name'] = f"q{i + 1}"

    def addCharge(self, charge_value, position):
        """Adiciona uma nova carga ao sistema."""
        try:
            self.list_reta = []

            charge_value = float(charge_value)
            position = tuple(map(float, position.strip("()").split(",")))  # Parsing seguro para posição
            if len(position) == 2:
                new_charge = {"charge": charge_value, "pos": position, "name":f"q{len(self.charges) + 1}"}
                self.charges.append(new_charge)
                print(f"Carga adicionada: {new_charge}")
            else:
                raise ValueError("A posição deve ser uma tupla (x, y).")
        except Exception as e:
            print(f"Erro ao adicionar carga: {e}")

    def removeCharge(self, charge_number):
        print(f'Removendo {charge_number}')
        try:
            self.list_reta = []

            for charge in self.charges:
                if charge["name"] == charge_number:
                    self.charges.remove(charge)
                    print(f"Carga removida: {charge}")

                    break
            else:
                print(f"Carga não encontrada: Q{charge_number}")
        except Exception as e:
            print(f"Erro ao remover carga: {e}")

    def alterarCharge(self, charge_data):
        #print(f'Alterando {charge_data}')
        try:
            self.list_reta = []

            for charge in self.charges:
                if charge["name"] == charge_data["name"]:
                    charge["charge"] = float(charge_data["charge"])
                    charge["pos"] = tuple(map(float, charge_data['pos'].strip("()").split(",")))
                    break
            else:
                print(f"Carga não encontrada: {charge_data['name']}")
        except Exception as e:
            print(f"Erro ao alterar carga: {e}")

    def buscarCharge(self, charge_number):
        print(f'Buscando {charge_number}')
        try:
            self.list_reta = []

            for charge in self.charges:
                if charge["name"] == charge_number:
                    print(f"Carga encontrada: {charge}")
                    return charge
            else:
                print(f"Carga não encontrada: Q{charge_number}")
                return None
        except Exception as e:
            print(f"Erro ao buscar carga: {e}")               
            return None
  
    def calcularDistancia(self, charge_number1, charge_number2):
        charge1 = self.buscarCharge(charge_number1)
        charge2 = self.buscarCharge(charge_number2)
        if charge1 is not None and charge2 is not None:
            x1, y1 = charge1["pos"]
            x2, y2 = charge2["pos"]

            # Ajusta as coordenadas para o sistema da tela
            mid_x, mid_y = self.screen.get_size()[0] // 2, self.screen.get_size()[1] // 2
            self.list_reta.append({
                "q1": (mid_x + x1 * 20, mid_y - y1 * 20),
                "q2": (mid_x + x2 * 20, mid_y - y2 * 20),
                "distancia":((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            })

            # Marca que as retas precisam ser desenhadas
            self.list_check = True

            # Calcula a distância euclidiana
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return None
    

    def importar(self):
        try:
            with open(name_arquivo, 'r') as file:
                self.charges.clear()  # Limpa as cargas atuais
                for idx, line in enumerate(file):
                    parts = line.split()  # Divide a linha em partes

                    charge = {
                        'pos': tuple(map(float, parts[1].strip("()").split(","))),
                        'charge': float(parts[3]),
                        'name': f"q{idx + 1}"  # Adiciona um número sequencial à carga
                    }

                    self.charges.append(charge)

            print("Cargas importadas com sucesso!")
        except FileNotFoundError:
            print(f"Arquivo {name_arquivo} não encontrado.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")

                        

    def salvar_campo(self, name_arquivo="cargas.txt"):
        try:
            # Converter as cargas para o formato correto
            charges_to_save = [
                {
                    "charge": charge["charge"],
                    "pos": charge["pos"],
                    "number": index + 1  # Adiciona o número com base no índice
                }
                for index, charge in enumerate(self.charges)
            ]
            
            # Salvar no arquivo JSON
            with open(name_arquivo, "w") as file:
                json.dump(charges_to_save, file, indent=4)
            
            print("Cargas salvas com sucesso no arquivo JSON!")
        except Exception as e:
            print(f"Erro ao salvar o arquivo JSON: {e}")
    def salvar(self):
        try:
            with open(name_arquivo, 'w') as file:
                for charge in self.charges:
                    file.write(f"pos: {charge['pos'][0]},{charge['pos'][1]} charge: {charge['charge']}\n")
            print("Cargas salvas com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def calculate_force(self,q1, q2):
        k = 8.99e9  # Constante eletrostática
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

    def draw_force_vectors(self):
        charges = self.charges
        SCALE = 20
        VECTOR_LENGTH = 50
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        width, height = self.screen.get_size()

        def draw_arrow(start_x, start_y, end_x, end_y, color):
            pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 3)
            angle = math.atan2(end_y - start_y, end_x - start_x)
            arrow_length = 10
            arrow_angle = math.pi / 6
            pygame.draw.line(self.screen, color, (end_x, end_y), (end_x - arrow_length * math.cos(angle - arrow_angle), end_y - arrow_length * math.sin(angle - arrow_angle)), 3)
            pygame.draw.line(self.screen, color, (end_x, end_y), (end_x - arrow_length * math.cos(angle + arrow_angle), end_y - arrow_length * math.sin(angle + arrow_angle)), 3)

        for i in range(len(charges)):
            total_force_x = 0
            total_force_y = 0

            for j in range(len(charges)):
                if i != j:
                    force = self.calculate_force(charges[i], charges[j])

                    if not self.show_resultant_force:
                        pos_x1 = int(charges[i]['pos'][0] * SCALE + width // 2)
                        pos_y1 = int(height // 2 - charges[i]['pos'][1] * SCALE)

                        magnitude = math.sqrt(force[0]**2 + force[1]**2)
                        if magnitude > 0:
                            unit_fx = force[0] / magnitude
                            unit_fy = force[1] / magnitude
                            scaled_length = min(magnitude * 0.0001, VECTOR_LENGTH)

                            end_x = pos_x1 + unit_fx * scaled_length
                            end_y = pos_y1 - unit_fy * scaled_length

                            draw_arrow(pos_x1, pos_y1, end_x, end_y, RED)

                    total_force_x += force[0]
                    total_force_y += force[1]

            if self.show_resultant_force:
                total_force_magnitude = math.sqrt(total_force_x**2 + total_force_y**2)
                pos_x1 = int(charges[i]['pos'][0] * SCALE + width // 2)
                pos_y1 = int(height // 2 - charges[i]['pos'][1] * SCALE)

                if total_force_magnitude > 0:
                    unit_fx = total_force_x / total_force_magnitude
                    unit_fy = total_force_y / total_force_magnitude
                    scaled_length = min(total_force_magnitude * 0.0001, VECTOR_LENGTH)

                    end_x = pos_x1 + unit_fx * scaled_length
                    end_y = pos_y1 - unit_fy * scaled_length
                    draw_arrow(pos_x1, pos_y1, end_x, end_y, GREEN)


    def toggle_force_mode(self):
        self.show_resultant_force = not self.show_resultant_force


    def show_forces(self, q):

        total_force_x = 0
        total_force_y = 0

        for other_charge in self.charges:
            if other_charge != q:
                force = self.calculate_force(q, other_charge)
                
                # Verificar se as cargas têm a mesma posição no eixo X ou Y
                if q['pos'][0] == other_charge['pos'][0]:  # Mesma posição no eixo X
                    force[0] = 0  # Força em X será zero
                if q['pos'][1] == other_charge['pos'][1]:  # Mesma posição no eixo Y
                    force[1] = 0  # Força em Y será zero

                total_force_x += force[0]
                total_force_y += force[1]

        # Calcular a magnitude total da força uma vez
        total_force_magnitude = math.sqrt(total_force_x**2 + total_force_y**2)

        # Adiciona a força total na lista de forças
        return {"total_force": (total_force_x, total_force_y), "magnitude_total":total_force_magnitude}




class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pagina_inicial = True
        self.layout_app()

        self.interface_intro()
        QTimer.singleShot(1000, self.atualizar_interface)  # 1000 milissegundos = 1 segundos

    def layout_app(self):
        self.setWindowTitle("Simulador de Lei de Coulomb.")
        screen = QApplication.primaryScreen()
        screen_geometry =screen.availableGeometry()  

        self.width = int(screen_geometry.width())
        self.height = int(screen_geometry.height())
        self.resize(self.width, self.height)

        available_fonts = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(""))
        if "Roboto" in available_fonts:
            self.font = QFont("Roboto")
        elif "Liberation Sans" in available_fonts:
            self.fonte = QFont("Liberation Sans")
        else:
            self.fonte = QFont("Arial") 

    def interface_intro(self):

        layout_principal = QVBoxLayout()

        # Texto do título
        title_open = QLabel("Simulador da Lei de Coulomb")
        title_open.setAlignment(Qt.AlignCenter)  # Centraliza o texto
        title_open.setStyleSheet("font-family: fonte; font-size: 55px; font-weight: bold;")

        layout_principal.addWidget(title_open)  # Adiciona ao layout principal

        # Define o layout na janela principal
        container_open = QWidget()
        container_open.setLayout(layout_principal)
        #container_open.setStyleSheet("background-color: #f0f0f0;")

        self.setCentralWidget(container_open)


    def atualizar_interface(self):
        if self.pagina_inicial:
            self.pagina_inicial = False
            self.interface_introduction()
        else:
            self.interface_play()


    def interface_introduction(self):
        self.setCentralWidget(None)  # Remove o layout atual

        layout_principal = QVBoxLayout()

        # Widgets principais
        # Widgets principais
        widget_superior = QWidget()
        widget_inferior = QWidget()

        # Widgets para divisão inferior
        widget_inferior_esquerdo = QWidget()
        widget_inferior_direito = QWidget()
        #texto_introduction = QLabel("A Lei de Coulomb é uma lei da física que descreve a interação eletrostática")
        # Texto de introdução
        #texto_introducao = QLabel("A Lei de Coulomb é uma lei da física que descreve a interação eletrost")
        title_open = QLabel("Lei de Coulomb")
        #title_open.setAlignment(Qt.AlignCenter)  # Centraliza o texto
        title_open.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold;")
        layout_principal.addWidget(title_open, alignment=Qt.AlignLeft)


        # Botão "Pular"
        button_pular = QPushButton("Pular")
        button_pular.clicked.connect(self.interface_play)  
        button_pular.setFixedSize(100, 50)
        button_pular.setStyleSheet("font-family: fonte; font-size: 25px; color: black; border: none;")
        layout_principal.addWidget(button_pular, alignment=Qt.AlignRight)

        container_open = QWidget()
        container_open.setLayout(layout_principal)
        self.setCentralWidget(container_open)
        

    def interface_play(self):
        self.setCentralWidget(None)  

        layout_principal = QVBoxLayout()

        self.largura_janela = self.size().width()
        self.altura_janela = self.size().height()
        print(self.largura_janela*0.7, self.altura_janela*0.9)


        self.aviso = QLabel()
        self.aviso.setStyleSheet("font-family: fonte; font-size: 18px; color: red; border: none; margin-top: 30px")

        #####################################################################
        ######## Superior ############
        # Menu
        widget_superior = QWidget()
        widget_superior.setFixedHeight(int(self.altura_janela * 0.05))  

        widget_superior.setStyleSheet("border-bottom: 2px solid darkgray;")
        
        layout_superior = QHBoxLayout()
        layout_superior.setContentsMargins(10, 0, 10, 0)

        buttons = [
            ("ARQUIVO", self.arquivo),
            ("ADICIONAR", self.adicionar),
            ("REMOVER", self.remover),
            ("ALTERAR", self.alterar),
            ("DADOS DA CARGA", self.dadosCarga),
            ("DISTÂNCIA ENTRE CARGAS", self.distanciaEntreCargas),
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            
            button.setStyleSheet("font-family: fonte; font-size: 16px; color: black; border: none; margin-right: 50px;")
            layout_superior.addWidget(button)

        layout_superior.addStretch()
        widget_superior.setLayout(layout_superior)

        #####################################################################
        ####### Inferior #############
        widget_inferior = QWidget()
        self.layout_inferior = QHBoxLayout()
        
        # Menu inferior esquerdo
        widget_inferior_esquerdo = QWidget()
        widget_inferior_esquerdo.setMaximumWidth(int(self.largura_janela * 0.25))
        widget_inferior_esquerdo.setMinimumHeight(int(self.altura_janela * 0.9))

        widget_inferior_esquerdo.setStyleSheet(" border-right: 2px solid darkgray;")

        self.layout_menu_esquerdo = QVBoxLayout()
        self.layout_menu_esquerdo.setContentsMargins(10, 0, 10, 0)
        
        self.arquivo()

        widget_inferior_esquerdo.setLayout(self.layout_menu_esquerdo)
        self.layout_inferior.addWidget(widget_inferior_esquerdo)
        
        # Plano inferior direito
        layout_direito = QVBoxLayout()

        self.pygame_widget = PygameWidget(self.largura_janela, self.altura_janela)
        layout_direito.addWidget(self.pygame_widget)

        widget_inferior_direito = QWidget()
        widget_inferior_direito.setLayout(layout_direito)

        self.layout_inferior.addWidget(widget_inferior_direito)


        # Colocando as duas colunas no layout inferior
        widget_inferior.setLayout(self.layout_inferior)
        #####################################################################

        # Adiciona widgets principais ao layout principal
        layout_principal.addWidget(widget_superior)
        layout_principal.addWidget(widget_inferior)

        layout_principal.addStretch()

        # Container principal
        container_play = QWidget()
        container_play.setLayout(layout_principal)
        self.setCentralWidget(container_play)


    def limpar_menu_esquerdo(self):
        """Limpar os widgets do menu esquerdo e garantir que o layout seja completamente reiniciado"""
        # Remover todos os widgets do layout antigo
        for i in reversed(range(self.layout_menu_esquerdo.count())):
            widget = self.layout_menu_esquerdo.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.layout_menu_esquerdo.setAlignment(Qt.AlignTop)

    def visualizar_campo_eletrico(self):
        self.pygame_widget.visualizar_campo_eletrico()
    def visualizar_cargas(self):
        self.pygame_widget.visualizar_dados_cargas()
    def vazio(self):
       pass

    def importar_arquivo(self): 
        self.pygame_widget.importar()
    
    def salvar_arquivo(self):
        self.pygame_widget.salvar()
    def F_resultante_ou_separada(self):
        self.pygame_widget.toggle_force_mode()

    def arquivo(self):
        # Limpar o menu esquerdo
        self.limpar_menu_esquerdo()

        # Título da seção
        title_adicionar = QLabel("ARQUIVO")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")
        self.layout_menu_esquerdo.addWidget(title_adicionar)

        # Lista de botões e suas ações
        buttons = [
            ("Reiniciar", self.atualizar_interface),
            ("Importar", self.importar_arquivo),
            ("Salvar", self.salvar_arquivo),
            ("Visualizar forças separadas ou resultante", self.F_resultante_ou_separada),
            ("Visualizar cargas no sistema", self.visualizar_cargas),
            ("Visualizar campo elétrico", self.visualizar_campo_eletrico),
        ]

        # Adicionando os botões ao layout
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button.setStyleSheet("""
                font-family: fonte;
                font-size: 18px;
                color: black;
                border: none;
                margin-bottom: 10px;
                text-align: left;
                padding-left: 10px;
            """)
            self.layout_menu_esquerdo.addWidget(button)

    def adicionar(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Adicionar")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        q_adicionar = QLabel("O valor da carga:")
        q_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        q_campo_texto = QLineEdit()
        q_campo_texto.setPlaceholderText("Digite a carga")
        q_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")
        pos_adicionar = QLabel("Posição da carga:")
        pos_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
        pos_texto = QLineEdit()
        pos_texto.setPlaceholderText("x,y")
        pos_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        add_button = QPushButton("Adicionar")
        add_button.clicked.connect(lambda: self.pygame_widget.addCharge(q_campo_texto.text().strip(), pos_texto.text().strip()))
        add_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(q_adicionar)
        self.layout_menu_esquerdo.addWidget(q_campo_texto)
        self.layout_menu_esquerdo.addWidget(pos_adicionar)
        self.layout_menu_esquerdo.addWidget(pos_texto)
        self.layout_menu_esquerdo.addWidget(add_button)

    def remover(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Remover")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        r_remover = QLabel("O nome da carga:")
        r_remover.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        r_campo_texto = QLineEdit()
        r_campo_texto.setPlaceholderText("Digite o nome")
        r_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        sub_button = QPushButton("Remover")
        sub_button.clicked.connect(lambda: (self.display_remover(r_campo_texto.text().strip()), self.pygame_widget.removeCharge(r_campo_texto.text().strip())))

        sub_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(r_remover)
        self.layout_menu_esquerdo.addWidget(r_campo_texto)
        self.layout_menu_esquerdo.addWidget(sub_button) 


    def display_remover(self, charge_number):
            charge = self.pygame_widget.buscarCharge(charge_number)
            if charge is not None:
                self.remover()

                n_label = QLabel("Carga a ser removida:")
                n_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none; margin-top: 20px; margin-bottom: 8px;")
                self.layout_menu_esquerdo.addWidget(n_label)

                nome_label = QLabel()
                nome_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none;")
                nome_label.setText(f"Nome: {charge['name']}")
                self.layout_menu_esquerdo.addWidget(nome_label)

                carga_label = QLabel()
                carga_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none;")
                carga_label.setText(f"Carga: {charge['charge']}")
                self.layout_menu_esquerdo.addWidget(carga_label)

                posicao_label = QLabel()
                posicao_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none;")
                posicao_label.setText(f"Posição: {charge['pos']}")
                self.layout_menu_esquerdo.addWidget(posicao_label)

    def alterar(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Alterar")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        b_buscar = QLabel("O nome da carga:")
        b_buscar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        b_campo_texto = QLineEdit()
        b_campo_texto.setPlaceholderText("Digite o nome ")
        b_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(lambda: self.displayAlteraCharge(b_campo_texto.text().strip()))

        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(b_buscar)
        self.layout_menu_esquerdo.addWidget(b_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)
    
    def displayAlteraCharge(self, charge_number):
        charges = self.pygame_widget.buscarCharge(charge_number)
        if charges is not None:
            self.alterar()

            nome_label = QLabel()
            nome_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none; margin-top: 20px;")
            nome_label.setText(f"Nome: {charges['name']}")
            self.layout_menu_esquerdo.addWidget(nome_label)

            carga_label = QLabel()
            carga_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none;")
            carga_label.setText(f"Carga: {charges['charge']}")
            self.layout_menu_esquerdo.addWidget(carga_label)

            posicao_label = QLabel()
            posicao_label.setStyleSheet("font-family: fonte; font-size: 20px; border: none; margin-bottom: 20px;")
            posicao_label.setText(f"Posição: {charges['pos']}")
            self.layout_menu_esquerdo.addWidget(posicao_label)

            #------------------------------------------#

            q_adicionar = QLabel("O valor da carga:")
            q_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
            q = QLineEdit()
            q.setText(str(charges['charge']))
            q.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")
           
            pos_adicionar = QLabel("Posição da carga:")
            pos_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
            pos = QLineEdit()
            pos.setText(str(charges['pos'][0])+","+str(charges['pos'][1]))
            pos.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

            add_button = QPushButton("Alterar")
            add_button.clicked.connect(lambda: (self.pygame_widget.alterarCharge({'name': charge_number,'charge': q.text().strip(), 'pos': pos.text().strip()}), self.displayAlteraCharge(charge_number)))
            add_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px; color: black; margin-top: 20px;")

            self.layout_menu_esquerdo.addWidget(q_adicionar)
            self.layout_menu_esquerdo.addWidget(q)
            self.layout_menu_esquerdo.addWidget(pos_adicionar)
            self.layout_menu_esquerdo.addWidget(pos)
            self.layout_menu_esquerdo.addWidget(add_button)

           
    def dadosCarga(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Dados da Carga:")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        b_buscar = QLabel("O nome da carga")
        b_buscar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        b_campo_texto = QLineEdit()
        b_campo_texto.setPlaceholderText("Digite o nome")
        b_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(lambda: self.display_charge_data(b_campo_texto.text().strip()))
        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(b_buscar)
        self.layout_menu_esquerdo.addWidget(b_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)

    def display_charge_data(self, charge_number):
            charge = self.pygame_widget.buscarCharge(charge_number)
            if charge is not None:
                self.dadosCarga()
                nome_label = QLabel()
                nome_label.setStyleSheet("font-family: fonte; font-size: 10px; border: none; margin-top: 20px;")
                nome_label.setText(f"Nome: {charge['name']}")
                self.layout_menu_esquerdo.addWidget(nome_label)

                carga_label = QLabel()
                carga_label.setStyleSheet("font-family: fonte; font-size: 10px; border: none;")
                carga_label.setText(f"Carga: {charge['charge']} C")
                self.layout_menu_esquerdo.addWidget(carga_label)

                posicao_label = QLabel()
                posicao_label.setStyleSheet("font-family: fonte; font-size: 10px; border: none;")
                posicao_label.setText(f"Posição: {charge['pos']}")
                self.layout_menu_esquerdo.addWidget(posicao_label)

                force = self.pygame_widget.show_forces(charge)
                print(force)

                force_label = QLabel()
                force_label.setStyleSheet("font-family: fonte; font-size: 10px; border: none;")
                force_label.setText(f"Vetor de Força: ( {force['total_force'][0]:.2e}î, {force['total_force'][1]:.2e}ĵ) N")
                self.layout_menu_esquerdo.addWidget(force_label)

                force_magnitude_label = QLabel()
                force_magnitude_label.setStyleSheet("font-family: fonte; font-size: 10px; border: none;")
                force_magnitude_label.setText(f"Magnitude: {force['magnitude_total']:.2e} N")
                self.layout_menu_esquerdo.addWidget(force_magnitude_label)


    def distanciaEntreCargas(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Distância entre Cargas")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        q1_distancia = QLabel("O nome da carga 1:")
        q1_distancia .setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        q1_campo_texto = QLineEdit()
        q1_campo_texto.setPlaceholderText("Digite o nome")
        q1_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        q2_distancia = QLabel("O nome da carga 2:")
        q2_distancia.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
        q2_campo_texto = QLineEdit()
        q2_campo_texto.setPlaceholderText("Digite o nome")
        q2_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Calcular Distância")
        buscar_button.clicked.connect(lambda: self.pygame_widget.calcularDistancia(q1_campo_texto.text().strip(),q2_campo_texto.text().strip()))
        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")


        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(q1_distancia)
        self.layout_menu_esquerdo.addWidget(q1_campo_texto)
        self.layout_menu_esquerdo.addWidget(q2_distancia)
        self.layout_menu_esquerdo.addWidget(q2_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec_())