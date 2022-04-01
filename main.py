import os.path
import sys
from tqdm import tqdm

import random
import pygame
import pycountry
import pygal
from pygal.style import Style
from os import path
from pathlib import Path
import glob

pygame.init()

WINDOW_SIZE = (3000, 1500)
WINDOW_SIZE_X, WINDOW_SIZE_Y = WINDOW_SIZE
FRAMERATE = 60

screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

BASE = path.abspath(path.join(__file__, ".."))
WORLDMAP_IMGS = path.join(BASE, "worldmap_imgs")


def get_country_name(code):
    return pycountry.countries.get(alpha_2=code.upper()[:2]).name


flag_paths = glob.glob(path.join(BASE, "w1280", "*.png"))
flag_sz = (800, 450)
flag_imgs = [(Path(flag_path).stem, pygame.image.load(flag_path)) for flag_path in flag_paths]
flag_imgs = [(cnt, pygame.transform.scale(flag, flag_sz)) for cnt, flag in flag_imgs]

pygal_style = Style(colors=('#FF0000', '#0000FF',
                             '#00FF00', '#000000',
                             '#FFD700'))
worldmap_imgs = {}
worldmap_bar = tqdm(flag_imgs)
os.makedirs(WORLDMAP_IMGS, exist_ok=True)
for cnt_code, _ in worldmap_bar:
    worldmap_bar.set_description(cnt_code)
    try:
        country = get_country_name(cnt_code)
    except AttributeError:
        continue
    worldmap_bar.set_description(f"{country} ({cnt_code})")
    png_path = path.join(WORLDMAP_IMGS, f"{cnt_code}.png")
    if not path.exists(png_path):
        worldmap = pygal.maps.world.World(style=pygal_style)
        worldmap.title = country.capitalize()
        worldmap.add("", [cnt_code])
        world_img_sz = WINDOW_SIZE_X-flag_sz[0], WINDOW_SIZE_Y
        worldmap.width, worldmap.height = world_img_sz
        worldmap.render_to_png(png_path, dpi=400)
    img = pygame.image.load(png_path)
    worldmap_imgs[cnt_code] = img

flag_imgs = [(cnt_code, flag) for cnt_code, flag in flag_imgs if cnt_code in worldmap_imgs]

text_colour = (200, 200, 200)
font = pygame.font.SysFont("Arial", 36)


def choose_flag():
    return random.choice(flag_imgs)



timer_steps = (10, 3, 0)
curcountry, curflag = choose_flag()
next_timer = timer_steps[0]
while True:
    screen.fill((0, 0, 0))
    screen.blit(font.render("Country Guesser!", True, text_colour), (30, 50))

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT | pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                print("Exiting normally...")
                pygame.display.quit()
                sys.exit()
            case pygame.MOUSEBUTTONDOWN if event.button == 1:
                for s in timer_steps:
                    if next_timer > s: next_timer = s; break
            case _: pass

    flag_loc = (000, 200)
    #pygame.draw.rect(curflag, text_colour, (*flag_loc, *flag_sz), 0, 10)
    screen.blit(curflag, flag_loc)
    below_flag_y = 230+flag_sz[1]
    below_flag_x = 30

    if next_timer <= timer_steps[1]:
        cur_worldmap = worldmap_imgs[curcountry]
        screen.blit(cur_worldmap, (flag_sz[0], 0))

        below_flag_text = f"Name: {get_country_name(curcountry)}"
    else:
        below_flag_text = f"Name: "
    screen.blit(font.render(below_flag_text, True, text_colour), (below_flag_x, below_flag_y))

    if next_timer <= timer_steps[-1]:
        curcountry, curflag = choose_flag()
        next_timer = timer_steps[0]


    pygame.display.update()
    dt = clock.tick(FRAMERATE)/ 1000
    next_timer -= dt

