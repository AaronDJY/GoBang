import pygame
import sys
import random
from pygame.locals import *

class GoBang:
    def __init__(self, map_size=16):
        """
        # map_size * map_size reresent a chessboard
        # '# 0 : represent the empty
        # 1 : represent the black chess
        # -1 : represent the white chess
        """
        self.map_size = map_size
        self.map = [[0 for y in range(0, map_size)] for x in range(0, map_size)]
        # A historical record of each step,used for contrite chess.
        # It is a list whose members are a tuple (chess piece type, map.x, map.y)
        self.record_move = []

        self.current_status = 0
        self.winner = 0

    def start_move(self):
        """ 
        start to move
        no input
        change the current_status to 1 which means start game and it is for black player's term  
        """
        self.current_status = 1

    def get_last_move(self):
        """
        return the last step of move, which is a helper method for undo
        """
        return self.record_move[-1]

    def get_winner(self):
        """
        return the winner from this class's field
        """
        return self.winner

    def get_steps(self):
        """
        return the length of the record list, which means how many steps did the player move
        """
        return len(self.record_move)

    def check_win(self):
        """
        The algorithm to judge the winning and losing: it only needs to judge whether the four lines 
        related to the current spot (horizontal, vertical, left oblique, right oblique) form 5 links.

        Add all the drops on the line (black ~ 1, white ~ -1) in turn. 
        If the sum of the absolute values of the consecutive drops reaches 5, it can be judged as victory
        """
        temp = 0
        last_step = self.record_move[-1]

        #first case, there are five same chess on the vertical line
        #Check vertical line, x is fixed
        for y in range(0, self.map_size):
            # It should be continuous, if not, temp will be 0
            if y > 0 and self.map[last_step[1]][y] != self.map[last_step[1]][y - 1]:
                temp = 0
            temp += self.map[last_step[1]][y]
            if abs(temp) >= 5:
                return last_step[0]

        # second case, there are five same chess on the horizontal line
        # check the Horizontal line, y is fixed
        temp = 0
        for x in range(0, self.map_size):
            if x > 0 and self.map[x][last_step[2]] != self.map[x - 1][last_step[2]]:
                temp = 0
            temp += self.map[x][last_step[2]]
            if abs(temp) >= 5:
                return last_step[0]

        # Right oblique line, calculate the coordinates of the upper left vertex. And then both x and y increase to the bottom right corner.
        temp = 0
        min_dist = min(last_step[1], last_step[2])
        top_point = [last_step[1] - min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            # it cannot go out of boundary
            if top_point[0] + incr > self.map_size - 1 or top_point[1] + incr > self.map_size - 1:
                break
            if incr > 0 and self.map[top_point[0] + incr][top_point[1] + incr] \
                != self.map[top_point[0] + incr - 1][top_point[1] + incr - 1]:
                temp = 0
            temp += self.map[top_point[0] + incr][top_point[1] + incr]
            if abs(temp) >= 5:
                return last_step[0]

        # Left oblique line, calculate the coordinates of the upper right vertex. Then x decreases and y increases, reaching the bottom-left vertex.
        temp = 0
        min_dist = min(self.map_size - 1 - last_step[1], last_step[2])
        top_point = [last_step[1] + min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            if top_point[0] - incr < 0  or top_point[1] + incr > self.map_size - 1:
                break
            if incr > 0 and self.map[top_point[0] - incr][top_point[1] + incr] \
                    != self.map[top_point[0] - incr + 1][top_point[1] + incr - 1]:
                temp = 0
            temp += self.map[top_point[0] - incr][top_point[1] + incr]
            if abs(temp) >= 5:
                return last_step[0]

        return 0

    
    def if_gameover(self):
        """
        Determine whether this bureau is over
        return code C if all the steps is complete
        return code code_win if one player win
        return code code_run to countinue
        """
        if len(self.record_move) >= self.map_size ** 2:
            return Errorcode().code_over
        winner = self.check_win()
        if winner != 0:
            self.winner = winner
            return Errorcode().code_win

        return Errorcode().code_run

    
    def move(self, x, y):
        """
        input the cordinate of the chess
        and record it in the map with white and black color
        and determine if game is over, and return the code
        """
        if self.current_status != 1 and self.current_status != 2:
            return Errorcode().code_status_error
        if self.map_size <= x or x < 0 or self.map_size <= y or y < 0:
            return Errorcode().code_wrong_range
        if self.map[x][y] != 0:
            return Errorcode().code_pos

        t = 1 if self.current_status == 1 else -1
        self.map[x][y] = t
        self.record_move.append((t, x, y))

        # Determine whether it is over
        ret = self.if_gameover()
        if self.is_finish(ret):
            if ret == Errorcode().code_win:
                self.__set_current_status(3)
            else:
                self.__set_current_status(4)
            return ret

        # change the current_state after each step
        last_step = self.record_move[-1]
        current_stat = 2 if last_step[0] == 1 else 1
        self.__set_current_status(current_stat)
        return Errorcode().code_run

    def __set_current_status(self, current_stat):
        """
        input the currect status and change the field of this class to current status
        """
        self.current_status = current_stat

    def is_finish(self, err_code):
        """
        get the error code and return a boolean by the game stat
        """
        if err_code == Errorcode().code_error or err_code == Errorcode().code_win:
            return True
        return False

    def rollback(self):
        """
        this function is for rollback the laststep
        it will determine if there is exist steps, if not will return error code
        then the function will use pop method to delete the latest steps from the move records
        after remove will refresh the status of the game
        """
        if len(self.record_move) == 0:
            return Errorcode().code_error
        step = self.record_move.pop()
        self.map[step[1]][step[2]] = 0
        # refresh the current status
        if step[0] == 1:  
            # If the current one is Black, then the state switches to waiting for Black to move
            self.current_status = 1
        elif step[0] == -1:
            self.current_status = 2
        else:
            return Errorcode().code_error

        return Errorcode().code_run


    def get_current_status(self):
        """
        Get the current current_state
        0 ~ No opening
        1 ~ Wait for Black to move
        2 ~ Wait for White to move
        3 ~ End (one side wins)
        4 ~ End (the board is full)
        """
        return self.current_status

    def get_record_move(self):
        """
        return the record in this class
        """
        return self.record_move


class GameGoBang(GoBang):

    def __init__(self, map_size=16, map_unit=50):

        # The parent class is initialized
        super(GameGoBang, self).__init__(map_size=map_size)

        self.SIZE = map_size
        self.unit = map_unit
        self.TITLE = 'GoBang'
        self.panel_size = 285  # the width for the right panel
        self.width = 50  # Width reserved
        b1 = Background()
        self.picture = b1.random_picture()

        # Calculate the effective range of the checkerboard
        self.RANGE_X = [self.width, self.width + (self.SIZE - 1) * self.unit]
        self.RANGE_Y = [self.width, self.width + (self.SIZE - 1) * self.unit]

        # Calculate the valid range of the current_status panel
        self.PANEL_X = [self.width + (self.SIZE - 1) * self.unit,
                        self.width + (self.SIZE - 1) * self.unit + self.panel_size]
        self.PANEL_Y = [self.width, self.width + (self.SIZE - 1) * self.unit]

        # Calculating the window size
        self.WINDOW_WIDTH = self.width * 2  + self.panel_size + (self.SIZE - 1) * self.unit
        self.WINDOW_HEIGHT = self.width * 2  + (self.SIZE - 1) * self.unit


        # Initializing the Game
        self.game_window()

    # Draw chess board
    def chess_borad_draw(self):
        """
        this function is using to draw the chess board
        the chess board is drawing by the unit number of col and row with number
        """
        pos_start = [self.width, self.width]

        s_font = pygame.font.SysFont('arial', 16)
        # draw the row
        for item in range(0, self.SIZE):
            pygame.draw.line(self.screen, Color().BLACK,[pos_start[0], pos_start[1] + item * self.unit],
            [pos_start[0] + (self.SIZE - 1) * self.unit,pos_start[1] + item * self.unit], 1)
            s_surface = s_font.render(f'{item + 1}', True, Color().BLACK)
            self.screen.blit(s_surface, [pos_start[0] - 30, pos_start[1] + item * self.unit - 10])

        # draw the col
        for item in range(0, self.SIZE):
            pygame.draw.line(self.screen, Color().BLACK,[pos_start[0] + item * self.unit, pos_start[1]],
                             [pos_start[0] + item * self.unit, pos_start[1] + (self.SIZE - 1) * self.unit],1)
            s_surface = s_font.render(f'{item + 1}', True, Color().BLACK)
            self.screen.blit(s_surface, [pos_start[0] + item * self.unit - 5, pos_start[1] - 30])

    # Draw a chess
    def chess_draw(self):
        """
        this fucntion is using to draw the chess with the current chess pos
        the pygame is refresh in very fast speed and it will draw all the thing ceaseless
        so we need to iterate the list of chess to draw each of them
        the chess color will switch with it's parameter
        """
        chess_position = self.get_record_move()
        for item in chess_position:
            x = self.width + item[1] * self.unit
            y = self.width + item[2] * self.unit
            t_color = Color().BLACK if item[0] == 1 else Color().WHITE
            pygame.draw.circle(self.screen, t_color, [
                               x, y], int(self.unit / 2.5))

    # redraw all the window
    def __redraw_all(self):
        """
        reset all the display thing in this class
        draw the chess board and draw the background, panel
        """
        # refresh the background
        self.screen.blit(pygame.image.load(self.picture), (0, 0))
        # draw the chess board
        self.chess_borad_draw()
        # draw the chess
        self.chess_draw()
        # draw the panel
        self.panel_draw()

    def game_window(self):
        """
        this function is the initial of pygame
        it will set the window title and size
        it will get the picture of the picture class
        it will draw the chess board and right panel
        """
        # Initialize pygame
        pygame.init()
        # Sets the size of the window in pixels
        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        # Setting the Window Title
        pygame.display.set_caption(self.TITLE)
        # Setting the Background Color
        # self.screen.fill(WHITE)

        background = pygame.image.load(self.picture)
        self.screen.blit(background, (0, 0))

        # Loading sound files
        self.sound_black = pygame.mixer.Sound(Bgm("p1").get_voice())
        self.sound_white = pygame.mixer.Sound(Bgm("p2").get_voice())
        self.sound_win = pygame.mixer.Sound(Bgm("win").get_voice())
        self.sound_error = pygame.mixer.Sound(Bgm("error").get_voice())
        self.sound_start = pygame.mixer.Sound(Bgm("newgame").get_voice())

        # Draw a checkerboard
        self.chess_borad_draw()

        # Draw the current_status panel on the right
        self.panel_draw()

    def panel_draw(self):
        """
        This function is used to draw all the button and information of this game
        the function will read the current_status and show the current current_state in the right up corner
        There are 6 condition:
        'Wait to start'
        'wait for black player..
        'wait for white player..'
        'Game is over'
        'Black Player wins!'
        'White player wins!'

        dispaly the steps count 
        dispaly the exit, undo, refresh game button
        """
        # The panel area is redrawn and covered with a white rectangle
        pygame.draw.rect(self.screen, Color().WHITE,
                         [self.PANEL_X[0] + 30, 0,
                          1000, 1000])

        self.panel_font = pygame.font.SysFont('simhei', 20)

        # current_status of game
        current_stat = self.get_current_status()
        if current_stat == 0:
            current_stat_str = 'Wait to start'
        elif current_stat == 1:
            current_stat_str = 'wait for black player..'
        elif current_stat == 2:
            current_stat_str = 'wait for white player..'
        elif current_stat == 4:
            current_stat_str = 'Game is over'
        elif current_stat == 3:
            winner = self.get_winner()
            if winner == 1:
                current_stat_str = 'Black Player wins!'
            else:
                current_stat_str = 'White player wins!'
        else:
            current_stat_str = ''
        self.surface_current_stat = self.panel_font.render(current_stat_str, False, Color().BLACK)
        self.screen.blit(self.surface_current_stat, [
                         self.PANEL_X[0] + 50, self.PANEL_Y[0] + 50])

        # steps record
        steps = self.get_steps()
        self.surface_steps = self.panel_font.render(
            f'Steps: {steps}', False, Color().BLACK)
        self.screen.blit(self.surface_steps, [
                         self.PANEL_X[0] + 50, self.PANEL_Y[0] + 150])

        # refresh the game button
        offset_x = self.PANEL_X[0] + 50
        offset_y = self.PANEL_Y[0] + 400
        button_height = 50
        button_width = 150
        button_gap = 20
        button_text_x = 35
        button_text_y = 15
        self.new_x = [offset_x, offset_x + button_width]
        self.new_y = [offset_y, offset_y + button_height]
        pygame.draw.rect(self.screen, Color().BLACK,
                         [offset_x, offset_y,
                          button_width, button_height])
        self.button = self.panel_font.render(f'New Round', False, Color().WHITE)
        self.screen.blit(
            self.button, [offset_x + button_text_x, offset_y + button_text_y])

        # exit the game bhutton
        self.button_exit_x = [offset_x, offset_x + button_width]
        self.button_exit_y = [offset_y + button_height + button_gap,
                                      offset_y + button_height + button_gap + button_height]
        pygame.draw.rect(self.screen, Color().BLACK,
                         [offset_x, offset_y + button_height + button_gap,
                          button_width, button_height])
        self.button = self.panel_font.render(f'EXIT', False, Color().WHITE)
        self.screen.blit(self.button,
                         [offset_x + button_text_x, offset_y + button_height + button_gap + button_text_y])

        # undo
        self.button_undo_x = [offset_x, offset_x + button_width]
        self.button_undo_y = [offset_y + (button_height + button_gap) * 2,
                               offset_y + (button_height + button_gap) * 2 + button_height]
        pygame.draw.rect(self.screen, Color().BLACK,
                         [offset_x, offset_y + (button_height + button_gap) * 2,
                          button_width, button_height])
        self.button = self.panel_font.render(f'Undo', False, Color().WHITE)
        self.screen.blit(self.button,
                         [offset_x + button_text_x, offset_y + (button_height + button_gap) * 2 + button_text_y])

    def done_move(self, pos):
        """
        at first determine the position of player mouse, if it out of boundary will play the error sound and return the error code
        play differernt sound with two player term
        if the player mouse is in the boundary will search the nearest point, which will use round to help it get the correct position
        if the chess drop correctly will move it in the logic first than draw
        we will use black circle and white circle to represent the 

        """
        # The spot is invalid outside the board
        if pos[0] < self.RANGE_X[0] or pos[0] > self.RANGE_X[1] \
                or pos[1] < self.RANGE_Y[0] or pos[1] > self.RANGE_Y[1]:
            self.sound_error.play()
            return Errorcode().code_error

        # Play drop sound effects
        if self.get_current_status() == 1:
            self.sound_black.play()
        else:
            self.sound_white.play()
        # 
        s_x = round((pos[0] - self.width) / self.unit)
        s_y = round((pos[1] - self.width) / self.unit)
        x = self.width + self.unit * s_x
        y = self.width + self.unit * s_y
        
        ret = self.move(s_x, s_y)
        if ret < 0:
            self.sound_error.play()
            return Errorcode().code_error
        # draw
        last_move = self.get_last_move()
        #this if statement will return white and black by it's parameter
        t_color = Color().BLACK if last_move[0] == 1 else Color().WHITE
        pygame.draw.circle(self.screen, t_color, [x, y], int(self.unit / 2.5))

        self.panel_draw()
        if self.get_current_status() >= 3:
            self.sound_win.play()
        return Errorcode().code_run

    def undo_chess(self):
        """
        undo function of chessboard, if the programe is still run, we will do the 
        redraw all function
        """
        if self.rollback() == Errorcode().code_run:
            self.__redraw_all()

    def refresh_game(self):
        """
        start a new game will the refresh game sound, and do the start function
        """
        self.__init__()
        self.sound_start.play()
        self.start()

    def button_press(self, pos):
        """
        this function will get the position of the mouse and determine if the mouse in the range of the button
        we have three button and each button regarding to one function which is refreseh game,exit and undo
        """
        # determine if press the button
        if self.new_x[0] < pos[0] < self.new_x[1] and self.new_y[0] < pos[1] < self.new_y[1]:
            self.refresh_game()
            return code_run
        elif self.button_exit_x[0] < pos[0] < self.button_exit_x[1] and self.button_exit_y[0] < pos[1] < self.button_exit_y[1]:
            sys.exit()
        elif self.button_undo_x[0] < pos[0] < self.button_undo_x[1] and self.button_undo_y[0] < pos[1] < self.button_undo_y[1]:
            self.undo_chess()
            return Errorcode().code_run
        else:
            return Errorcode().code_error

    def start(self):
        """
        it is the main function of this programe
        run this fucntion will run the whole programe
        it will draw and dispaly the game
        """
        self.start_move()
        self.panel_draw()
        # main loop of the programe
        while True:
            # this is all the event in the game
            for event in pygame.event.get():
                # Check whether the event is an exit event
                if event.type == QUIT:
                    # exit pygame
                    pygame.quit()
                    # Exit the system
                    sys.exit()

                if event.type == MOUSEBUTTONUP:
                    if self.button_press(event.pos) < 0:
                        # Non-button events handle moves
                        self.done_move(event.pos)

            # update and display on the screen
            pygame.display.update()


class Button:

    def __init__(self,button_name, x, y) -> None:
        self.button =button_name
        self.pos_x = x
        self.pos_y = y
    
    def get_x(self):
        return  self.pos_x

    def get_y(self):
        return self.pos_y

class Errorcode:
    def __init__(self) -> None:
        self.code_pos = -4
        self.code_wrong_range = -3
        self.code_status_error = -2
        self.code_error = -1
        self.code_run = 0
        self.code_over = 1
        self.code_win = 2

class Color:
    def __init__(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (142, 218, 0)

class Background:
    def __init__(self) -> None:
        self.number = random.randint(1, 5)

    def random_picture(self):
        """
        return the different picture with random number
        """
        if self.number == 1:
            return "b1.jpg"
        elif self.number == 2:
            return "b2.jpg"
        elif self.number == 3:
            return "b3.jpg"
        elif self.number == 4:
            return "b4.jpg"
        elif self.number == 5:
            return "b5.jpg"


class Bgm:
    def __init__(self, voice_name) -> None:
        self.bgm = voice_name
    
    def get_voice(self):
        if self.bgm == "p1":
            return "p1.mp3"
        elif self.bgm == "p2":
            return "p2.mp3"
        elif self.bgm == "win":
            return "win.mp3"
        elif self.bgm == "error":
            return "error.mp3"
        else:
            return "newgame.mp3"


if __name__ == '__main__':
    inst1 = GameGoBang(map_unit=50)
    inst1.start()
