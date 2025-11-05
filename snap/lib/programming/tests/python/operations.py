
# unary

-1
+1
~1
not 1

# binary

a, b = 1, 2
a + b
1 + 1
a - 1
a * b
a / b
a // b
a % b
a ** b
a << b
a >> b
a | b
a ^ b
a & b

# bool

1 or 2
a or b or a
a and b and b
a and b or 1 or 2 and 3
a and b or (1 and 2 or 3) # TODO order is not caught by py ast parse?

# compare

1 == 2
a != b
2 < a
3 <= 3
2 > 3
a >= 2
a is b
a is not 2
a in [1,2]
b not in [a]

1 == 2 == 3
2 <= 3 <= 4 == 5

# check evaluation in multi-comparison statements (if left side is True, then it returns and right side is not evaluated)
def c(BOOL):
	assert BOOL is True
	return BOOL
c(True) or c(True)
c(True) or False and c(False)
c(True) and c(False)
True and c(True) or c(False)

