#
# テスト用のプログラム
# 

import pygame
import sys

# 初期設定
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

DEAD_ZONE = 0.1

# プレイヤー設定
PLAYER_VEL = 10
player_size = 50
player_pos = [width // 2, height - 2 * player_size]
GRAVITY = 0.98
jump_speed = -30
vertical_vel = 0
ground = height - player_size
on_ground = True

# 最初に接続されているジョイスティックを選択
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()    
else:
    print('ゲームパッドが接続されていません')

# ゲームループ
running = True
stick_pos = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.JOYBUTTONDOWN:
            if on_ground and event.button == 0:
                vertical_vel = jump_speed
                on_ground = False
        elif event.type == pygame.JOYBUTTONUP:
            pass
        elif event.type == pygame.JOYAXISMOTION:
            # デッドゾーンの範囲内であれば何もしない
            if DEAD_ZONE > abs(event.value):
                stick_pos = 0
                continue
            
            if event.axis == 0:
                stick_pos = event.value * PLAYER_VEL
            if event.axis == 1:
                #player_pos[1] += event.value * PLAYER_VEL
                pass
    
    player_pos[0] += stick_pos
    
    # キー入力の取得
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= PLAYER_VEL
    if keys[pygame.K_RIGHT]:
        player_pos[0] += PLAYER_VEL
    
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # ジャンプ処理
    if on_ground and keys[pygame.K_SPACE]:
        vertical_vel = jump_speed
        on_ground = False

    # 重力処理
    player_pos[1] += vertical_vel
    vertical_vel += GRAVITY
    if player_pos[1] >= ground:
        player_pos[1] = ground
        vertical_vel = 0
        on_ground = True

    # 画面描画
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (player_pos[0], player_pos[1], player_size, player_size))

    pygame.display.flip()
    clock.tick(30)
