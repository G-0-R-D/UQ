

def run_with_valgrind(self):

	# https://valgrind.org/docs/manual/manual.html
	"""
	valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes --verbose --log-file=valgrind-out.txt ./libsnap

	valgrind --leak-check=full --show-leak-kinds=definite --track-origins=yes --read-var-info=yes --log-file=valgrind-out.txt -v ./libsnap

	"""

	raise NotImplementedError()

