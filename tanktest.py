#d: The website where i got the blitRotate function from: https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
#d: The website where i got the base shooting function from: (its the second response by furas, under the one which says "mimimal working example"): https://stackoverflow.com/questions/63495823/how-to-shoot-a-bullet-towards-mouse-cursor-in-pygame

import pygame 
import random
import timeit
import math

from tanks import all_tanks

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1250
SCREEN_HEIGHT = 725

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

screen_rect = screen.get_rect()
pygame.display.set_caption("Tank")

clock = pygame.time.Clock()

player_current_tank = "M1A1HA"
player_current_tank_specs = all_tanks[player_current_tank]

player_tank_hull = pygame.transform.scale((pygame.image.load(player_current_tank_specs["hull_sprite"]).convert_alpha()), (60,30)) #<- variablized?
player_tank_turret = pygame.transform.scale((pygame.image.load(player_current_tank_specs["turret_sprite"]).convert_alpha()), (74.5, 30))

T72_SCALE = (82, 33)
t72_tank_hull = pygame.transform.scale((pygame.image.load("vehicle_sprites\T72M1_hull.png").convert_alpha()), T72_SCALE)
t72_tank_turret = pygame.transform.scale((pygame.image.load("vehicle_sprites\T72M1_turret.png").convert_alpha()), T72_SCALE)

FIELD_BASESIZE = (15872, 10580)
field_base = pygame.transform.scale((pygame.image.load("field.png").convert_alpha()), FIELD_BASESIZE)

MAX_FPS = 60
# FPS Storage Variables, don't touch. 
fps, fps_record, time_check = 0, 0, 0

myfont = pygame.font.Font(None,25)

BACKGROUND_COLOR = (40,94,33)

TURN_SPEED_SEC = player_current_tank_specs = player_current_tank_specs["hull_turn_speed_sec"]
turn_speed = 360/(TURN_SPEED_SEC * MAX_FPS)

angle = 0
turret_angle = 0 #1080
x_mov, y_mov, mov = 0, 0, 0
TURRET_TURN_SPEED_SEC = 9 #Seconds it takes to rotate 360 degrees
turret_turn_speed_org = 360/(TURRET_TURN_SPEED_SEC * MAX_FPS)
turret_turn_speed = turret_turn_speed_org
ACCELERATION = 0.012
STOP_ACCELERATION = 0.012
turn_modifier = 0
max_speed = 3
max_speed_reverse = max_speed / 1.3
player_x_pos = SCREEN_WIDTH / 2
player_y_pos = SCREEN_HEIGHT / 2

player_width, player_height = player_tank_hull.get_size()
turret_width, turret_height = player_tank_turret.get_size()

#FIX THIS>... WHY DOES T72 HULL USE M1 SIZE>???
bot_width, bot_height = player_tank_hull.get_size()
bot_turret_width, bot_turret_height = player_tank_turret.get_size()


engine_on = True

class Player:
    def __init__(self):
        self.hull_angle = 0
        self.turret_angle = self.hull_angle
        self.screen_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.screen_pos_org = self.screen_pos
        self.world_pos = ""
        self.velocity = 0
        self.x_velocity = 0
        self.y_velocity = 0
        self.turn_modifier = 0
        self.TURN_SPEED = ""
        self.ACCELERATION = ""
        self.STOP_ACCELERATION = ""
        self.MAX_SPEED = ""
        self.MAX_REVERSE_SPEED = ""
        self.hull_width = ""
        self.hull_height = ""
        self.turret_width = ""
        self.turret_height = ""
        self.hull_sprite = ""
        self.turret_sprite = ""

#useless???
class Tank:
    def __init__(self, vehicle_type, health, acceleration, stop_acceleration, top_speed, top_reverse_speed):
        self.vehicle_type = vehicle_type
        self.health = health
        self.acceleration = acceleration
        self.stop_acceleration = stop_acceleration
        self.top_speed = top_speed
        self.top_reverse_speed = top_reverse_speed

class Ammo:
    def __init__(self, type, penetration, velocity, damage, amount):
        self.type = type
        self.penetration = penetration
        self.velocity = velocity
        self.damage = damage
        self.amount = amount

class Background_Object:
    def __init__(self, screen_pos, image):
        self.screen_pos = screen_pos
        self.screen_pos_org = screen_pos
        self.image = image
    def update_position(self, player_x_mov, player_y_mov, mod_x, mod_y):
        self.screen_pos_org[0] += player_x_mov
        self.screen_pos_org[1] += player_y_mov
        self.screen_pos[0] = self.screen_pos_org[0] - mod_x
        self.screen_pos[1] = self.screen_pos_org[1] - mod_y

# potentially in the future integrate all explosion handlers to one frame animator function. Also want to put the classes into another folder.
class Gif_Rico_Impact:
    def __init__(self, screen_pos, angle, offset, frames_per_frame):
        self.screen_pos = screen_pos
        self.angle = angle
        self.offset = offset
        self.current_frame = 0
        self.frames_per_frame = frames_per_frame

#take into account that the screen pos and the world pos can't initally be the same, since zoom is now set to 1 instead of 0 -- the original screen pos is not initially the center of the screen anymore, its 1 pixel off.
        
class Gif:
    def __init__(self, screen_pos, screen_pos_org, world_pos, angle, offset, frames_per_frame):
        self.screen_pos = screen_pos
        self.screen_pos_org = screen_pos_org
        self.world_pos = (0,0)
        self.angle = angle
        self.offset = offset
        self.current_frame = 0
        self.frames_per_frame = frames_per_frame
    def update_position(self, player_x_mov, player_y_mov, mod_x, mod_y):
        self.screen_pos_org[0] += player_x_mov
        self.screen_pos_org[1] += player_y_mov
        self.screen_pos[0] = self.screen_pos_org[0] - mod_x
        self.screen_pos[1] = self.screen_pos_org[1] - mod_y

current_ammo = "M829A1"
ammunition_options = {}

ammunition_options["M829"] = Ammo("APFSDS", 540, 360, 7250, 5)
ammunition_options["M829A1"] = Ammo("APFSDS", 600, 400, 7500, 20)
ammunition_options["M830"] = Ammo("HEATFS", 630, 310, 10000, 15)
 
