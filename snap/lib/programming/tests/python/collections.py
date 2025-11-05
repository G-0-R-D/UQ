
# list

l = list()
l = []
l = [1,2,3]
l[:3]
l[0] = 0

# tuple

t = tuple()
t = ()
t = (1,2,3)
t[:3]

try:
	t[0] = 0
except:
	print('ok')

# set

s = set()
s = {1}
s[:3]
s[0] = 1

# dict

d = dict()
d = {}
d = dict(a=1)
d = {'a':1, **d}
d[0] = 1

