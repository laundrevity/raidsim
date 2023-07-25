# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 18:07:41 2018

@author: conor
"""

from classes import Battle


done = False
difficulty = None
while not done:
    if not difficulty:
        battle = Battle()
        battle.initialize()
        battle.run()
        difficulty = battle.difficulty
        
    else:
        valid_response = False
        while not valid_response:
            input_string = input('Continue? [y/n] ')
            valid_response = (input_string in ['y','n'])
        
        if input_string == 'y':
            difficulty += 100
            print('Commencing battle with boss HP = %d' % difficulty)
        else:
            done = True
            print('Until next time')
        
        if not done:
            battle = Battle(difficulty)
            battle.initialize()
            battle.run()