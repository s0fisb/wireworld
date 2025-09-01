import pyxel
import copy  # para copiar a matriz

# Estados
VAZIO = 0
FIO = 1
CABECA = 2
CAUDA = 3

cores = {
    VAZIO: 0,    # preto
    FIO: 9,      # azul
    CABECA: 10,  # amarelo
    CAUDA: 8     # laranja
}


class WireWorld:
    def __init__(self, largura=40, altura=40, cell_size=15):
        self.largura = largura
        self.altura = altura
        self.cell_size = cell_size

        # matriz inicial
        self.mundo = [[VAZIO for _ in range(largura)] for _ in range(altura)]
        self.estado_inicial = None
        self.modo_simulacao = False

        # contador de frames (para desacelerar a simulação)
        self.frame_count = 0

        # inicializa pyxel
        pyxel.init(largura * cell_size, altura * cell_size)
        pyxel.mouse(True)  # mostra o cursor
        pyxel.run(self.update, self.draw)

    def reset(self):
        if self.estado_inicial is not None:
            self.mundo = copy.deepcopy(self.estado_inicial)
            self.modo_simulacao = False

    def update(self):
        # alternar edição/simulação
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.modo_simulacao = not self.modo_simulacao
            if self.modo_simulacao:
                self.estado_inicial = copy.deepcopy(self.mundo)

        # reset
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()

        if not self.modo_simulacao:
            # MODO EDIÇÃO
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                x = pyxel.mouse_x // self.cell_size
                y = pyxel.mouse_y // self.cell_size
                if 0 <= x < self.largura and 0 <= y < self.altura:
                    # alterna entre os 4 estados
                    self.mundo[y][x] = (self.mundo[y][x] + 1) % 4

        else:
            # MODO SIMULAÇÃO
            self.frame_count += 1
            if self.frame_count % 10 == 0:  # só atualiza a cada 10 frames
                novo_mundo = [[VAZIO for _ in range(self.largura)] for _ in range(self.altura)]
                for y in range(self.altura):
                    for x in range(self.largura):
                        cel = self.mundo[y][x]
                        if cel == VAZIO:
                            novo_mundo[y][x] = VAZIO
                        elif cel == FIO:
                            vizinhos = 0
                            for dy in (-1, 0, 1):
                                for dx in (-1, 0, 1):
                                    if dx == 0 and dy == 0:
                                        continue
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < self.largura and 0 <= ny < self.altura:
                                        if self.mundo[ny][nx] == CABECA:
                                            vizinhos += 1
                            novo_mundo[y][x] = CABECA if vizinhos in (1, 2) else FIO
                        elif cel == CABECA:
                            novo_mundo[y][x] = CAUDA
                        elif cel == CAUDA:
                            novo_mundo[y][x] = FIO
                self.mundo = novo_mundo

    def draw(self):
        pyxel.cls(0)

        # desenha células
        for y in range(self.altura):
            for x in range(self.largura):
                cor = cores[self.mundo[y][x]]
                pyxel.rect(x * self.cell_size, y * self.cell_size,
                           self.cell_size, self.cell_size, cor)

        # desenha grade
        for x in range(0, self.largura * self.cell_size, self.cell_size):
            pyxel.line(x, 0, x, self.altura * self.cell_size, 5)
        for y in range(0, self.altura * self.cell_size, self.cell_size):
            pyxel.line(0, y, self.largura * self.cell_size, y, 5)

        # destaca célula sob o mouse
        if not self.modo_simulacao:
            cx = pyxel.mouse_x // self.cell_size
            cy = pyxel.mouse_y // self.cell_size
            if 0 <= cx < self.largura and 0 <= cy < self.altura:
                pyxel.rectb(cx * self.cell_size, cy * self.cell_size,
                            self.cell_size, self.cell_size, 7)

        # instruções
        if not self.modo_simulacao:
            pyxel.text(5, 5, "EDICAO (clique p/ mudar estado, ESPACO play)", 7)
        else:
            pyxel.text(5, 5, "SIMULACAO (ESPAÇO pausa, R reset)", 7)


# executa o programa
WireWorld()
