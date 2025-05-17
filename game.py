# game.py: Arquivo principal que inicializa o jogo My Minecraft
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from mapmanager import Mapmanager
from hero import Hero
import os

class Game(ShowBase):
    def __init__(self):
        # Inicializa a janela de jogo
        ShowBase.__init__(self)
        
        # Configura o campo de visão da câmera
        base.camLens.setFov(90)
        
        # Inicializa o gerenciador de mapas
        self.land = Mapmanager()
        
        # Carrega o mapa inicial de land.txt
        try:
            if os.path.exists("land.txt"):
                x, y = self.land.loadLand("land.txt")
                # Posiciona o jogador em (1, 0, 2) para teste com mapa simples
                self.hero = Hero((1, 0, 2), self.land)
                print(f"Mapa carregado com dimensões: {x}x{y}")
            else:
                print("Erro: land.txt não encontrado. Criando mapa vazio.")
                self.land.startNew()
                self.hero = Hero((1, 0, 2), self.land)
        except Exception as e:
            print(f"Erro ao carregar mapa: {e}")
            self.land.startNew()
            self.hero = Hero((1, 0, 2), self.land)

if __name__ == "__main__":
    game = Game()
    game.run()