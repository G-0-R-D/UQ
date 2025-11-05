# symlink to this file: # ln -s "this file" "path file"

# TODO make it possible to re-select graphics engine for a program (with program restart), including main one!

#from SnapEnv import SnapEnv, MAIN_PROGRAM


import os

from snap.SnapEnv import SnapEnv

ENV = SnapEnv(gui='QT5', engine='QT5') # TODO sys.argv will take precedence over these

ENV.__register_import_path__(os.path.dirname(os.path.realpath(__file__))) # 'UQ'

if __name__ == '__main__':

	# TODO init args, allow passing json descriptions to initialize a module?  or just use a recipe file?  json - save/load TODO

	ENV.__build__('UQ.app') # builds everything except UQApplication
	
	ENV.__run_gui__('UQ.app.UQApplication')


