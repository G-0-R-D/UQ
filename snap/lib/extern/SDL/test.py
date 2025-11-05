
from snap.lib.extern.SDL import *

WIDTH = 800
HEIGHT = 600
DELAY = 3000

def main():
  
  if SDL_Init(SDL_INIT_VIDEO) != 0:
    print("SDL failed to initialise:", SDL_GetError())
    return 1

  window = SDL_CreateWindow("SDL Example", #/* Title of the SDL window */
			    SDL_WINDOWPOS_UNDEFINED, #/* Position x of the window */
			    SDL_WINDOWPOS_UNDEFINED, #/* Position y of the window */
			    WIDTH, #/* Width of the window in pixels */
			    HEIGHT, #/* Height of the window in pixels */
			    0); #/* Additional flag(s) */

  if window == None:
    print("SDL window failed to initialise:", SDL_GetError())
    return 1

  print("num touch devices:", SDL_GetNumTouchDevices())

  SDL_Delay(DELAY)

  SDL_DestroyWindow(window)
  
  SDL_Quit()
  
  return 0


if __name__ == '__main__':

	main()
