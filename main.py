from structures.controller import *

# tester = Controller.load_file( "sam-solidbase/.controller.json" )

tester = Controller( "sam", '1MB' )

block = ControllerBlock( "numbers123", FILE_CONTROLLER, parent = 0, start = 0,end = 2 )

tester.push_control( block, "./test-files/test.txt" )

block_2 =  tester.free_space(  )[0]

img_url="https://www.gravatar.com/avatar/7adfa37e16d44badfc22e2b1d9a78bca?s=256&d=identicon&r=PG"
tester.push_control( block_2, img_url )
