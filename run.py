import os
import time
import pyautogui
import json
from pynput import mouse, keyboard


POSICAO_INICIAL = (10,10)

DIRETORIO_GRAVACOES = 'gravacoes'
if not os.path.exists(DIRETORIO_GRAVACOES):
    os.mkdir(DIRETORIO_GRAVACOES)

acoes = []
gravando = False

def on_move(x, y):
    if gravando:
        acoes.append(('move', x, y))

def on_click(x, y, button, pressed):
    if gravando and pressed:
        acoes.append(('click', x, y, button.name))

def on_key_release(key):
    global gravando
    if key == keyboard.KeyCode.from_char('1') and not gravando:
        gravando = True
        pyautogui.moveTo(*POSICAO_INICIAL)  # Mova para o ponto inicial ao iniciar a gravação
        print("Gravação iniciada. Pressione 'Esc' para parar.")
    elif key == keyboard.Key.esc and gravando:
        gravando = False
        print("Gravação terminada.")
        return False  # Encerrar o listener

def gravar_acoes():
    global acoes

    print("Pressione '1' para começar a gravação...")
    
    with mouse.Listener(on_move=on_move, on_click=on_click) as m_listener:
        with keyboard.Listener(on_release=on_key_release) as k_listener:
            k_listener.join()

    nome_gravacao = input("Digite um nome para esta gravação: ")
    caminho_arquivo = os.path.join(DIRETORIO_GRAVACOES, nome_gravacao + '.json')

    # Salva as ações em um arquivo
    with open(caminho_arquivo, 'w') as f:
        json.dump(acoes, f)

def carregar_acoes():
    global acoes
    gravacoes = os.listdir(DIRETORIO_GRAVACOES)

    for index, gravacao in enumerate(gravacoes):
        print(f"{index}. {gravacao}")

    escolha = int(input("Digite o número da gravação que deseja carregar: "))
    caminho_arquivo = os.path.join(DIRETORIO_GRAVACOES, gravacoes[escolha])

    with open(caminho_arquivo, 'r') as f:
        acoes = json.load(f)

def reproduzir_acoes(velocidade='normal', reproduzir_movimentos=True):
    # Mova o mouse para a posição inicial antes de reproduzir
    pyautogui.moveTo(*POSICAO_INICIAL)
    time.sleep(1)

    duracao_movimento = 0.1 if velocidade == 'normal' else 0.01
    duracao_espera = 0.1 if velocidade == 'normal' else 0.01

    for acao in acoes:
        if acao[0] == 'move' and reproduzir_movimentos:
            pyautogui.moveTo(acao[1], acao[2], duration=duracao_movimento)
        elif acao[0] == 'click':
            if acao[3] == 'left':
                pyautogui.click(acao[1], acao[2], button='left')
            elif acao[3] == 'right':
                pyautogui.click(acao[1], acao[2], button='right')
            time.sleep(duracao_espera)

def main():
    while True:
        opcao = input("\nEscolha uma opção (gravar/carregar/reproduzir/sair): ").lower()
        if opcao == "gravar":
            gravar_acoes()
        elif opcao == "carregar":
            carregar_acoes()
            print("Ações carregadas com sucesso!")
        elif opcao == "reproduzir":
            velocidade = input("Escolha a velocidade (rápido/normal): ").lower()
            movimentos = input("Deseja reproduzir movimentos? (sim/nao): ").lower()
            reproduzir_acoes(velocidade)
        elif opcao == "sair":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
