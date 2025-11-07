# symlink to this file: # ln -s "this file" "path file"

import os

from snap.SnapEnv import SnapEnv

class UQEnv(SnapEnv):

	def __init__(self, *a, **k):
		SnapEnv.__init__(self, *a, **k)

		self.__register_import_path__(os.path.dirname(os.path.realpath(__file__))) # 'UQ'

		self.__build__('UQ.app') # builds everything except UQApplication

def main(ENV):

	ENV.__run_gui__('UQ.app.UQApplication')

if __name__ == '__main__':

	main(UQEnv(gui='QT5', engine='QT5')) # TODO sys.argv will take precedence over these)




