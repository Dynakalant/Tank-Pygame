import pygame 

def mzflash(x,y,frame, len,ex_size,tur_cur_pos,tur_cur_angle):
    flashxoff = 130
    inc = 10
    blitRotate(screen,basepart, tur_cur_pos, (base_w/2-5, base_h/2+1), angle)
    if frame >= 0 and frame < 1*len:
        ex1 = pygame.image.load("flash\mz1.png").convert_alpha()
        ex1 = pygame.transform.scale(ex1, (ex_size*3, ex_size))
        blitRotate(screen,ex1, (rot[0],rot[1]), (ex_size*3/2 + flashxoff,ex_size/2), tur_cur_angle)
    elif frame >= 1*len and frame < 2*len:
        ex2 = pygame.image.load("flash\mz2.png").convert_alpha()
        ex2 = pygame.transform.scale(ex2, (ex_size*3, ex_size))
        blitRotate(screen,ex2, (rot[0],rot[1]), (ex_size*3/2 + flashxoff,ex_size/2), tur_cur_angle)
    elif frame >=2*len and frame < 3*len:
        ex3 = pygame.image.load("flash\mz3.png").convert_alpha()
        ex3 = pygame.transform.scale(ex3, (ex_size*3, ex_size))
        blitRotate(screen,ex3, (rot[0],rot[1]), (ex_size*3/2 + flashxoff,ex_size/2), tur_cur_angle)
    elif frame >= 3*len and frame < 4*len:
        ex4 = pygame.image.load("flash\mz4.png").convert_alpha()
        ex4 = pygame.transform.scale(ex4, (ex_size*3, ex_size))
        blitRotate(screen,ex4, (rot[0],rot[1]), (ex_size*3/2 + flashxoff,ex_size/2), tur_cur_angle)
    elif frame >= 4*len and frame < 5*len:
        ex5 = pygame.image.load("flash\mz5.png").convert_alpha()
        ex5 = pygame.transform.scale(ex5, (ex_size*3, ex_size))
        blitRotate(screen,ex5, (rot[0],rot[1]), (ex_size*3/2 + flashxoff,ex_size/2), tur_cur_angle)
    elif frame <= 6*len:
        all_flash.pop(0)
    
def explode(x,y,frame, len,ex_size):
    if frame >= 0 and frame < 1*len:
        ex1 = pygame.image.load("explosions\ex1.png").convert_alpha()
        ex1 = pygame.transform.scale(ex1, (ex_size, ex_size))
        screen.blit(ex1, (x-ex_size/2, y-ex_size/2))
    elif frame >= 1*len and frame < 2*len:
        ex2 = pygame.image.load("explosions\ex2.png").convert_alpha()
        ex2 = pygame.transform.scale(ex2, (ex_size, ex_size))
        screen.blit(ex2, (x-ex_size/2, y-ex_size/2))
    elif frame >=2*len and frame < 3*len:
        ex3 = pygame.image.load("explosions\ex3.png").convert_alpha()
        ex3 = pygame.transform.scale(ex3, (ex_size, ex_size))
        screen.blit(ex3, (x-ex_size/2, y-ex_size/2))
    elif frame >= 3*len and frame < 4*len:
        ex4 = pygame.image.load("explosions\ex4.png").convert_alpha()
        ex4 = pygame.transform.scale(ex4, (ex_size, ex_size))
        screen.blit(ex4, (x-ex_size/2, y-ex_size/2))
    elif frame >= 4*len and frame < 5*len:
        ex5 = pygame.image.load("explosions\ex5.png").convert_alpha()
        ex5 = pygame.transform.scale(ex5, (ex_size, ex_size))
        screen.blit(ex5, (x-ex_size/2, y-ex_size/2))
    elif frame >= 5*len and frame < 6*len:
        ex6 = pygame.image.load("explosions\ex6.png").convert_alpha()
        ex6 = pygame.transform.scale(ex6, (ex_size, ex_size))
        screen.blit(ex6, (x-ex_size/2, y-ex_size/2))
    elif frame >=6*len and frame <7*len:
        ex7 = pygame.image.load("explosions\ex7.png").convert_alpha()
        ex7 = pygame.transform.scale(ex7, (ex_size, ex_size))
        screen.blit(ex7, (x-ex_size/2, y-ex_size/2))
    elif frame >= 7*len and frame < 8*len:
        ex8 = pygame.image.load("explosions\ex8.png").convert_alpha()
        ex8 = pygame.transform.scale(ex8, (ex_size, ex_size))
        screen.blit(ex8, (x-ex_size/2, y-ex_size/2))
    elif frame >= 8*len and frame < 9*len:
        ex9 = pygame.image.load("explosions\ex9.png").convert_alpha()
        ex9 = pygame.transform.scale(ex9, (ex_size, ex_size))
        screen.blit(ex9, (x-ex_size/2, y-ex_size/2))
    elif frame >= 9*len and frame < 9*len + len:
        ex10 = pygame.image.load("explosions\ex10.png").convert_alpha()
        ex10 = pygame.transform.scale(ex10, (ex_size, ex_size))
        screen.blit(ex10, (x-ex_size/2, y-ex_size/2))
    else:
        all_explosions.pop(0)