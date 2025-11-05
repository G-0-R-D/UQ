
#a and b or (1 and 2 or 3) # TODO order is not caught by py ast parse?
#1 and (2 or 3 and 4) and 5 and (6 or 7 or 8)
#1 and 2 and (3 or 4 or 5)
#1 and 2 and 3 or 4 <= (1 <= 2 <= 3 <= (1 or 2 or 3))
#1 and 2 or 3 and 4 and 5

#1 <= (2 > 3) < 4



#try:
#	print('hi')
#except:
#	print('error')

for a in (1,2,3):
	print(a)

