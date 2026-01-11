import pygame,sys,random


def ball_animation():
    global ball_speed_x,ball_speed_y,opponent_score,player_score,score_time
    ball.x+=ball_speed_x
    ball.y+=ball_speed_y
    if ball.top<=0 or ball.bottom>=screen_height:
        ball_speed_y*=-1
    if ball.left<=0:
        player_score+=1
        score_time=pygame.time.get_ticks()
    if ball.right>=screen_width:
        opponent_score+=1
        score_time=pygame.time.get_ticks()
    if ball.colliderect(player) and ball_speed_x>0:
        if abs(ball.right-player.left)<10:
            ball_speed_x*=-1
        elif abs(ball.bottom-player.top)<10 and ball_speed_y>0:
            ball_speed_y*=1
        elif abs(ball.top-player.bottom)<10 and ball_speed_y<0:
            ball_speed_y*=1
    if ball.colliderect(opponent) and ball_speed_x<0:
        if abs(ball.left-opponent.right)<10:
            ball_speed_x*=-1
        elif abs(ball.bottom-opponent.top)<10 and ball_speed_y>0:
            ball_speed_y*=1
        elif abs(ball.top-opponent.bottom)<10 and ball_speed_y<0:
            ball_speed_y*=1

def player_animation():
    player.y+=player_speed
    if player.top<=0 :
        player.top=0
    if player.bottom>=screen_height:
        player.bottom=screen_height
def opponent_ai():
    global ball_speed_x,ball_speed_y
    if opponent.top<ball.y:
        opponent.top+=opponent_speed
    if opponent.bottom>ball.y:
        opponent.bottom-=opponent_speed
    if opponent.top<=0 :
        opponent.top=0
    if opponent.bottom>=screen_height:
        opponent.bottom=screen_height
def ball_start():
    global ball_speed_x,ball_speed_y,score_time
    
    current_time=pygame.time.get_ticks()
    ball.center=(screen_width/2,screen_height/2)
    if current_time-score_time<700:
        number_three=game_font.render('3',False,white)
        screen.blit(number_three,(screen_width/2-10,screen_height/2+20))
    if 700<current_time-score_time<1400:
        number_two=game_font.render('2',False,white)
        screen.blit(number_two,(screen_width/2-10,screen_height/2+20))
    if 1400<current_time-score_time<2100:
        number_one=game_font.render('1',False,white)
        screen.blit(number_one,(screen_width/2-10,screen_height/2+20))
    if current_time-score_time<2100:
        ball_speed_x,ball_speed_y=0,0
    else:
        ball_speed_x=7*random.choice((1,-1))
        ball_speed_y=7*random.choice((1,-1))
        score_time=None

pygame.init()
clock=pygame.time.Clock()
screen_width=790
screen_height=560
screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('PONG')
ball=pygame.Rect(screen_width/2-15,screen_height/2-15,30,30)
player=pygame.Rect(screen_width-20,screen_height/2-70,10,140)
opponent=pygame.Rect(10,screen_height/2-70,10,140)
blue=(78,231,254)
red=(255,3,62)
white=(255,255,255)
green=(124,184,17)
orange=(242, 140, 40)
ball_speed_x=7*random.choice((1,-1))
ball_speed_y=7*random.choice((1,-1))
player_speed=0
opponent_speed=10
player_score=0
opponent_score=0
game_font=pygame.font.Font(None,32)
score_time=True
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_UP:
                player_speed-=7
            if event.key==pygame.K_DOWN:
                player_speed+=7
        if event.type==pygame.KEYUP:
            if event.key==pygame.K_UP:
                player_speed+=7
            if event.key==pygame.K_DOWN:
                player_speed-=7
    ball_animation()
    player_animation()
    opponent_ai()
    screen.fill(green)
    pygame.draw.rect(screen,blue,player)
    pygame.draw.rect(screen,red,opponent)
    pygame.draw.line(screen,orange,(screen_width/2,0),(screen_width/2,screen_height),8)
    pygame.draw.ellipse(screen,white,ball)
    if score_time:
        ball_start()
    player_text=game_font.render(f'{player_score}',False,blue)
    screen.blit(player_text,(420,10))
    opponent_text=game_font.render(f'{opponent_score}',False,red)
    screen.blit(opponent_text,(360,10))
    pygame.display.flip()
    clock.tick(60)
    
