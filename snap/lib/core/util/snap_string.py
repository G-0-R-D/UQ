

def camelcase_to_lowercase_underscored(STRING):
	if not STRING:
		return ''
	# NOTE: we don't insert '_' before first character (hence STRING[1:])
	return STRING[0].lower() + ''.join(['_' + c.lower() if c.isupper() else c for c in STRING[1:]])

def lowercase_underscored_to_camelcase(STRING):

	if not STRING:
		return ''
	idx = 0
	while idx < len(STRING) and STRING[idx] == '_':
		idx += 1
	if not idx < len(STRING):
		return ''
	s = []
	while idx < len(STRING):
		if STRING[idx] == '_':
			idx += 1
			if idx < len(STRING) and STRING[idx] != '_':
				s.append(STRING[idx].upper())
				idx += 1
			continue
		else:
			s.append(STRING[idx])
				
		idx += 1
	return ''.join(s)


