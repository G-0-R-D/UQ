
# test to trigger all ast nodes in one go (not necessarily one at a time)
# NOTE: this is to test ast parsing, this file won't actually run...

# following: https://docs.python.org/3/library/ast.html#root-nodes

# Module

# -

# Expression

x

# Interactive

# -

# FunctionType

def sum(a, b):
	# type: (int, int) -> int
	return a + b

# LITERALS -----

# Constant

'str'
b'bytes'
1 # int
1.0 # float
# complex?
True # bool
None
#... # ellipsis no longer supported

# TODO FormattedValue

# TODO JoinedStr

# TODO TemplateStr

# TODO Interpolation

# List

[1,2,3]

# Tuple

(1,2,3)

# Set

{1,2,3}

# Dict

{'a':1}

# VARIABLES -----

# Name

name

# Load

name

# Store

name = 1

# Del

del name

# Starred

a, *b = iterator()
call(*unpack)

# EXPRESSIONS -----

# Expr - statement by itself

p

# UnaryOp

# UAdd
+1
# USub
-1
# Invert
~1
# Not
not 1

# BinaryOp

# Add
1 + 1
# Sub
1 - 1
# Mult
1 * 1
# Div
1 / 1
# FloorDiv
1 // 1
# Mod
1 % 1
# Pow
1 ** 1
# LShift
1 << 1
# RShift
1 >> 1
# BitOr
1 | 1
# BitXor
1 ^ 1
# BitAnd
1 & 1
# MatMult XXX why?  just use __mul__ on a matrix class...
#1 @ 2

# BoolOp

# And
1 and 2 and 3
1 and (2 and 3)

# Or
1 or 2 or 3
(1 or 2) or 3

# Compare

# Eq
1 == 1
# NotEq
1 != 1
# Lt
1 < 1
# LtE
1 <= 1
# Gt
1 > 1
# GtE
1 >= 1
# Is
1 is 1
# IsNot
1 is not 1
# In
1 in [1]
# NotIn
1 not in [1]

# Call
# keyword
a(1,2, *args, a=3, **kwargs)

# IfExp
if a:
	'a'
else:
	if b:
		'b'
	else:
		'c'

# Attribute
a.b.c

# NamedExpr
#x := 4 # XXX v3.8!

# Subscript
my_list[:c():2, 'other']

# Slice
my_list[:]

# ListComp
[x for x in (1,2,3)]
# SetComp
{x for x in (1,2,3)}
# GeneratorExp
(x for x in (1,2,3))
# DictComp
{i:i for i in (1,2,3)}

# comprehension
[x if x else y for x in (1,2,3) for y in (4,5,6)]
# https://peps.python.org/pep-0530/
[i async for i in (1,2,3)]

# STATEMENTS

# Assign
a = 1
(a,b) = 1,2
# AnnAssign
#c: int # XXX TODO?
# AugAssign
a += 1
a *= 1
# Raise
raise Exception('oops')
# Assert
assert 'ok', 'message'
# Delete
del a
del a,b,c
# Pass
pass
# TypeAlias
#type a = int # XXX TODO

# IMPORTS

# Import
import x,y,z as banana
# ImportFrom
from ..x import (a,b,c as fruit)

# CONTROL FLOW

# If
if 'a':
	'a'
elif 'b':
	'b'
elif 'c':
	'c'
else:
	if 'A':
		'A'
	else:
		'B'
# For
for x in (1,2,3):
	pass
else:
	'what?'
# While
while 1:
	pass
else:
	'wut?'

# Break
break
# Continue
continue
# Try
# ExceptHandler
try:
	'a'
except (OSError, SystemError):
	'b'
except Exception as e:
	'c'
else:
	'oh yeah?'
finally:
	'cleanup time!'
# TryStar XXX TODO?
#try:
#	'a'
#except* Exception:
#	'?'
# With
# withitem
with something as another:
	pass

# TODO ... v3.8 stuff?

# FunctionDef
# arguments
@decorator
def func(a, b, *c, d=1, e=2, **f):
	print('ok')
	return 'ok'
# Lambda
lambda x: x

# Return
def func():
	return
# Yield
def func():
	yield 'a'
# YieldFrom
def func():
	yield from b

# Global
global x,y,z
# Nonlocal
nonlocal a,b,c

# ClassDef
@decorated
class Class(object):
	__slots__ = []

	def method(self):
		pass

