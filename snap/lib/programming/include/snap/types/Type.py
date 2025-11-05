
# TODO
"""

c func is assigned to __bytes__ of function type?  and when the function __call__ is used it forward to the c function call (or to opcodes if c function is not defined?

need to also emulate pythons type() api...  maybe the __call__ of the Type base can handle the various arguments appropriately?



"""

# NOTE: this is just using python syntax for defining the type, this is compiled into a c representation

class Type:

	__slots__ = []

	def __call__(self, *a, **k):
		'' # based on args either create new type instance or return the type of the input

	def __new__(self, *a, **k):
		''

	def __init__(self, *a, **k):
		''

