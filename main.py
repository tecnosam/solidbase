from structures.controller import *

tester = Controller( "monkey", '6BB' )

block = ControllerBlock( "test.txt", FILE_CONTROLLER, 0, 0, 2 )

tester.push_control( block )

block_2 = tester.free_space()[0]

block_2.name = "test2.txt"

tester.push_control( block_2 )