ammunition_options_list = [ammo_name for ammo_name in ammunition_options.keys()]
current_ammo_index = ammunition_options_list.index(current_ammo)


bullet_width = 2

reload_time = 125
reload_time_mod = reload_time
reload_fatigue = 0
reload = 0
damage_amt = 10000
player_health = 40000
ZOOM_MAX = 400

zoom_x, zoom_y = 0, 0

all_world_objects = {'Player': [], 'Objects': [], 'Bots': [], 'Projectiles': [], 'Hitboxes': [], 'Explosions': [], 'Muzzleflash': [], 'ImpRico': [], 'Sounds': []}

all_world_objects['Objects'].append(Background_Object([-5000,-5000], field_base))

PLAYER_MSP = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2] #midpoint screen pos
PLAYER_MSP2 = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

BOT_MSP = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2] #midpoint screen pos
BOT_MSP2 = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

all_world_objects['Player'] = [PLAYER_MSP, PLAYER_MSP2, [1000 + SCREEN_WIDTH / 2, 1000 + SCREEN_HEIGHT / 2], 40000, 1]

t72_armor_layout = [380, 100, 140, 140]

all_world_objects['Bots'].append([BOT_MSP, BOT_MSP2, [1000 + SCREEN_WIDTH / 2, 1000 + SCREEN_HEIGHT / 2], 10000,t72_tank_hull,t72_tank_turret, 35, [], t72_armor_layout, "T-72M", 35, 65])

#yes = ['screen_pos', 'screen_pos_org', 'world_pos'], health, zoomsssssssssss

m1a1_armor_layout = [430, 160, 160, 110]

ex_size = 30
mz_size = 30
rico_size = 30
imp_size = 30

gif_frames = {}

muzzle120_frames = []
#create muzzle flash sprites
for i in range(1,10): muzzle120_frames.append(pygame.transform.scale(pygame.image.load(f"flash\mz{i}.png").convert_alpha(), (mz_size*3, mz_size)))
gif_frames['muzzle120_frames'] = muzzle120_frames

explosion_frames = []
for i in range(1,11): explosion_frames.append(pygame.transform.scale(pygame.image.load(f"explosions\ex{i}.png").convert_alpha(), (ex_size, ex_size)))
gif_frames['explosion_frames'] = explosion_frames

armor_impact_frames = []
for i in range(1,13): armor_impact_frames.append(pygame.transform.scale(pygame.image.load(f"armor_impacts\imp{i}.png").convert_alpha(), (imp_size, imp_size)))
gif_frames['armor_impact_frames'] = armor_impact_frames

ricochet_impact_frames = []
for i in range(1,9): ricochet_impact_frames.append(pygame.transform.scale(pygame.image.load(f"impact_ricochet\imp_rico{i}.png").convert_alpha(), (rico_size, rico_size)))
gif_frames['ricochet_impact_frames'] = ricochet_impact_frames

soundpacks = {"m256shot": ((4000, "m256shot.wav"), (0, "m256shot_far.wav"))}
sounds = []

log = []
log_buffer = 400
log_wait = log_buffer

hours, minutes, seconds = 0, 0, 0

def turn(turn_direction):
    global angle
    global turret_angle
    global mov
    global turn_modifier
    turn_modifier = turn_direction  + (turn_direction * (abs(mov)/2 if abs(mov) > 0 else 0))
    angle += turn_modifier
    turret_angle += turn_modifier
    if mov > 0:
        mov -= STOP_ACCELERATION + (STOP_ACCELERATION * (abs(mov) if abs(mov) > 0 else 0))
        if mov < 0:
            mov = 0
    elif mov < 0:
        mov += STOP_ACCELERATION  + (STOP_ACCELERATION * (abs(mov) if abs(mov) > 0 else 0))
        if mov > 0:
            mov = 0

def rolling_stop_l(stop_accel):
    global mov
    mov -= stop_accel
    if mov < 0:
        mov = 0

def rolling_stop_r(stop_accel):
    global mov
    mov += stop_accel
    if mov > 0:
        mov = 0

def blitRotate(surf, image, pos, originPos, angle, offset=0, type="blit"):
    global rot 
    # makes a rectangle based on the image. Pos - originpos is used to find the point which we want the image
    # to rotate around. For example, in most cases, I want to spin the image around the center, so I make pos
    #as the coordinate of the image and origin_pos as half the base and height.
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1] - originPos[1]))

    #d: dont really know what this does, it seems to be minusing the rectangle image's center from the actual center inputted into the function.
    #pygame math vector2 pos: basically a vector of the position (which might be the same thing anyway)
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    #print(f'{rotated_offset} + {angle}')
    #d: i presume this somehow changes the center of the rotated image to match the original center of the image. again, dont know how.
    # roatetd image center
    rotated_image_center = [pos[0] - rotated_offset.x, pos[1] - rotated_offset.y]

    x_var = offset * math.cos(math.radians(angle))
    y_var = -1 * offset * math.sin(math.radians(angle))
    rotated_image_center = (rotated_image_center[0] + x_var, rotated_image_center[1] + y_var)
    #d: I added this one in, to assign the tuple to a variable so that i can make the center position of the helicopter rotor when i call this function
    #d: again for rotating the rotor. See, i cant just have the rotor center be the helicopter's center, since the rotor's correct visual position 
    #d: on the helicopter isnt actually in the center but actually offset. And i have to compensate for changing these coordinates whenever i rotate
    #d: the helicopter (the rotor must stay in the same spot during rotation, it sounds simple but its actually quite complicated, and this was quite 
    #d: an annoying problem for me for some time).  Theres probably a better way to do it, but for now, ive settled with doing it this way.
    rot = rotated_image_center
    #d: rotates the image and makes a rectangle of the rotated image using whatever witchcraft they did previously in the function. 
    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    #d: and makes the image on the board.
    # rotate and blit the image
    if type == "blit":
        surf.blit(rotated_image, rotated_image_rect)
    elif type == "rot":
        return (rotated_image, rotated_image_rect)
    #d: this was included in the orignal copy pasted funcion, this draws a rectangle around the images that are being rotated, but since i have no 
    #d: use for this, i decided to just comment it because it might be handy later.
    #pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)

