# hero.py: Controla o jogador, incluindo movimentação, câmera, e interação com o mapa
from panda3d.core import *

# Definição das teclas para controle
key_switch_camera = 'c'  # Alterna visão da câmera
key_switch_mode = 'z'    # Alterna modo espectador/principal
key_forward = 'w'        # Movimento para frente
key_back = 's'           # Movimento para trás
key_left = 'a'           # Movimento para esquerda
key_right = 'd'          # Movimento para direita
key_up = 'e'             # Movimento para cima
key_down = 'q'           # Movimento para baixo
key_turn_left = 'n'      # Rotação para esquerda
key_turn_right = 'm'     # Rotação para direita
key_build = 'b'          # Construir bloco
key_destroy = 'v'        # Destruir bloco
key_savemap = 'k'        # Salvar mapa
key_loadmap = 'l'        # Carregar mapa

class Hero:
    def __init__(self, pos, land):
        """Inicializa o jogador"""
        self.land = land
        self.mode = True  # Inicia no modo espectador
        self.hero = loader.loadModel('smiley')
        self.hero.setColor(1, 0.5, 0)  # Cor laranja
        self.hero.setScale(0.3)
        self.hero.setH(180)  # Orienta o jogador
        self.hero.setPos(pos)
        self.hero.reparentTo(render)
        self.cameraBind()
        self.accept_events()

    def cameraBind(self):
        """Vincula a câmera ao jogador"""
        base.disableMouse()
        base.camera.setH(180)
        base.camera.reparentTo(self.hero)
        base.camera.setPos(0, 0, 1.5)
        self.cameraOn = True

    def cameraUp(self):
        """Desvincula a câmera para modo espectador"""
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)
        base.enableMouse()
        self.cameraOn = False

    def changeView(self):
        """Alterna entre visão vinculada e desvinculada"""
        if self.cameraOn:
            self.cameraUp()
        else:
            self.cameraBind()

    def turn_left(self):
        """Rotaciona o jogador para a esquerda"""
        self.hero.setH((self.hero.getH() + 5) % 360)

    def turn_right(self):
        """Rotaciona o jogador para a direita"""
        self.hero.setH((self.hero.getH() - 5) % 360)

    def look_at(self, angle):
        """Calcula as coordenadas para onde o jogador se moverá"""
        x_from = round(self.hero.getX())
        y_from = round(self.hero.getY())
        z_from = round(self.hero.getZ())
        dx, dy = self.check_dir(angle)
        return (x_from + dx, y_from + dy, z_from)

    def just_move(self, angle):
        """Move o jogador no modo espectador"""
        pos = self.look_at(angle)
        self.hero.setPos(pos)
        print(f"Movido (espectador) para {pos}")

    def move_to(self, angle):
        """Decide o tipo de movimento com base no modo"""
        print(f"move_to chamado com ângulo {angle}, modo: {'Espectador' if self.mode else 'Principal'}")
        if self.mode:
            self.just_move(angle)
        else:
            self.try_move(angle)

    def check_dir(self, angle):
        """Calcula a direção de movimento com base no ângulo"""
        if angle >= 0 and angle <= 20:
            return (0, -1)
        elif angle <= 65:
            return (1, -1)
        elif angle <= 110:
            return (1, 0)
        elif angle <= 155:
            return (1, 1)
        elif angle <= 200:
            return (0, 1)
        elif angle <= 245:
            return (-1, 1)
        elif angle <= 290:
            return (-1, 0)
        elif angle <= 335:
            return (-1, -1)
        else:
            return (0, -1)

    def forward(self):
        """Move para frente"""
        angle = (self.hero.getH()) % 360
        print(f"forward chamado, ângulo: {angle}")
        self.move_to(angle)

    def back(self):
        """Move para trás"""
        angle = (self.hero.getH() + 180) % 360
        print(f"back chamado, ângulo: {angle}")
        self.move_to(angle)

    def left(self):
        """Move para esquerda"""
        angle = (self.hero.getH() + 90) % 360
        print(f"left chamado, ângulo: {angle}")
        self.move_to(angle)

    def right(self):
        """Move para direita"""
        angle = (self.hero.getH() + 270) % 360
        print(f"right chamado, ângulo: {angle}")
        self.move_to(angle)

    def changeMode(self):
        """Alterna entre modo espectador e principal"""
        self.mode = not self.mode
        print(f"Modo: {'Espectador' if self.mode else 'Principal'}")

    def try_move(self, angle):
        """Move no modo principal, considerando colisões"""
        pos = self.look_at(angle)
        print(f"Tentando mover para {pos}, vazio: {self.land.isEmpty(pos)}")
        if self.land.isEmpty(pos):
            # Move para a posição mais alta vazia (gravidade)
            new_pos = self.land.findHighestEmpty(pos)
            print(f"Nova posição: {new_pos}, vazio: {self.land.isEmpty(new_pos)}")
            if self.land.isEmpty(new_pos):
                self.hero.setPos(new_pos)
            else:
                print(f"Erro: Nova posição {new_pos} não é vazia, não movendo")
        else:
            # Tenta escalar um bloco acima
            climb_pos = (pos[0], pos[1], pos[2] + 1)
            print(f"Tentando escalar para {climb_pos}, vazio: {self.land.isEmpty(climb_pos)}")
            if self.land.isEmpty(climb_pos):
                # Verifica se a posição atual permite escalada
                current_pos = (round(self.hero.getX()), round(self.hero.getY()), round(self.hero.getZ()))
                if self.land.isEmpty((current_pos[0], current_pos[1], current_pos[2] + 1)):
                    self.hero.setPos(climb_pos)
                else:
                    print(f"Posição atual {current_pos} não permite escalada, não movendo")
            else:
                print(f"Posição {climb_pos} ocupada, não movendo")

    def up(self):
        """Move para cima no modo espectador"""
        if self.mode:
            self.hero.setZ(self.hero.getZ() + 1)
            print(f"Movido para cima, nova Z: {self.hero.getZ()}")

    def down(self):
        """Move para baixo no modo espectador"""
        if self.mode:
            self.hero.setZ(self.hero.getZ() - 1)
            print(f"Movido para baixo, nova Z: {self.hero.getZ()}")

    def build(self):
        """Constrói um bloco à frente do jogador"""
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        print(f"Construindo bloco em {pos}")
        if self.mode:
            self.land.addBlock(pos)
        else:
            self.land.buildBlock(pos)

    def destroy(self):
        """Destrói um bloco à frente do jogador"""
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        print(f"Destruindo bloco em {pos}")
        if self.mode:
            self.land.delBlock(pos)
        else:
            self.land.delBlockFrom(pos)

    def accept_events(self):
        """Registra os eventos de teclado"""
        print("Registrando eventos de teclado. Certifique-se de que o teclado está em inglês.")
        base.accept(key_turn_left, self.turn_left)
        base.accept(key_turn_left + '-repeat', self.turn_left)
        base.accept(key_turn_right, self.turn_right)
        base.accept(key_turn_right + '-repeat', self.turn_right)
        base.accept(key_forward, self.forward)
        base.accept(key_forward + '-repeat', self.forward)
        base.accept(key_back, self.back)
        base.accept(key_back + '-repeat', self.back)
        base.accept(key_left, self.left)
        base.accept(key_left + '-repeat', self.left)
        base.accept(key_right, self.right)
        base.accept(key_right + '-repeat', self.right)
        base.accept(key_switch_camera, self.changeView)
        base.accept(key_switch_mode, self.changeMode)
        base.accept(key_up, self.up)
        base.accept(key_up + '-repeat', self.up)
        base.accept(key_down, self.down)
        base.accept(key_down + '-repeat', self.down)
        base.accept(key_build, self.build)
        base.accept(key_destroy, self.destroy)
        base.accept(key_savemap, self.land.saveMap)
        base.accept(key_loadmap, self.land.loadMap)