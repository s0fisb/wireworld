import pyxel
import tkinter as tk
from tkinter import filedialog
import copy 

# Estados
VAZIO = 0
FIO = 1
CABECA = 2
CAUDA = 3

cores = {
    VAZIO: 0,    # preto
    FIO: 14,      # rosa claro
    CABECA: 8,  # rosa escuro
    CAUDA: 12     # azul
}

PAUSE = 1
PLAY = 2

class WireWorld:
    def __init__(self, largura=40, altura=40, cell_size=10):
        self.width = largura
        self.height = altura
        self.cell_size = cell_size

        # matriz inicial
        self.grid = [[VAZIO for _ in range(largura)] for _ in range(altura)]
        self.grid_color = 1
        self.state_inicial = None

        self.state = 'menu'
        self.menu = Menu(self.cell_size)

        self.mode = PAUSE
        self.edit_mode = False
        
        self.speed = 11

        # contador de frames (para desacelerar a simulação)
        self.frame_count = 0

        # inicializa pyxel
        pyxel.init(largura * cell_size, altura * cell_size)
        pyxel.mouse(True)  # mostra o cursor
        pyxel.run(self.update, self.draw)

    def reset(self):
        if self.state_inicial is not None:
            self.grid = copy.deepcopy(self.state_inicial)

    def update(self):

        if self.state == "menu":
            self.menu.update()
        
            if pyxel.btnp(pyxel.KEY_RETURN):

                if self.menu.options_initial[self.menu.option] == 'NEW MAP':
                    self.state = 'level'
                    self.mode = PAUSE
                    self.edit_mode = True

                elif self.menu.options_initial[self.menu.option] == 'LOAD MAP':

                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(
                        title="Selecione o arquivo do mapa",
                        filetypes=[("WireWorld Map", "*.richsof"), ("Todos os arquivos", "*.*")]
                    )
                    if file_path:
                        with open(file_path, "r") as f:
                            lines = f.readlines()
                            for y, line in enumerate(lines):
                                for x, val in enumerate(line.strip().split()):
                                    if y < self.height and x < self.width:
                                        self.grid[y][x] = int(val)
                        self.state_inicial = copy.deepcopy(self.grid)
                        self.state = 'level'
                        self.mode = PAUSE
                        self.edit_mode = False

                    root.destroy()

                elif self.menu.options_initial[self.menu.option] == "QUIT GAME":
                    pyxel.quit()  # sai do jogo
        else:

            if pyxel.btnp(pyxel.KEY_KP_PLUS) or pyxel.btnp(pyxel.KEY_EQUALS):
                self.speed = max(1, self.speed - 1)
            
            if pyxel.btnp(pyxel.KEY_KP_MINUS) or pyxel.btnp(pyxel.KEY_MINUS):
                self.speed = min(20, self.speed + 1)


            # alternar edição/simulação
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.mode = PAUSE if self.mode == PLAY else PLAY

            # reset
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()

            if pyxel.btnp(pyxel.KEY_L):
                self.grid = [[VAZIO for _ in range(self.width)] for _ in range(self.height)]
                self.state_inicial = None
                self.state = 'level'
                self.mode = PAUSE
                self.edit_mode = True

            if pyxel.btnp(pyxel.KEY_E):
                self.edit_mode = not self.edit_mode

            # abrir o menu ao pressionar apagar
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.state = "menu"
                self.edit_mode = False
                self.mode = PAUSE

            # salvar matriz ao pressionar S
            if pyxel.btnp(pyxel.KEY_S):
                if self.state_inicial is not None:
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".richsof",
                        filetypes=[("WireWorld Map", "*.richsof"), ("Todos os arquivos", "*.*")],
                        title="Salvar mapa como"
                    )
                    if file_path:
                        with open(file_path, "w") as f:
                            for row in self.state_inicial:
                                f.write(" ".join(str(cell) for cell in row) + "\n")
                    root.destroy()

            if self.edit_mode and self.mode == PAUSE:
                # MODO EDIÇÃO
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    x = pyxel.mouse_x // self.cell_size
                    y = pyxel.mouse_y // self.cell_size
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # alterna entre os 4 estados
                        self.painting = (self.grid[y][x] + 1) % 4
                        self.grid[y][x] = self.painting
                        self.state_inicial = copy.deepcopy(self.grid)

                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    x = pyxel.mouse_x // self.cell_size
                    y = pyxel.mouse_y // self.cell_size
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # alterna entre os 4 estados
                        self.grid[y][x] = (self.painting)
                        self.state_inicial = copy.deepcopy(self.grid)

            if self.mode == PLAY or self.mode == PAUSE and pyxel.btnp(pyxel.KEY_RIGHT):
                # MODO SIMULAÇÃO
                self.frame_count += 1
                if self.frame_count % self.speed == 0 or pyxel.btnp(pyxel.KEY_RIGHT):  # só atualiza a cada 10 frames
                    novo_mundo = [[VAZIO for _ in range(self.width)] for _ in range(self.height)]
                    for y in range(self.height):
                        for x in range(self.width):
                            cel = self.grid[y][x]
                            if cel == VAZIO:
                                novo_mundo[y][x] = VAZIO
                            elif cel == FIO:
                                vizinhos = 0
                                for dy in (-1, 0, 1):
                                    for dx in (-1, 0, 1):
                                        if dx == 0 and dy == 0:
                                            continue
                                        nx, ny = x + dx, y + dy
                                        if 0 <= nx < self.width and 0 <= ny < self.height:
                                            if self.grid[ny][nx] == CABECA:
                                                vizinhos += 1
                                novo_mundo[y][x] = CABECA if vizinhos in (1, 2) else FIO
                            elif cel == CABECA:
                                novo_mundo[y][x] = CAUDA
                            elif cel == CAUDA:
                                novo_mundo[y][x] = FIO
                    self.grid = novo_mundo


    def draw(self):

        if self.state == "menu":
            self.menu.draw()
        else:
            pyxel.cls(0)

            # desenha células
            for y in range(self.height):
                for x in range(self.width):
                    cor = cores[self.grid[y][x]]
                    pyxel.rect(x * self.cell_size, y * self.cell_size,
                            self.cell_size, self.cell_size, cor)

            # desenha grade
            for x in range(0, self.width * self.cell_size, self.cell_size):
                pyxel.line(x, 0, x, self.height * self.cell_size, self.grid_color)
            for y in range(0, self.height * self.cell_size, self.cell_size):
                pyxel.line(0, y, self.width * self.cell_size, y, self.grid_color)

            # destaca célula sob o mouse
            if self.edit_mode:
                cx = pyxel.mouse_x // self.cell_size
                cy = pyxel.mouse_y // self.cell_size
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    pyxel.rectb(cx * self.cell_size, cy * self.cell_size,
                                self.cell_size, self.cell_size, 7)

            # instruções
            status = "PLAY" if self.mode == PLAY else "PAUSE"
            edit = "EDICAO ATIVADA" if self.edit_mode else "EDIÇAO DESATIVADA"
            pyxel.text(5, 5, f"Modo: {edit} | Estado: {status} | Speed: {21-self.speed}", 7)

            if self.mode==PAUSE:
                pyxel.text(5, 15, "\nESPACO: PAUSAR/PLAY | R: RESETAR | S: SALVAR \n\n" "E: ATIVAR/DESATIVAR EDICAO | BACKSPACE: MENU | L: LIMPAR MAPA", 7)

class Menu:
    def __init__(self, cell_size):
        self.options_initial = ['NEW MAP', 'LOAD MAP', 'QUIT GAME']
        self.option = 0
        self.cell_size = cell_size

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.option = (self.option - 1) % len(self.options_initial)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.option = (self.option + 1) % len(self.options_initial)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(150,110,'WIREWORLD BY RICH AND SOFS', 7)
        for i, option in enumerate(self.options_initial):
            if i == self.option:     
                color= 7
            else: 
                color= 8
            pyxel.text(180, 150 + i * 10, option, color)

WireWorld()