def rotPoint(origin, x_off, y_off, angle):
    #returns the position of a theoretical point, offset from an origin point, rotated around an origin.
    #example: plotting points for the outside corners of a rotated rectangular image.
    x_off, y_off = x_off * -1, y_off * -1 # to account for the wierdness of pygame windows (y increasing goes down not up)
    ang_rad = math.radians(angle)
    x = origin[0] + x_off * math.cos(ang_rad) * -1 - y_off * math.sin(ang_rad)
    y = origin[1] + x_off * math.sin(ang_rad) - y_off * math.cos(ang_rad)
    return (x, y)

def player_object_movement(object, player_x_mov, player_y_mov, mod_x, mod_y):
    object.screen_pos_org[0] += player_x_mov
    object.screen_pos_org[1] += player_y_mov
    object.screen_pos[0] = object.screen_pos_org[0] - mod_x
    object.screen_pos[1] = object.screen_pos_org[1] - mod_y


    """
    object[0][0] = object[1][0] - zoom_x
    object[0][1] = object[1][1] - zoom_y
    object[0][0] += x_mov
    object[0][1] += y_mov
    object[1][0] += x_mov
    object[1][1] += y_mov
    """

def play_gif(render_list, objects_list, surface, frame_pack, object, max_frame, origin_pos, layer):
    render_list.append([layer, [[surface, gif_frames[frame_pack][math.floor(object.current_frame)], object.screen_pos, origin_pos, object.angle, object.offset]], 'blitrotate'])
    if object.current_frame < max_frame:
        #current frame NEVER CHANGES.
        object.current_frame += 1 / object.frames_per_frame
    else:
        all_world_objects[objects_list].pop(0)

bot_hitbox_fb = pygame.transform.scale((pygame.image.load("hitbox.png").convert_alpha()), (4, 22))
bot_hitbox_rl = pygame.transform.scale((pygame.image.load("hitbox.png").convert_alpha()), (42, 4))

bot_hb_dis_fb = 30
bot_hb_dis_rl = 46
hfb_width, hfb_height = bot_hitbox_fb.get_size()

sun_angle = 45
intensity = 8
darkness = 128
shift = (intensity * math.cos(math.radians(sun_angle)), intensity * math.sin(math.radians(sun_angle)))

start = timeit.default_timer()
run = True

pygame.mixer.set_num_channels(100)

ENGINE_VOL = 0.10
engine_channel_1  = pygame.mixer.Channel(98)
engine_channel_2 = pygame.mixer.Channel(99)
elapsed_time = 100000000
engine_current_channel = 1
engine_current_sound_name = "idle"
engine_prev_sound_name = "idle"
spool_percentage = 0.0
prev_play = False

engine_idle = pygame.mixer.Sound("m1_engine_sounds\m1_engine_idle.wav")
engine_up = pygame.mixer.Sound("m1_engine_sounds\m1_engine_up.wav")
engine_down = pygame.mixer.Sound("m1_engine_sounds\m1_engine_down.wav")
engine_high = pygame.mixer.Sound("m1_engine_sounds\m1_engine_high.wav")

SOUNDS_REPEAT_ACCOUNTER = 41
m1_engine_sounds = {"idle": (engine_idle, math.floor(engine_idle.get_length() * 1000) - SOUNDS_REPEAT_ACCOUNTER),
                    "up": (engine_up, math.floor(engine_up.get_length() * 1000) - SOUNDS_REPEAT_ACCOUNTER),
                    "down": (engine_down, math.floor(engine_down.get_length() * 1000) - SOUNDS_REPEAT_ACCOUNTER),
                    "high": (engine_high, math.floor(engine_high.get_length() * 1000) - SOUNDS_REPEAT_ACCOUNTER),
                    }

current_engine_sound_soundobject = m1_engine_sounds["idle"][0]

TRACK_VOL = 0.16
TRACK_BASE_BASE_DELAY = 10
track_base_delay = TRACK_BASE_BASE_DELAY
track_delay = track_base_delay
track = pygame.mixer.Sound("m1_engine_sounds\m1_track.wav")

target_on = False

pygame.mouse.set_visible(False)

