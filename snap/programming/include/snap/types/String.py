
# TODO
# _str() is always const char* type, and __byte_size__ < 0 to indicate it isn't owned
#	-- then we can check __byte_size__ < 0 and __type__ == str to know if it is const
# const strings should also have identifier codes so we can use switches?
#	-- strings are assigned to ENV and obtained from there?
