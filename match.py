#!/usr/bin/env python
from game.go import Board, opponent_color
from game.ui import UI
import pygame
import time
from agent.search.search_agent import AlphaBetaAgent
from os.path import join
from argparse import ArgumentParser
import sys

class Match:
    def __init__(self, agent_black=None, agent_white=None, gui=True, dir_save=None):
        #black moves first and from center as center is the most strategic point
        self.agent_black = agent_black
        self.agent_white = agent_white

        self.board = Board(next_color='BLACK') 

        gui = gui if agent_black and agent_white else True
        self.ui = UI() if gui else None
        self.dir_save = dir_save

        self.time_elapsed = None

    @property
    def winner(self):
        return self.board.winner

    @property
    def next(self):
        return self.board.next

    @property
    def counter_move(self):
        return self.board.counter_move

    def start(self):
        if self.ui:
            self._start_with_ui()
        else:
            self._start_without_ui()

    def end_game(self):
        if self.ui:
            self.ui.exit_game()

    def _start_with_ui(self):
        self.ui.initialize()
        self.time_elapsed = time.time()


        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)
        self.ui.draw(first_move, opponent_color(self.board.next))

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next == 'BLACK':
                point = self.perform_one_move(self.agent_black)
            else:
                point = self.perform_one_move(self.agent_white)

            # Check if action is legal
            if point not in self.board.legal_actions:
                continue

            # Apply action
            prev_legal_actions = self.board.legal_actions.copy()
            self.board.put_stone(point, check_legal=False)
            # Remove previous legal actions on board
            for action in prev_legal_actions:
                self.ui.remove(action)
            # Draw new point
            self.ui.draw(point, opponent_color(self.board.next))
            # Update new legal actions and any removed groups
            if self.board.winner:
                for group in self.board.removed_groups:
                    for point in group.points:
                        self.ui.remove(point)
                if self.board.end_by_no_legal_actions:
                    print('Game ends early (no legal action is available for %s)' % self.board.next)
            else:
                for action in self.board.legal_actions:
                    self.ui.draw(action, 'BLUE', 8)

        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            path_file = join(self.dir_save, 'go_' + str(time.time()) + '.jpg')
            self.ui.save_image(path_file)
            print('board image saved in file ' + path_file)


    def perform_one_move(self, agent):
        if agent:
            return self._move_by_agent(agent)
        else:
            return self._move_by_human()

    def _move_by_agent(self, agent):
        if self.ui:
            pygame.time.wait(100)
            pygame.event.get()
        return agent.get_action(self.board)

    def _move_by_human(self):
        while True:
            pygame.time.wait(100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.ui.outline.collidepoint(event.pos):
                        x = int(round(((event.pos[0] - 5) / 40.0), 0))
                        y = int(round(((event.pos[1] - 5) / 40.0), 0))
                        point = (x, y)
                        stone = self.board.exist_stone(point)
                        if not stone:
                            return point


def get_args():
    parser = ArgumentParser('Mini Go Game')
    parser.add_argument('-b', '--agent_black', default=None,
                        help='allowed agents: minimax or None (for human); DEFAULT is None')
    parser.add_argument('-w', '--agent_white', default=None,
                        help='allowed agents: minimax or None (for human); DEFAULT is None')
    parser.add_argument('-d', '--search_depth', type=int, default=1,
                        help='search depth for minimax agent; DEFAULT is 1')
    parser.add_argument('-g', '--gui', type=bool, default=True,
                        help='show GUI; always True if human plays; DEFAULT is True')
    parser.add_argument('-s', '--dir_save', default=None,
                        help='directory to save the board image; DEFAULT is None (no save)')
    return parser.parse_args()



def get_agent(str_agent, color, depth):
    if str_agent is None:
        return None
    str_agent = str_agent.lower()
    if str_agent == 'none':
        return None
    elif str_agent == 'minimax':
        return AlphaBetaAgent(color, depth=depth)
    else:
        raise ValueError('Invalid agent for ' + color)


def main():
    args = get_args()
    screen = pygame.display.set_mode((640,480))
    depth = args.search_depth
    agent_black = get_agent(args.agent_black, 'BLACK', depth)
    agent_white = get_agent(args.agent_white, 'WHITE', depth)
    gui = args.gui
    dir_save = args.dir_save

    print('Agent for BLACK: ' + (str(agent_black) if agent_black else 'Human'))
    print('Agent for WHITE: ' + (str(agent_white) if agent_white else 'Human'))
    if dir_save:
        print('Directory to save board image: ' + dir_save)

    match = Match(agent_black=agent_black, agent_white=agent_white, gui=gui, dir_save=dir_save)

    print('Match starts!')
    match.start()
    running =True

    #case for when useer exits in between the game 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running =False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    running=False
    print(match.winner + ' wins!')
    print('Match ends in ' + str(match.time_elapsed) + ' seconds')
    print('Match ends in ' + str(match.counter_move) + ' moves')
    match.end_game()
    sys.exit()





if __name__ == '__main__':
    main()
