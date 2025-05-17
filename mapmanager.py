# mapmanager.py: Gerencia o mapa, incluindo carregamento, salvamento, e manipulação de blocos
import pickle
from panda3d.core import *

class Mapmanager:
    def __init__(self):
        # Define o modelo e textura padrão para os blocos
        self.model = 'block'  # block.egg
        self.texture = 'block.png'
        
        # Lista de cores RGBA para blocos em diferentes alturas
        self.colors = [
            (0.2, 0.2, 0.35, 1),  # Azul escuro
            (0.2, 0.5, 0.2, 1),   # Verde
            (0.7, 0.2, 0.2, 1),   # Vermelho
            (0.5, 0.3, 0.0, 1)    # Marrom
        ]
        
        # Inicializa o nó principal do mapa
        self.startNew()

    def startNew(self):
        """Cria a base para um novo mapa"""
        self.land = render.attachNewNode("Land")  # Nó pai para todos os blocos

    def getColor(self, z):
        """Retorna a cor correspondente à altura z"""
        if z < len(self.colors):
            return self.colors[z]
        return self.colors[-1]  # Última cor para alturas maiores

    def addBlock(self, position):
        """Adiciona um bloco na posição especificada"""
        try:
            block = loader.loadModel(self.model)
            block.setTexture(loader.loadTexture(self.texture))
            block.setPos(position)
            block.setColor(self.getColor(int(position[2])))
            # Formata a tag como uma string simples
            tag = f"{int(position[0])},{int(position[1])},{int(position[2])}"
            block.setTag("at", tag)
            block.reparentTo(self.land)
            print(f"Bloco adicionado em {position}, tag: {tag}")
            return block
        except Exception as e:
            print(f"Erro ao adicionar bloco: {e}")
            return None

    def clear(self):
        """Remove todos os blocos e reinicia o mapa"""
        self.land.removeNode()
        self.startNew()

    def loadLand(self, filename):
        """Carrega um mapa de um arquivo de texto, retorna dimensões"""
        self.clear()
        try:
            with open(filename, 'r') as file:
                y = 0
                for line in file:
                    x = 0
                    line = line.strip().split(' ')
                    for z in line:
                        try:
                            z = int(z)
                            for z0 in range(z + 1):
                                self.addBlock((x, y, z0))
                            x += 1
                        except ValueError:
                            print(f"Erro: Valor inválido '{z}' na linha {y}")
                    y += 1
                return x, y
        except FileNotFoundError:
            print(f"Erro: Arquivo {filename} não encontrado")
            return 0, 0
        except Exception as e:
            print(f"Erro ao carregar mapa: {e}")
            return 0, 0

    def findBlocks(self, pos):
        """Encontra blocos na posição especificada"""
        tag = f"{int(pos[0])},{int(pos[1])},{int(pos[2])}"
        blocks = self.land.findAllMatches("=at=" + tag)
        print(f"Buscando blocos em {pos}, tag: {tag}, encontrados: {len(blocks)}")
        return blocks

    def isEmpty(self, pos):
        """Verifica se a posição está vazia"""
        empty = len(self.findBlocks(pos)) == 0
        print(f"Posição {pos} está {'vazia' if empty else 'ocupada'}")
        return empty

    def findHighestEmpty(self, pos):
        """Encontra a posição mais alta vazia em uma coluna"""
        x, y, z = pos
        z = 0  # Inicia do chão
        while not self.isEmpty((x, y, z)):
            z += 1
            if z > 100:  # Evita loops infinitos
                print(f"Aviso: Limite de altura atingido em {pos}")
                return (x, y, 0)
        print(f"Posição mais alta vazia em {pos}: {(x, y, z)}")
        return (x, y, z)

    def buildBlock(self, pos):
        """Adiciona um bloco no modo principal, considerando gravidade"""
        x, y, z = pos
        new = self.findHighestEmpty(pos)
        if new[2] <= z + 1:
            self.addBlock(new)

    def delBlock(self, position):
        """Remove todos os blocos na posição especificada (modo espectador)"""
        blocks = self.findBlocks(position)
        for block in blocks:
            block.removeNode()

    def delBlockFrom(self, position):
        """Remove o bloco mais alto na posição (modo principal)"""
        x, y, z = self.findHighestEmpty(position)
        pos = (x, y, z - 1)
        blocks = self.findBlocks(pos)
        for block in blocks:
            block.removeNode()

    def saveMap(self):
        """Salva o mapa em um arquivo binário com pickle"""
        try:
            blocks = self.land.getChildren()
            with open('my_map.dat', 'wb') as fout:
                pickle.dump(len(blocks), fout)
                for block in blocks:
                    x, y, z = block.getPos()
                    pos = (int(x), int(y), int(z))
                    color = block.getColor()
                    pickle.dump((pos, color), fout)
        except Exception as e:
            print(f"Erro ao salvar mapa: {e}")

    def loadMap(self):
        """Carrega o mapa de um arquivo binário"""
        try:
            self.clear()
            with open('my_map.dat', 'rb') as fin:
                length = pickle.load(fin)
                for _ in range(length):
                    pos, color = pickle.load(fin)
                    block = self.addBlock(pos)
                    if block:
                        block.setColor(color)
        except FileNotFoundError:
            print("Erro: my_map.dat não encontrado")
        except pickle.UnpicklingError:
            print("Erro: Arquivo my_map.dat corrompido")
        except Exception as e:
            print(f"Erro ao carregar mapa: {e}")