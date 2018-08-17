#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
    @author: Hiago dos Santos (hiagop22@gmail.com)

    Múdulo responsável por gerar a interface gráfica
"""

from pre_req import *        # Vai importar as classes e funções do módulo pre_req
from resolution import *     # Arquivos com as contantes que são definidas como sendo a resolução da tela
import graphviz as gv        # Responsável pela criação de Grafos
import functools             # Usado para se salvar as imagens geradas das disciplinas
from constantes import *     # Contém as contantes principais para se fazer mineração de dados 
import os                    # Possibilita acessar as imagens geradas das disciplinas
from PIL import Image as Img # Alteração do nome Image, pois estava dando conflito
from PIL import ImageTk
import sys

try:
    from tkinter import *
    from tkinter import ttk
except ImportError:
    from Tkinter import *
    from Tkinter import ttk

# Especificação do formato em que as imagens geradas dos grafos serão salvas
graph = functools.partial(gv.Graph, format='gif')
digraph = functools.partial(gv.Digraph, format='gif')

class Graph(object):
    """Classe grafo"""
    def __init__(self, type = digraph()):
        self.graph = type # Ao contrário do grafo, o dígrafo permite orientação (SETAS)
    def add_edges(self, edges):
        """Responsável por criar os caminhos recebidos"""
        for e in edges:
            if isinstance(e[0], tuple):
                self.graph.edge(*e[0], **e[1])
            else:
                self.graph.edge(*e)
    def plot(self, name_arq = 'graph'):
        """Salva o grafo no formato especificado fora para o tipo de grafo"""
        self.graph.render('img/%s' %name_arq)
    def clear(self):
        """Limpa o grafo e evita que fique adicionado vários nós (ou caminhos) sempre
           que fizer uma busca"""
        self.graph.clear()

class Buscador(object):
    """Classe responsável por gerenciar os widgets na tela de pesquisa"""
    def __init__(self, instancia):
        '''Método construtor da classe Buscador'''
        self.instancia = instancia
        self.fonte_head1 = ('Serif', 11)      # ou 'Sans Serif' 
        self.fonte_head2 = ('Sans Serif', 16) # ou 'Sans Serif' 
        self.fonte_head3 = ('Serif', 10)      # ou 'Sans Serif' 

        self.wsize_canv = int(RESOLUTION.split('x')[0])*0.53
        self.hsize_canv = int(RESOLUTION.split('x')[1])*0.7

        self.hsize_text = int(RESOLUTION.split('x')[1])*0.053
        self.wsize_text = int(RESOLUTION.split('x')[0])*0.05

        ## Configuração da parte responsável pela busca ##
        self.frame_busca = Frame(self.instancia)
        self.frame_busca.grid(row=0, column=0, pady = 2)

        self.texto_cod_disc = Label(self.frame_busca, text = 'Código da disciplina:', font = self.fonte_head1)
        self.caixa_busca = Entry(self.frame_busca, font = self.fonte_head2, width = 14)
        self.caixa_busca.focus_set()
        self.caixa_busca.bind(ENTER, self.acha_disciplina)
        self.botao_busca = Button(self.frame_busca, text='Pesquisar', font = self.fonte_head3, command = self.acha_disciplina, width = 6)
        self.botao_busca.bind(ENTER, self.acha_disciplina)
        self.sub_framebusca = Frame(self.frame_busca)

        self.var_pos_graduac = IntVar() # Variável auxiliar que alterará seu valor de acordo com o Checkbutton pos_graduac
        self.var_graduacao = IntVar()   # Variável auxiliar que alterará seu valor de acordo com o Checkbutton graduacao

        self.pos_graduac = Checkbutton(self.sub_framebusca, text = 'pós-graduação', variable = self.var_pos_graduac, command = lambda: self.valida_checkbuttons('pos'))
        self.graduacao = Checkbutton(self.sub_framebusca, text = 'graduação', variable = self.var_graduacao, command = lambda: self.valida_checkbuttons('grad'))
        self.info = Label(self.frame_busca, text = '', fg = 'red', font = self.fonte_head2) #DISCIPLINA NÂO ENCONTRADA...

        self.texto_cod_disc.grid(row = 0, column = 0)
        self.caixa_busca.grid(row = 0, column = 1, padx = 10, sticky = W)
        self.botao_busca.grid(row = 0, column = 2)
        self.sub_framebusca.grid(row = 1, column = 1, sticky = W)
        self.graduacao.pack(side = LEFT)
        self.pos_graduac.pack(side = RIGHT)
        self.info.grid(row = 2, column = 0, columnspan=3, rowspan=3, pady = 20)

        self.nivel = Nivel()

        ## Configura a parte do widget de descrição ##
        '''Não tá diminuindo o widget descrição quando muda o tamnho da tela
        '''

        # Frame que contém a área de descrição da disciplina ////, text="Descrição da disciplina"
        self.lab_frame = ttk.Frame(self.instancia)

        # Widget responsável por mostrar a descrição da disciplina ao usuário
        self.descricao = Text(self.lab_frame, height=int(self.hsize_text), width=int(self.wsize_text)) 

        # Adicionando uma barra de rolagem vertical
        scroll = Scrollbar(self.lab_frame)
        self.descricao.configure(yscrollcommand=scroll.set, borderwidth=0, bg='white')

        scroll.config(command=self.descricao.yview)
        self.lab_frame.grid(row = 1, column = 0, pady = 5, sticky = W)
        scroll.pack(side=RIGHT, fill=Y)
        self.descricao.pack(side=LEFT, expand=YES, fill=BOTH)

        self.descricao['state'] = DISABLED

    def valida_checkbuttons(self, event = ''):
        ''' Impede que haja dois checkbuttons selecionados ao mesmo tempo e caso não haja nenhum selecionado, retorna False'''
        if event == 'grad':
            if self.var_graduacao.get() == ATIVADO:
                self.pos_graduac.deselect()
        elif event == 'pos':
            if self.var_pos_graduac.get() == ATIVADO:
                self.graduacao.deselect()
        elif event == '' and self.var_pos_graduac.get() == DESATIVADO and self.var_graduacao.get() == DESATIVADO:
            return False
        return True

    def acha_disciplina(self, event = ENTER):
        '''Chama a função dentro de pre-req passando a disciplina deseja e tendo como retorno um objeto disciplina'''
        
        ## Verifica se algum dos checkbuttons está selecionado ##
        if self.valida_checkbuttons() == False:
            self.info['text'] = 'Marque uma das opções acima...'
            return
        if not self.caixa_busca.get().strip().isdigit():
            self.info['text'] = 'Digite apenas números...'
            return
        
        self.info['text'] = ''

        if self.var_graduacao.get() == ATIVADO:
            self.disc = encontra_disc(self.caixa_busca.get().strip(), self.nivel.graduacao)
        else:
            self.disc = encontra_disc(self.caixa_busca.get().strip(), self.nivel.posgraduacao)

        self.descricao['state'] = NORMAL    #Habilita a edição no widget de descrição
        self.descricao.delete('1.0', END)   #Limpa o widget de descrição, caso contrário vai ficar inserindo
                                            #uma descrição abaixo da última realizada
        self.descricao['state'] = DISABLED  #Desabilita a edição no widget de descrição

        # Se não retornar erro permite que mostre a descrição da disciplina
        if self.disc.erro != '':
            self.info['text'] = self.disc.erro
        else:
            self.mostra_tudo_disc()

    def mostra_tudo_disc(self):
        '''Mostra a descrição da disciplina'''
        self.descricao['state'] = NORMAL # Habilita a edição
        self.descricao.tag_config('n', font=('Serif', 12, 'bold', 'italic'))
        self.descricao.tag_config('a', font=('Serif', 11))
        self.descricao.insert(END, '>>Nome: ', 'n')
        self.descricao.insert(END, self.disc.nome, 'a')

        self.descricao.insert(END, '>>Departamento: ', 'n')
        self.descricao.insert(END, self.disc.departamento, 'a')

        self.descricao.insert(END, '>>Código: ', 'n')
        self.descricao.insert(END, self.disc.codigo, 'a')

        self.descricao.insert(END, '>>Nível: ', 'n')
        self.descricao.insert(END, self.disc.nivel, 'a')

        self.descricao.insert(END, '>>Vigência: ', 'n')
        self.descricao.insert(END, self.disc.vigencia, 'a')

        self.descricao.insert(END, '>>Ementa: \n', 'n')
        self.descricao.insert(END, self.disc.ementa, 'a')

        self.descricao.insert(END, '>>Programa: \n', 'n')
        self.descricao.insert(END, self.disc.programa, 'a')

        self.descricao.insert(END,  '>>Bibliografia: \n', 'n')
        self.descricao.insert(END, self.disc.bibliografia, 'a')

        self.gera_img_prereq()
        #self.descricao.insert(END,  '>>Pré-requisitos: \n', 'n')
        #self.descricao.insert(END, self.disc.pre_requisitos, 'a')
        #print(self.disc.pre_requisitos)

        self.descricao['state'] = DISABLED # Disabilita a edição
    
    def limpa_busca_anterior(self):
        '''Exclui os arquivos das buscas anteriores'''
        path = "img"
        dir = os.listdir(path)
        for file in dir:
            if file != '.gitkeep': # O arquivo .gitkeep é necessário pois o github não aceita pastas vazias
                os.remove('%s/%s' %(path, file))

    def gera_img_prereq(self):
        '''Gera as imagens onde estaram contidas os pré-requisitos das disciplinas'''
        self.imag_preq = [] # Lista de digrafos
        
        self.limpa_busca_anterior()

        #Adiciona os grafos e suas devidas informações à lista
        for x in range(len(self.disc.pre_requisitos)):
            self.imag_preq.append(Graph()) 
            self.imag_preq[x].add_edges(self.disc.pre_requisitos[x])
            self.imag_preq[x].plot('graph%i' %x)

            #Limpa o conteúdo dentro do grafo
            self.imag_preq[x].clear()
        
        self.opcoes_de_cursar()        

    def opcoes_de_cursar(self):
        '''Pega os pré-requisitos em formatos de imagem e os adiciona ao programa'''
        self.info_janelas = Label(self.instancia, fg = 'green')
        self.info_janelas['text'] = '''Cada janela mostrada logo abaixo é uma forma diferente de se cursar 
        a disciplina desejada, ou seja, pode cursar a disciplina desejada tentando pela cadeia de matérias
        mostradas na janela 1, ou pela janela 2, e assim por diante...'''
        self.info_janelas.grid(row = 0, column = 1)

        self.list_janelas = []
        self.list_canvas = []
        self.list_sbar = []
        n = ttk.Notebook(self.instancia)

        for x in range(len(self.disc.pre_requisitos)):
            self.list_janelas.append(ttk.Frame(n)) #Cada índice da lista é uma página
            n.add(self.list_janelas[x], text= ' ' + str(x) + ' ' ) # Título das páginas, os espaços fazem com que o lugar em que o número vai ficar o caiba
            n.grid(row = 1, column= 1, rowspan = 2, padx = 20, pady = 10, sticky = N)
            
            self.list_canvas.append(Canvas(self.list_janelas[x], width = self.wsize_canv, height = self.hsize_canv, bg = 'white'))

            imagem = Img.open("img/graph%i.gif" %x)
            imagem_phot = ImageTk.PhotoImage(imagem)

            #tam = imagem.size #tam = (width, height)

            self.list_canvas[x].create_image(0,0, image=imagem_phot, anchor=NW)
            self.list_canvas[x].imagem = imagem_phot    

            ## Scrollbar no canvas ##
            if imagem.size[1] >= self.hsize_canv:
                self.list_canvas[x].config(scrollregion=(0,0, 0, imagem.size[1]))
            else:
                self.list_canvas[x].config(scrollregion=(0,0, 0, self.hsize_canv))

            #self.list_canvas[x].config(scrollregion=(0,0, 0, 1000))         
            self.list_canvas[x].config(highlightthickness=0)          
            self.list_sbar.append(Scrollbar(self.list_janelas[x]))
            self.list_sbar[x].config(command=self.list_canvas[x].yview)                   
            self.list_canvas[x].config(yscrollcommand=self.list_sbar[x].set)              
            self.list_sbar[x].pack(side=RIGHT, fill=Y)                     
            self.list_canvas[x].pack(side=LEFT, expand=YES, fill=BOTH) 

            ## Controlando Scrollbar com bora do mouse ## 
            self.list_canvas[x].bind('<Button-5>', lambda event : self.list_canvas[x].yview('scroll', 1, 'units'))  # Mover imagem para cima
            self.list_canvas[x].bind('<Button-4>', lambda event : self.list_canvas[x].yview('scroll', -1, 'units')) # Mover imagem para baixo

            #self.lab_frame = ttk.Frame(self.instancia)

instancia = Tk()
instancia.title('Pre-req')
instancia.geometry(RESOLUTION) # Cria o widget principal com o mesmo tamanho da tela do usuário
Buscador(instancia)
instancia.mainloop()