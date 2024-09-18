import test
import Menu2

def OpenScene(sceneName):
    # Remove the sleep delay for smoother transitions
    if sceneName == 'Menu2':
        Menu2.Menu()
    elif sceneName == "Game":
        test.Game()
