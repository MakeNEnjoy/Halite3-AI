#!/usr/bin/env python3
# Python 3.6

from math import factorial

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info(
	"Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

going = {}

while True:
	# This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
	#   running update_frame().
	game.update_frame()
	# You extract player metadata and the updated map metadata here for convenience.
	me = game.me
	game_map = game.game_map

	# A command queue holds all the commands you will run this turn. You build this list up and submit it at the
	#   end of the turn.
	command_queue = []

	for ship in me.get_ships():

		high_halite = [0, 0]

		for x in range(game_map.width):
			for y in range(game_map.height):
				if(game_map[Position(x, y)].halite_amount / 4 ** (game_map.calculate_distance(ship.position, Position(x, y))) >
				game_map[Position(*high_halite)].halite_amount / 4 ** (game_map.calculate_distance(ship.position, Position(*high_halite)))
				and len(me.get_ships()) * 0.5 < game_map.calculate_distance(me.shipyard.position, Position(x, y))):
					high_halite = [x, y]

		# For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
		#   Else, collect halite.
		if random.random() < 0.1:
			command_queue.append(
				ship.move(
					game_map.naive_navigate(
						ship,
						random.choice(ship.position.get_surrounding_cardinals())
					))
				)
		else:
			logging.info(
				"Ship Id: {} Distance to yard: {} going: {} cardinals: {}".format(
					ship.id,
					game_map.calculate_distance(ship.position, me.shipyard.position),
					going.get(ship.id, 'Not Found'),
					ship.position.get_surrounding_cardinals()
				)

			)

			if ship.halite_amount == 1000 or going.get(ship.id, False) and game_map.calculate_distance(ship.position, me.shipyard.position) != 0:
				going[ship.id] = True
				command_queue.append(ship.move(
                    game_map.naive_navigate(ship, me.shipyard.position)))
			elif game_map.calculate_distance(ship.position, me.shipyard.position) == 0:
				going[ship.id] = False

				cardinals = []
				for cardinal in ship.position.get_surrounding_cardinals():
					if(game_map[cardinal].is_empty):
						cardinals.append(cardinal)				

				if not cardinals:
					command_queue.append(
						ship.move(random.choice([Direction.North, Direction.South, Direction.East, Direction.West])))
				else:
					command_queue.append(
						ship.move(
							game_map.naive_navigate(
								ship,
								random.choice(cardinals)
							))
						)
			else:
				command_queue.append(
					ship.move(
						game_map.naive_navigate(
							ship, Position(*high_halite))))

	if game.turn_number <= constants.MAX_TURNS * 0.625 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
		command_queue.append(me.shipyard.spawn())

	# Send your moves back to the game environment, ending this turn.
	game.end_turn(command_queue)
