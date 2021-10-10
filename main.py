from structures.controller import *

tester = Controller( "monkey", '6MB' )

block = ControllerBlock( "numbers.txt", FILE_CONTROLLER, 0, 0, 2 )

tester.push_control( block, "test.txt" )

block_2 = tester.free_space()[0]

block_2.name = "test2.txt"

tester.push_control( block_2, "test2.txt" )