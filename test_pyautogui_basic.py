import pyautogui
import time

print("You have 3 seconds to switch to a text editor or input box...")
time.sleep(3)

pyautogui.typewrite("Hello from PyAutoGUI!\n", interval=0.1)
pyautogui.press("enter")
pyautogui.press("tab")
