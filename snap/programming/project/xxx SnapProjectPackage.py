
import os

def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapProjectPackage(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class rootpath:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['rootpath']

			def set(self, MSG):
				"(str!)"
				rootpath = MSG.args[0]
				if rootpath is None:
					self.close()

				elif isinstance(rootpath, str):
					rootpath = os.path.realpath(rootpath)
					assert os.path.exists(rootpath), 'not a valid sys path: {}'.format(rootpath)
					self.open(rootpath=rootpath)

				else:
					raise TypeError(rootpath)

		@ENV.SnapChannel
		def close(self, MSG):
			"()"

		@ENV.SnapChannel
		def open(self, MSG):
			"(str rootpath!)"
			
			# TODO open would mean open the 'working file' for the project, then we add in the source packages...
			# make 'packages' property to get/set?

			# TODO load the package by iterating each language and passing the package rootpath to the language, and then if it found something hang onto the language node...?  then we store each language under the package['languages']

			rootpath = MSG.unpack('rootpath', None)

			self.close()

			if rootpath is None:
				print('no rootpath')
				return

			rootpath = os.path.realpath(rootpath)

			data = {
				'rootpath':rootpath,
				'files':[], # all files, using relative paths to rootpath
				# empty_folders?  just to keep track of them?
			}

			for root,subs,files in os.walk(rootpath):

				for fname in files:
					fullpath = os.path.join(root, fname)
					data['files'].append(fullpath[len(rootpath):])

			# XXX pass project as a whole to language to determine what is relevant?  so build systems can determine it too?
			for f in data['files']:
				ext = os.path.basename(f).split('.')[-1]

			# TODO process build systems first?  because they might make use of language modules...?

			for lang in ENV.LANGUAGE.languages:
				print(lang)
				

			#print(json.dumps(project, indent=4))

			# TODO now parse files by ext
			# TODO then figure out the hierarchy by import scheme...  create a layout that is just a set of lists, but we open and parse each module to figure it out...

			

			# TODO

			# TODO start by just creating a dict with graphics for each concept, render and arrange the graphics here...

			# TODO use ENV.LANGUAGE.by_extension('py') to load decoder if available, otherwise mark unknown

			# create lists of import dependencies and stuff like that, make displays to showcase different analysis

			#ENV.snap_out('open', path)

			#FILE = SnapProjectFile(self, filepath=__file__)
			#FILE.open()
			#self['children'] = [FILE]

			#with open(__file__, 'r') as openfile:
			#	# TODO replace tabs with spaces BEFORE the parse so the spans come out already correct!
			#	text = GFX.Text(text=openfile.read().replace('\t','      '))
			#	#text = GFX.Text(text='hello world')
			#	#text = GFX.Path(description=['L', 0,0, 100,0, 100,100, 0,100, 'C'])

			#print(text['text'], text['text_extents'])

			#text['extents'] = text['text_extents'] # TODO when text is assigned the extents should be updated internally?

			# TODO make ast representation as colored squares behind the text, use grey when name isn't known

			# TODO add each visible element as it's own container, then set that visible element using the source info (dict)...
			# TODO implement the rendering using a shader that implements drawing operations in the draw() call by looking up the info to draw...

			# aspects (requiring own shaders...)
			# file list
			# open module(s) -- module text display -- with own aspects like syntax highlighting (that get assigned to itself)

			#self['children'] = [text]

			# TODO make a container with clipping for file list, 

			# TODO make shaders for interactions, and maybe one for when nothing is open, show a design and 'click to open project'?

			self.changed(rootpath=rootpath)

			

		def __init__(self, ROOTPATH, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

	ENV.SnapProjectPackage = SnapProjectPackage

def main(ENV):

	ENV.__run_gui__(ENV.SnapProjectPackage, rootpath="../../../../demo/programming/hello_world/project/")

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

