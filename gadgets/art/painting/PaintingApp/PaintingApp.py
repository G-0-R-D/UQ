
def build(ENV):

	"""
	tiled surface, each tile as 3 layers (value (8 bit grey), color (RGB), and mask/alpha (8 bit)) -- can we combine value and color?
		operations act on the appropriate layer

	then we can have user layers using tiles (that lineup with lower layer tiles)

	also, painting can direct to low resolution image for responsive UI display, and a background process can render the high res tiled image on disk for quick responsive painting at high-res...?

	NOTE: we only need to create tiles where there is paint, otherwise full transparency is assumed

	"""