# Main loop
while run:
    screen.fill(BACKGROUND_COLOR)

    objects_to_render = []
    shadows = []

    keys = pygame.key.get_pressed()
    mouseclick = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            #engine turnon/off, to be added later?
            if event.key == pygame.K_u:
                if engine_on: engine_on = False
                elif not engine_on: engine_on = True
            if event.key == pygame.K_v:
                if target_on: target_on = False
                elif not target_on: target_on = True
            if event.key == pygame.K_1:
                current_ammo_index = current_ammo_index + 1 if current_ammo_index < len(ammunition_options_list) - 1 else 0
                current_ammo = ammunition_options_list[current_ammo_index]
                reload = reload_time
            if event.key == pygame.K_ESCAPE:
                pass
                #pause
        if event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()
    
    #reset the angle(s) so it doesnt go over 360
    if abs(angle) >= 360:
        angle = 0
    if abs(turret_angle) >= 360:
        turret_angle = 0

    turn_modifier = 0
    zoom = 0

    if player_health > 0:
        if keys[pygame.K_w]:
            if mov >= 0 and mov <= max_speed:
                mov += ACCELERATION / (mov * 2 if abs(mov) >= 1 else 1)
            elif mov < 0:
                rolling_stop_r(STOP_ACCELERATION + ACCELERATION)
        elif keys[pygame.K_s]:
            if mov <= 0 and mov >= -1 * max_speed_reverse:
                mov -= ACCELERATION / (mov * 2 if mov >= 1 else 1)
            elif mov > 0:
                rolling_stop_l(STOP_ACCELERATION + ACCELERATION)
        if keys[pygame.K_a]:
            turn(turn_speed)
        elif keys[pygame.K_d]:
            turn(-1 * turn_speed)
        if mov > 0 and not keys[pygame.K_w]:
            rolling_stop_l(STOP_ACCELERATION)
        elif mov < 0 and not keys[pygame.K_s]:
            rolling_stop_r(STOP_ACCELERATION)

        if keys[pygame.K_q]: zoom = 30
        elif keys[pygame.K_e]: zoom = -30
        
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            if engine_current_sound_name != "high":
                engine_current_sound_name = "up" 
        else:
            if engine_current_sound_name != "idle":
                engine_current_sound_name = "down"
        #print(engine_current_sound_name)


        engine_current_tuple = m1_engine_sounds[engine_current_sound_name]
        if engine_current_sound_name != engine_prev_sound_name: #if the sound has changed 
            current_engine_sound_soundobject = engine_current_tuple[0]
            '''
            if (engine_prev_sound_name == "up" or engine_prev_sound_name == "down") and (engine_current_sound_name != "up" or engine_current_sound_name !="down"):
                spoolup = elapsed_time / (m1_engine_sounds[engine_prev_sound_name][0].get_length() * 1000) #percentage of how much the prev sound was completed, if it was a spool
                
                cutoff = 6
                if engine_prev_sound_name == "down":
                    if elapsed_time <= m1_engine_sounds[engine_current_sound_name][0].get_length() * 1000 / cutoff:
                        spoolup = spoolup * cutoff
                    else:
                        spoolup = 0
                elif engine_prev_sound_name == "up":
                    e = spoolup
                    spoolup = spoolup / cutoff
                    print(e, cutoff, spoolup)
                
                print(spoolup)
                sound_array = engine_current_tuple[0].get_raw()

                slice_index = (math.floor(len(sound_array) * spoolup - len(sound_array)))
                slice_index = slice_index + 1 if slice_index % 2 else slice_index #sound array statics when slice index is odd (for some reason), so make it even if odd.

                split_sound = sound_array[slice_index:]
                #print(math.floor(len(sound_array) * spoolup), len(sound_array))
                current_engine_sound_soundobject = pygame.mixer.Sound(buffer=split_sound)

                elapsed_time = math.ceil(spoolup * m1_engine_sounds[engine_current_sound_name][0].get_length() * 1000)
            else:
                elapsed_time = 0
            '''
            #need to redo this whole thing, I have lost my mind.
            elapsed_time = 0

            if engine_current_channel == 1:
                engine_channel_2.play(current_engine_sound_soundobject)
                engine_current_channel = 2
            elif engine_current_channel == 2:
                engine_channel_1.play(current_engine_sound_soundobject)
                engine_current_channel = 1

            if engine_current_channel == 1: 
                engine_channel_2.stop()
            elif engine_current_channel == 2: 
                engine_channel_1.stop()

            engine_prev_sound_name = engine_current_sound_name
        else:
            elapsed_time += clock.get_time()
            if elapsed_time >= engine_current_tuple[1]:
                if engine_current_sound_name== "up":
                    engine_current_sound_name = "high"
                elif engine_current_sound_name == "down":
                    engine_current_sound_name = "idle"
                else:
                    if engine_current_channel == 1:
                        engine_channel_2.play(engine_current_tuple[0])
                        engine_current_channel = 2
                    elif engine_current_channel == 2:
                        engine_channel_1.play(engine_current_tuple[0])
                        engine_current_channel = 1 
                    elapsed_time = 0
        
        engine_channel_1.set_volume(ENGINE_VOL)
        engine_channel_2.set_volume(ENGINE_VOL)
        
        
        #uses a quadratic formula to spam track sounds, increasing as the tank's movemnet gets faster.
        track_base_delay = TRACK_BASE_BASE_DELAY - (-1 * 1.08333 * (abs(mov) ** 2) + (6.58333  * abs(mov)))
        track_base_delay -= (abs(turn_modifier) * 9) - (abs(mov) * 5 if turn_modifier != 0 else 0) # this accounts for the tank's turning for track sounds
        if track_delay <= 0 and ((mov != 0) or (turn_modifier != 0)):
            track_channel = pygame.mixer.find_channel()
            if track_channel:
                track_sound = pygame.mixer.Sound(track)

                track_sound.set_volume(TRACK_VOL)
                track_channel.play(track_sound)
            track_delay += track_base_delay
        elif track_delay > 0:
            track_delay -= 1
    else:
        mov = mov - STOP_ACCELERATION if mov < 0 else mov + STOP_ACCELERATION if mov < 0 else 0

    #calculating the directional movement of the vehicle based on the vehicle's current angle, using sin and cos.
    x_mov = mov * math.cos(math.radians(angle))
    y_mov = -1 * mov * math.sin(math.radians(angle))
    
    #temporary variables storing values pertaining to the zoom function (at the time of writing this I forget what these do.)
    zoom_x, zoom_y = 1, 1
    
    for bot in all_world_objects['Bots']:
        if bot[3] > 0: bot[10] += 0.5

    for ind, container in all_world_objects.items():
        if ind == "Player":
            if container[4] > 1 or (container[4] == 1 and zoom > 1):
                container[4] += zoom
            zoom_x = -1 * container[4] * math.cos(math.radians(turret_angle))
            zoom_y = container[4] * math.sin(math.radians(turret_angle))
            container[0][0] = container[1][0] - zoom_x
            container[0][1] = container[1][1] - zoom_y
            #Original screen position will always be the original so no need to be changed.
            container[2][0] -= x_mov
            container[2][1] -= y_mov
            objects_to_render.append([2,
                                    [[screen, player_tank_hull, container[0], (player_width/2, player_height/2), angle, -4],
                                   [screen, player_tank_turret, container[0], (turret_width/2,turret_height/2), turret_angle, 0]
                                   ],
                                   'blitrotate'])
            shadows.append([container[0], ((21,10), (-22,10), (-22,-10), (21,-10)), angle])

            if player_health > 0:
                #d: mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                #d: mouse x - player x gets the distance between the mouse and player . vice versa for y 
                distance_x = mouse_x - container[0][0]
                distance_y = mouse_y - container[0][1]
                #d: atan2 finds the angle in radians. so this is finding the angle. 
                bullet_angle = math.atan2(distance_y, distance_x)
                ang = math.degrees(bullet_angle)
                turret_target_angle = -1 * (ang - 180)
                turret_dir = (((turret_target_angle - turret_angle) + 180) % 360 - 180)

                #does something
                if not abs(turret_dir) < turret_turn_speed:
                    if turret_dir < 0:
                        turret_angle -= turret_turn_speed
                    elif turret_dir > 0:
                        turret_angle += turret_turn_speed
                else:
                    turret_angle += turret_dir
                
                #turret barrel shadow
                length_sha = 35 #length of shadow
                
                cent = container[0][:]
                shifted_cent = (cent[0] + shift[0], cent[1] + shift[1])

                lenx = shifted_cent[0] + -1 * length_sha * math.cos(math.radians(turret_angle))
                leny = shifted_cent[1] + length_sha * math.sin(math.radians(turret_angle))

                objects_to_render.append([3, [screen, (0,0,0, darkness), shifted_cent, (lenx, leny), 2], "line_shadow"])

                #fire a ronud
                if mouseclick[0] == True and reload == 0 and ammunition_options[current_ammo].amount > 0:

                    ammunition_options[current_ammo].amount -= 1
                    reload += reload_time 
                    #+ (reload_fatigue // 50)
                    #reload_fatigue = reload_fatigue + 1000

                    widtht = bullet_width

                    posp = pygame.math.Vector2(container[0])
                    center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    
                    dist = pygame.math.Vector2(posp).distance_to(center)

                    distance = center - posp

                    speedtt = distance.normalize() * ammunition_options[current_ammo].velocity
                    
                    #class Gif: def __init__(self, screen_pos, screen_pos_org, world_pos, angle, offset, frames_per_frame):
                    
                    # need to create a copy of posp or else it will be affected along with the original posp. (fustrating problem) hence [:]
                    all_world_objects["Projectiles"].append([container[0][:], container[1][:], container[2], speedtt, widtht, [], True, ammunition_options[current_ammo].penetration, turret_angle, ammunition_options[current_ammo].damage,  ammunition_options[current_ammo].velocity])
                    
                    all_world_objects["Muzzleflash"].append(Gif(container[0][:], container[1][:], container[2], turret_angle, -100, 1))

                    all_world_objects['Sounds'].append([container[0][:], container[1][:], container[2][:], soundpacks["m256shot"], 0, False, 1])
        elif ind == 'Projectiles':
            for projectile in all_world_objects["Projectiles"]:
                if projectile[6]: #if it exists.
                    projectile_filler = []
                    for i in range(projectile[10]):
                        ratio = ((i + 1) / projectile[10])
                        new_speed = projectile[0] + (projectile[3] * ratio)
                        new_speed_org = projectile[1] + (projectile[3] * ratio)
                        new_speed_world = projectile[2] + (projectile[3] * ratio)
                        #objects_to_render.append([1, (screen, (255,255,255), new_speed, new_speed), "line"])
                        projectile_filler.append([new_speed, new_speed_org, new_speed_world])#pygame.Rect(new_speed[0], new_speed[1], projectile[4], projectile[4]))
                
                
                    projectile[0][0] = projectile[1][0] - zoom_x #accounting for zoom changes.
                    projectile[0][1] = projectile[1][1] - zoom_y

                    projectile[0][0] += x_mov #accounting for player movement changes. The bullet's visual position on both the actual and zoomed screen should change, but not the world, because the tank moving doesnt affect its actual position.
                    projectile[0][1] += y_mov
                    projectile[1][0] += x_mov
                    projectile[1][1] += y_mov

                    projectile[0] += projectile[3] #accounting for bullet movement changes. The projectile's position on the screen, the original screen, and the world changes.
                    projectile[1] += projectile[3]
                    projectile[2] += projectile[3]

                    projectile[5] = projectile_filler

                    for target in all_world_objects["Bots"]:
                        if not projectile[6]:
                            break
                            """
                            if all subprojectiles in every projectile were to evaluate every potential target in the game,
                            it would extremely quickly start to severly lag the game. My solution is to limit this evalutation;
                            the subprojectile evaluation only occours if the current potential target is near that bullet.
                            The target is determined as "near" if it is closer than the bullet's velocity (or if it is within
                            the bullet's possible position by the next frame)
                            """
                        if pygame.math.Vector2(projectile[1]).distance_to(target[1]) < projectile[10]:
                            #objects_to_render.append([1, (screen, (0,0,255), projectile[0], projectile.velocity, 50), "circle"])
                            for subprojectile in projectile_filler:
                                if not projectile[6]:
                                    break
                                #blitRotate(screen, all_world_objects["Bots"][0][4], (all_world_objects["Bots"][0][0]), (bot_width/2, bot_height/2), 35, -4)
                                
                                hit_message = ""
                                rot_hb = []
                                #f, b, r, l
                                for i in range(4):
                                    rot_hb.append(blitRotate(target[7][i][0], target[7][i][1], target[7][i][2], target[7][i][3], target[7][i][4], target[7][i][5], "rot"))

                                for j, rot_hitbox in enumerate(rot_hb):
                                    if pygame.math.Vector2(subprojectile[0]).distance_to(target[0]) < 100:
                                        #if j < 2 and pygame.math.Vector2(subprojectile[0]).distance_to(target[7][j][2]) < bot_hb_dis_fb:
                                        image_mask = pygame.mask.from_surface(rot_hitbox[0])
                                        image_rect = rot_hitbox[1]

                                        if image_rect.collidepoint(subprojectile[0]):
                                            mask_x = subprojectile[0][0] - image_rect.left
                                            mask_y = subprojectile[0][1] - image_rect.top
                                            if image_mask.get_at((mask_x, mask_y)):

                                                #objects_to_render.append([1, (screen, (0,0,255), subprojectile[0], 5, 3), "circle"])

                                                projectile[6] = False
                                                if j == 0:
                                                    hit_message = hit_message + "Side: Front, "
                                                elif j == 1:
                                                    hit_message = hit_message + "Side: Back, "
                                                elif j == 2:
                                                    hit_message = hit_message + "Side: Right, "
                                                elif j == 3:
                                                    hit_message = hit_message + "Side: Left, "
                                                
                                                actual_projectile_angle = 360 - projectile[8] if projectile[8] >= 360 else projectile[8]

                                                incoming_angle = actual_projectile_angle - 180 if actual_projectile_angle >= 180 else actual_projectile_angle + 180 if actual_projectile_angle < 180 else actual_projectile_angle

                                                
                                                all_world_objects["Explosions"].append(Gif(subprojectile[0], subprojectile[1], subprojectile[2], incoming_angle, 0, 2))
                                                #all_world_objects["Explosions"].append([subprojectile[0], subprojectile[1], subprojectile[2], 0, 1, incoming_angle])
                                                
                                                hit_message = hit_message + f'incoming angle: {incoming_angle} -> {target[10]} = {math.sin(math.radians(abs(incoming_angle - target[10])))}'
                                                log.append([hit_message, 400])
                                                if j <= 1:
                                                    angle_percent = math.sin(math.radians(abs(incoming_angle - target[10])))
                                                    log.append([str(angle_percent), 400])
                                                    if abs(angle_percent) <= 0.90:
                                                        actual_pen = target[8][j] + abs(target[8][j] * angle_percent)
                                                        if projectile[7] > actual_pen:
                                                            target[3] -= projectile[9]
                                                            log.append([f'Penetrated, {projectile[7]} > {actual_pen}', 400])
                                                        else:
                                                            log.append([f'Non-penetration, {projectile[7]} < {actual_pen}', 400])
                                                    else:
                                                        off = 0 #target[10]
                                                        #all_world_objects['ImpRico'].append(Gif_Rico_Impact(target[0], off, 50, 4))
                                                        log.append([f"Non-penetration, shell ricochet, angle: {angle_percent}", 400])
                                                else:
                                                    angle_of_side = 90 + target[10]
                                                    angle_of_side = 360 - angle_of_side if angle_of_side < 0 else angle_of_side
                                                    angle_percent = math.sin(math.radians(abs(incoming_angle - angle_of_side)))
                                                    log.append([str(angle_percent), 400])
                                                    if abs(angle_percent) <= 0.90:
                                                        actual_pen = target[8][j] + abs(target[8][j] * angle_percent)
                                                        if projectile[7] > actual_pen:
                                                            target[3] -= projectile[9]
                                                            log.append([f'Penetrated, {projectile[7]} > {actual_pen}', 400])
                                                        else:
                                                            log.append([f'Non-penetration, {projectile[7]} < {actual_pen}', 400])
                                                    else:
                                                        off = 0 #target[10] - (90 if j == 2 else -90) 
                                                        #all_world_objects['ImpRico'].append(Gif_Rico_Impact(target[0], off, -24 if j == 2 else -26, 4))
                                                        log.append([f"Non-penetration, shell ricochet, angle: {angle_percent}", 400])
                                                break
                                    '''
                                    old code
                                    rot_hull = blitRotate(screen, target[4], (target[0]), (bot_width/2, bot_height/2), target[10], -4, "rot")

                                    image_mask = pygame.mask.from_surface(rot_hull[0])
                                    image_rect = rot_hull[1]

                                    if image_rect.collidepoint(subprojectile[0]):
                                        mask_x = subprojectile[0][0] - image_rect.left
                                        mask_y = subprojectile[0][1] - image_rect.top
                                        if image_mask.get_at((mask_x, mask_y)):
                                            print("Hit")
                                            #objects_to_render.append([1, (screen, (0,0,255), subprojectile[0], 5, 3), "circle"])
                                            all_world_objects["Explosions"].append([subprojectile[0], subprojectile[1], subprojectile[2], 0, 2])
                                            projectile[6] = False
                                    '''
                        else:
                            projectile_end = projectile[10] / 500
                            projectile_endpoint = projectile[0] - (projectile[3] * projectile_end)
                            #projecile detection hitbox
                            #objects_to_render.append([1, (screen, (0,0,255), projectile[0], projectile.velocity * 0.75, 5), "circle"])
                            objects_to_render.append([3, (screen, (255,255,255), projectile_endpoint, projectile[0]), "line"])
        elif ind == "Objects":
            for object in container:
                #player_object_movement(object, x_mov, y_mov, zoom_x, zoom_y)
                obj_mod_x, obj_mod_y = object.screen_pos[0] - zoom_x, object.screen_pos[1] - zoom_y
                #modify world position?
                object.screen_pos = list(map(lambda i, j: i + j, object.screen_pos, (x_mov, y_mov)))
                #object.screen_pos[0] += x_mov
                #object.screen_pos[1] += y_mov 
                objects_to_render.append([10, (object.image, (obj_mod_x,obj_mod_y)), 'blit'])
        elif ind == 'Bots':
            for object in container:
                object[0][0] = object[1][0] - zoom_x
                object[0][1] = object[1][1] - zoom_y
                object[0][0] += x_mov
                object[0][1] += y_mov
                object[1][0] += x_mov
                object[1][1] += y_mov
                objects_to_render.append([5,
                                        [[screen, object[4], (object[0][0], object[0][1]), (bot_width/2, bot_height/2), object[10], -4],
                                       [screen, object[5], (object[0][0], object[0][1]), (bot_turret_width/2, bot_turret_height/2), object[10] + 10, 0] #45 tur angle
                                       ],
                                       'blitrotate'])
                shadows.append([object[0], ((26,11), (-15,11), (-15,-11), (26,-11)), object[10]])
                
                #turret barrel shadow
                length_sha = 30
                
                cent = object[0][:]
                shifted_cent = (cent[0] + shift[0], cent[1] + shift[1])

                lenx = shifted_cent[0] + -1 * length_sha * math.cos(math.radians(object[10]))
                leny = shifted_cent[1] + length_sha * math.sin(math.radians(object[10]))

                objects_to_render.append([9, [screen, (0,0,0, darkness), shifted_cent, (lenx, leny), 2], "line_shadow"])
                
                # --- hitboxes
                bot_rotpoint_right = rotPoint(object[0], 17,1, object[10])
                bot_rotpoint_left = rotPoint(object[0], 17, 19, object[10])
                
                bot_f_hb = [screen, bot_hitbox_fb, object[0], (bot_width / 2, hfb_height / 2), object[10], 17]
                bot_b_hb = [screen, bot_hitbox_fb, object[0], (bot_width / 2, hfb_height / 2), object[10], 56]
                bot_r_hb = [screen, bot_hitbox_rl, bot_rotpoint_right, (bot_width / 2, hfb_height / 2), object[10], 0]
                bot_l_hb = [screen, bot_hitbox_rl, bot_rotpoint_left, (bot_width / 2, hfb_height / 2), object[10], 0]
                """
                physical representations of the hitboxes
                objects_to_render.append([4, [bot_f_hb], 'blitrotate'])
                objects_to_render.append([4, [bot_b_hb], 'blitrotate'])
                objects_to_render.append([4, [bot_r_hb], 'blitrotate'])
                objects_to_render.append([4, [bot_l_hb], 'blitrotate'])
                """
                object[7] = [bot_f_hb, bot_b_hb, bot_r_hb, bot_l_hb]
                # ---
                objects_to_render.append([0, [f'{object[9]} HP: {object[3]}', 1, (0,0,0), (object[0][0] - 60, object[0][1] - 40)], "text"])

        elif ind == "Muzzleflash":
            for object in container:
                object.update_position(x_mov, y_mov, zoom_x, zoom_y)
                #player_object_movement(object, x_mov, y_mov, zoom_x, zoom_y)
                play_gif(objects_to_render, "Muzzleflash", screen, 'muzzle120_frames', object, 8, (player_width/2, player_height/2), 3)
        elif ind == "Explosions":
            for object in container:
                object.update_position(x_mov, y_mov, zoom_x, zoom_y)             
                #player_object_movement(object, x_mov, y_mov, zoom_x, zoom_y)
                play_gif(objects_to_render, "Explosions", screen, 'armor_impact_frames', object, 11, (15,15), 4)
        elif ind == "ImpRico":
            for object in container:
                #want to out the explosion code into down here

                #object.screen_pos[0] += x_mov
                #object.screen_pos[1] += y_mov
                #ox = object.screen_pos[0] - zoom_x
                #oy = object.screen_pos[1] - zoom_y 
                obj_mod_x, obj_mod_y = object.screen_pos[0] - zoom_x, object.screen_pos[1] - zoom_y
                object.screen_pos = list(map(lambda i, j: i + j, object.screen_pos, (x_mov, y_mov)))
                
                objects_to_render.append([4, [[screen, ricochet_impact_frames[math.floor(object.current_frame)], (obj_mod_x, obj_mod_y), (15,15), 0,0]], 'blitrotate'])
                if object.current_frame < 7:
                    object.current_frame += 1 / object.frames_per_frame
                else:
                    all_world_objects["ImpRico"].pop(0)
        elif ind == "Sounds":
            #[name, traveled, exist]
            SPEED_OF_SOUND = 50
            SOUND_RANGE = 30000
            for sound in container:
                sound[0][0] = sound[1][0] - zoom_x
                sound[0][1] = sound[1][1] - zoom_y
                sound[0][0] += x_mov
                sound[0][1] += y_mov
                sound[1][0] += x_mov
                sound[1][1] += y_mov
                #circle for sound visualization
                #objects_to_render.append([4, [screen, (0,0,255), sound[0], sound[4], 2], "circle"])
                if pygame.math.Vector2((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)).distance_to(sound[0]) < sound[4]:
                    screen_dist = pygame.math.Vector2((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)).distance_to(sound[0])
                    sound_name = False
                    for sound_pair in sound[3]:
                        if sound_pair[0] == 0:
                            sound_name = sound_pair[1]
                        elif screen_dist <= sound_pair[0]:
                            sound_name = sound_pair[1]
                            break
                    if sound_name:
                        current_channel = pygame.mixer.find_channel()
                        if current_channel:
                            current_sound = pygame.mixer.Sound(sound_name)

                            volume = sound[6] - (sound[4] / SOUND_RANGE)
                            if volume < 0: volume = 0 

                            current_sound.set_volume(volume)
                            current_channel.play(current_sound)

                        sound[5] = True
                else:
                    sound[4] += SPEED_OF_SOUND
            #uses list comprehension to remove all played sounds from the sounds list.
            all_world_objects["Sounds"] = [s for s in container if not s[5]]


    for shadow in shadows:
        #[center, rect_points]
        rect_center = shadow[0]

        top_left = rotPoint(rect_center, shadow[1][0][0], shadow[1][0][1], shadow[2])
        top_right = rotPoint(rect_center, shadow[1][1][0], shadow[1][1][1], shadow[2])
        bottom_right = rotPoint(rect_center, shadow[1][2][0], shadow[1][2][1], shadow[2])
        bottom_left = rotPoint(rect_center, shadow[1][3][0], shadow[1][3][1], shadow[2])

        p1 = (top_left[0] + shift[0], top_left[1] + shift[1])
        p2 = (bottom_left[0] + shift[0], bottom_left[1] + shift[1])
        p3 = (bottom_right[0] + shift[0], bottom_right[1] + shift[1])
        p4 = (top_right[0] + shift[0], top_right[1] + shift[1])
        objects_to_render.append([9, (screen, (0,0,0, darkness), (p1, p2, p3, p4)), "polygon_shadow"])
        #pygame.draw.polygon(screen, (0,0,0), (p1, p2, p3, p4))

    """
    make list to blit. We dont want to blit everything in order of where it is in the dictionary,
    , so instead we should append to a list that blits everything in the order that we want it to and then
    have a for loop iterate through the function to blit things in order. For example, a tree would not 
    necesarily blit befoere the tank itself, becaus the leaves can go over the tank. Yet, the backround is
    in the same objects list as the tree, so this would be a problem.
     [blit_order, object, blit_type (array with)]
    """
    objects_to_render = sorted(objects_to_render, key = lambda i: i[0], reverse=True)
    for object in objects_to_render:
        if object[2] == 'blitrotate':
            for blitrot in object[1]:
                blitRotate(blitrot[0], blitrot[1], blitrot[2], blitrot[3], blitrot[4], blitrot[5])
        elif object[2] == 'blit':
            screen.blit(object[1][0],object[1][1])
        elif object[2] == 'line':
            pygame.draw.line(object[1][0], object[1][1], object[1][2], object[1][3])
        elif object[2] == "rect":
            pygame.draw.rect(object[1][0], object[1][1], object[1][2])
        elif object[2] == "circle":
            pygame.draw.circle(object[1][0], object[1][1], object[1][2], object[1][3], object[1][4])
        elif object[2] == "polygon":
            pygame.draw.polygon(object[1][0], object[1][1], object[1][2])
        elif object[2] == "line_shadow":
            sur = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(sur, object[1][1], object[1][2], object[1][3], object[1][4])
            screen.blit(sur, (0,0))
        elif object[2] == "polygon_shadow":
            sur = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(sur, object[1][1], object[1][2])
            screen.blit(sur, (0,0))
        elif object[2] == "text":
            #[word, ?, color, pos]
            screen.blit(myfont.render(object[1][0], object[1][1], object[1][2]), object[1][3])

    mouse_x, mouse_y = pygame.mouse.get_pos()
    reticle_width = 20
    reticle_thick = 1
    RETICLE_COLOR = (0,250,0) #(0,200,1) 
    pygame.draw.circle(screen, RETICLE_COLOR, (mouse_x, mouse_y), reticle_width/2, reticle_thick)
    pygame.draw.circle(screen, RETICLE_COLOR, (mouse_x, mouse_y), 1)
    if target_on: pygame.draw.line(screen, RETICLE_COLOR, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), (mouse_x, mouse_y), reticle_thick)

    dist_from_tank = pygame.math.Vector2((all_world_objects['Player'][0])).distance_to((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    if dist_from_tank > 25:
        pygame.draw.rect(screen, RETICLE_COLOR, pygame.Rect(SCREEN_WIDTH / 2 - (reticle_width/2), SCREEN_HEIGHT / 2 - (reticle_width/2),reticle_width, reticle_width),reticle_thick)
        pygame.draw.circle(screen, RETICLE_COLOR, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 1)

        pygame.draw.rect(screen, RETICLE_COLOR, (575, 425, 10, 10), 2)
        modded_dist = int(round(dist_from_tank / 10, 0))
        dis_text = myfont.render(str(modded_dist), 20, RETICLE_COLOR)
        dis_pos = (600, 425)
        screen.blit(dis_text, dis_pos)

        if target_on: pygame.draw.line(screen, RETICLE_COLOR, (all_world_objects['Player'][0]), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), reticle_thick)

    
    GUI_AMMO_BACKGROUND_SURFACE = pygame.Surface((200, 200), pygame.SRCALPHA)
    pygame.draw.rect(GUI_AMMO_BACKGROUND_SURFACE, (50,50,50,128), (0,0, 200, 100))
    screen.blit(GUI_AMMO_BACKGROUND_SURFACE, (0,0))

    gui_ammo_shift = 0
    GUI_AMMO_POS_X, GUI_AMMO_POS_Y = 10, 15
    GUI_TEXT_COLOR_1 = (210,210,210)
    GUI_TEXT_COLOR_MAIN = (255,255,255)
    for name, ammunition in ammunition_options.items():
        ammunition_text = myfont.render(f'{ammunition.type} {name}: {ammunition.amount}', 20, GUI_TEXT_COLOR_MAIN if name == current_ammo else GUI_TEXT_COLOR_1)
        ammunition_pos = [GUI_AMMO_POS_X * 3 if name == current_ammo else GUI_AMMO_POS_X ,GUI_AMMO_POS_Y + 30 * gui_ammo_shift]
        screen.blit(ammunition_text, ammunition_pos)
        gui_ammo_shift += 1


    total_ammo = 0
    for ammo_option in ammunition_options.values():
        total_ammo += ammo_option.amount

    if ammunition_options[current_ammo].amount == 0 and total_ammo != 0:
        current_ammo_index = current_ammo_index + 1 if current_ammo_index < len(ammunition_options_list) - 1 else 0
        current_ammo = ammunition_options_list[current_ammo_index]
        reload = reload_time
            
    if reload != 0:
        if ammunition_options[current_ammo].amount > 0:
            reload = reload - 1
        else:
            reload = reload_time
    #elif reload_fatigue != 0:
    #    reload_fatigue = reload_fatigue - 1
        
    reload_percentage = reload_time/(reload_time - reload) if reload_time != reload else reload_time
    pygame.draw.rect(screen, (0,150,0), pygame.Rect(0, 100, 200/reload_percentage, 10))
    pygame.draw.rect(screen, (150,0,0,128), pygame.Rect(200/reload_percentage, 100, 200*reload/reload_time, 10))


    stop = timeit.default_timer()

    #d: in-screendow log array.log_stack is a variable that increases with every log addition and makes the log "stack" up with mulitple entires (no overlap)
    log_stack = 0
    #d: iterates through every event in the log and prints it, both in-game and in the terminal.
    for event in log:
        #d: if event[1], which is the frames remaining before it dissapears, is still it's original amount, print the event. in other words when it first
        #d: gets added to the log. if this if statement wasn't here, then it would repeatedly spam the terminal with the same log entry every frame. 
        if event[1] == log_buffer:
            print(event[0])
        #d: print the event to the screen.
        event_surf = myfont.render(event[0], 1, (0,0,0))
        screen.blit(event_surf, (800,680 - log_stack))
        event[1] -= 1
        log_stack += 20
        if event[1] == 0:
            log.pop(0)

    """
    fps counter 
    if time_check (the time during the previous frame) is not equal to the current time, then a second has just passed and its time to update the FPS. 
    This if statement makes fps (what is shown on the screen) equal to the total frames counted during one second, and then resets that value, fps_record, to 0.
    Every frame, 1 is added to fps_record. This happens independently from the game clock, so if the game
    lags and only does 30 frames for a second, then thats what will be printed to the screen.
    variable time_check is equal to the elapsed time in seconds at the end of this frame
    """
    if int(stop-start) != time_check:
        fps = fps_record
        fps_record = 0 
    fps_record += 1 
    fps_surf = myfont.render("FPS: " + str(fps), 1, (0,0,0))
    fps_pos = [15,675]
    screen.blit(fps_surf, fps_pos)
    time_check = int(stop-start)

    clock.tick(MAX_FPS)
    pygame.display.update()
pygame.quit()

