import os
import time
import json
import pyautogui
from pynput import mouse, keyboard

INITIAL_POSITION = (10,10)

RECORDINGS_DIRECTORY = 'recordings'
if not os.path.exists(RECORDINGS_DIRECTORY):
    os.mkdir(RECORDINGS_DIRECTORY)

actions = []
recording = False
abort_playback = False

def select_option(options):
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    choice = 0
    while not (1 <= choice <= len(options)):
        try:
            choice = int(input(f"Select an option (1-{len(options)}): "))
        except ValueError:
            pass

    return options[choice - 1]

def on_move(x, y):
    if recording:
        actions.append(('move', x, y))

def on_click(x, y, button, pressed):
    if recording and pressed:
        actions.append(('click', x, y, button.name))

def on_key_release(key):
    global recording
    if key == keyboard.KeyCode.from_char('1') and not recording:
        recording = True
        pyautogui.moveTo(*INITIAL_POSITION)
        print("Recording started. Press 'Esc' to stop.")
    elif key == keyboard.Key.esc and recording:
        recording = False
        print("Recording stopped.")
        return False

def record_actions():
    global actions

    print("Press '1' to start recording...")

    with mouse.Listener(on_move=on_move, on_click=on_click) as m_listener:
        with keyboard.Listener(on_release=on_key_release) as k_listener:
            k_listener.join()

    recording_name = input("Enter a name for this recording: ")
    file_path = os.path.join(RECORDINGS_DIRECTORY, recording_name + '.json')

    with open(file_path, 'w') as f:
        json.dump(actions, f)

def load_actions():
    global actions
    recordings = os.listdir(RECORDINGS_DIRECTORY)

    for index, recording in enumerate(recordings):
        print(f"{index}. {recording}")

    choice = int(input("Enter the number of the recording you wish to load: "))
    file_path = os.path.join(RECORDINGS_DIRECTORY, recordings[choice])

    with open(file_path, 'r') as f:
        actions = json.load(f)

def listen_abort_key(key):
    global abort_playback
    if key == keyboard.KeyCode.from_char('q'):
        abort_playback = True
        return False

def playback_actions(play_movements=True):
    global abort_playback

    listener = keyboard.Listener(on_press=listen_abort_key)
    listener.start()

    pyautogui.moveTo(*INITIAL_POSITION)
    time.sleep(1)

    if play_movements:
        pyautogui.PAUSE = 0.005  # faster movement
    else:
        pyautogui.PAUSE = 0.3  # default speed

    for action in actions:
        if abort_playback:
            print("Playback aborted!")
            abort_playback = False
            break
        if action[0] == 'move' and play_movements:
            pyautogui.moveTo(action[1], action[2])
        elif action[0] == 'click':
            if action[3] == 'left':
                pyautogui.click(action[1], action[2], button='left')
            elif action[3] == 'right':
                pyautogui.click(action[1], action[2], button='right')

    listener.stop()

def main():
    while True:
        option = select_option(["Record", "Load", "Playback", "Exit"]).lower()

        if option == "record":
            record_actions()
        elif option == "load":
            load_actions()
            print("Actions successfully loaded!")
        elif option == "playback":
            movements = select_option(["Play movements", "Clicks only"]).lower()
            playback_actions(play_movements=(movements == 'play movements'))
        elif option == "exit":
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
