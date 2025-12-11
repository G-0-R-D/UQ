
def main(ENV):

	print('ok')

	class Base(ENV.SnapNode):

		@ENV.SnapProperty
		class prop:
			def set(self, MSG):
				print('inside prop.set()', MSG.args, MSG.kwargs)

			def get(self, MSG):
				print('inside prop.get()', MSG.args, MSG.kwargs)

		@ENV.SnapChannel
		def channel(self, MSG):
			print('inside channel()', MSG.args, MSG.kwargs)

	print(Base.channel)
	print(Base.prop)

	instance = Base()
	print(instance.channel)
	print(instance.prop)

	print(instance.__class__.prop)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv())
