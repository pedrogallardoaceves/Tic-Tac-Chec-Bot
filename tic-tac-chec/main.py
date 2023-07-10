from round_robin import RoundRobin
from player_random import TTCPlayer
from player import _TTCPlayer



player1 =TTCPlayer("BOT")
player2 = _TTCPlayer("VIRGIN_DESTROYER")
#player3 = TTCPlayer("juan3")
#player4 = TTCPlayer("juan4")

if __name__ == '__main__':
    #tournament = RoundRobin([player1, player2], 20, 5, 70)
    tournament = RoundRobin([player1, player2],20, 5, 70)
    tournament.start()
    