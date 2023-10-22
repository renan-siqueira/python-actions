import os
import time
import json
import pyautogui
from pynput import mouse, keyboard

POSICAO_INICIAL = (10,10)

DIRETORIO_GRAVACOES = 'gravacoes'
if not os.path.exists(DIRETORIO_GRAVACOES):
    os.mkdir(DIRETORIO_GRAVACOES)

acoes = []
gravando = False
abortar_reproducao = False

def selecionar_opcao(opcoes):
    for i, opcao in enumerate(opcoes, 1):
        print(f"{i}. {opcao}")

    escolha = 0
    while not (1 <= escolha <= len(opcoes)):
        try:
            escolha = int(input(f"Selecione uma opção (1-{len(opcoes)}): "))
        except ValueError:
            pass

    return opcoes[escolha - 1]

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
        pyautogui.moveTo(*POSICAO_INICIAL)
        print("Gravação iniciada. Pressione 'Esc' para parar.")
    elif key == keyboard.Key.esc and gravando:
        gravando = False
        print("Gravação terminada.")
        return False

def gravar_acoes():
    global acoes

    print("Pressione '1' para começar a gravação...")

    with mouse.Listener(on_move=on_move, on_click=on_click) as m_listener:
        with keyboard.Listener(on_release=on_key_release) as k_listener:
            k_listener.join()

    nome_gravacao = input("Digite um nome para esta gravação: ")
    caminho_arquivo = os.path.join(DIRETORIO_GRAVACOES, nome_gravacao + '.json')

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

def escutar_tecla_abortar(key):
    global abortar_reproducao
    if key == keyboard.KeyCode.from_char('q'):
        abortar_reproducao = True
        return False

def reproduzir_acoes(reproduzir_movimentos=True):
    global abortar_reproducao

    listener = keyboard.Listener(on_press=escutar_tecla_abortar)
    listener.start()

    pyautogui.moveTo(*POSICAO_INICIAL)
    time.sleep(1)

    if reproduzir_movimentos:
        pyautogui.PAUSE = 0.005  # movimento mais rápido
    else:
        pyautogui.PAUSE = 0.3  # velocidade padrão

    for acao in acoes:
        if abortar_reproducao:
            print("Reprodução abortada!")
            abortar_reproducao = False
            break
        if acao[0] == 'move' and reproduzir_movimentos:
            pyautogui.moveTo(acao[1], acao[2])
        elif acao[0] == 'click':
            if acao[3] == 'left':
                pyautogui.click(acao[1], acao[2], button='left')
            elif acao[3] == 'right':
                pyautogui.click(acao[1], acao[2], button='right')

    listener.stop()

def main():
    while True:
        opcao = selecionar_opcao(["Gravar", "Carregar", "Reproduzir", "Sair"]).lower()

        if opcao == "gravar":
            gravar_acoes()
        elif opcao == "carregar":
            carregar_acoes()
            print("Ações carregadas com sucesso!")
        elif opcao == "reproduzir":
            movimentos = selecionar_opcao(["Reproduzir movimento", "Somente cliques"]).lower()
            reproduzir_acoes(reproduzir_movimentos=(movimentos == 'reproduzir movimento'))
        elif opcao == "sair":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
