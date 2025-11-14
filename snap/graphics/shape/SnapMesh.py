

# https://wiki.blender.org/wiki/Source/Modeling/BMesh/Design

"""
typedef struct SnapMesh_data_t {
	int count;
	void* format; // const char *format
	// do vertices, edges (vert pairs (in continuous run?)), faces (edge sets)?
	// what about a void* to the format struct of a vertex?  then use the numbers to describe it's format?
	void* positions;
	void* indices;
	void* uvs;
} SnapMesh_data_t;
"""

def build(ENV):

	SnapShape = ENV.SnapShape

	class SnapMesh(SnapShape):

		__slots__ = []

		#def set(self, MSG):
		#	return SnapEngineData.set(self, MSG)

		def __init__(self, **SETTINGS):
			SnapShape.__init__(self, **SETTINGS)

	ENV.SnapMesh = SnapMesh


"""
any SnapMesh_event(SnapNode* self, any EVENT, SnapNode* MSG){

	if_ID
		return SnapEngineData_event(self, EVENT, MSG);
	}

	else if (EVENT == (any)"SET"){

		// point_count, axes
		// vertices, uvs, normals, indices?
		// store in sets of structs?

		any vertices = NULL;
		any indices = NULL;
		any uvs = NULL;

		any format = NULL; // axes, ...?

		(void)vertices;(void)format;(void)indices;(void)uvs;

		// any texture = NULL; ?? how to organize per-vertex textures?

		for_attr_in_SnapNode(MSG)
			if (attr == (any)"vertices"){
			}



			// TODO simple standard shape creation api
			else if (attr == (any)"rect" || attr == (any)"rectangle"){
				snap_event_noargs(self, "CLEAR");
				snap_event(self, "ADD", "rectangle", value);
			}

			else snap_event_redirect(SnapEngineData_event, self, EVENT, attr, value);
		}
		return NULL;
	}

	else if (EVENT == (any)"GET"){
		for_attr_in_SnapNode(MSG)
			if (attr == (any)"vertices"){
				// 
			}
			else snap_event_redirect(SnapEngineData_event, self, EVENT, attr, value);
		}
	}

	else if (EVENT == (any)"ADD"){
		for_attr_in_SnapNode(MSG)
			if (attr == (any)"rect" || attr == (any)"rectangle"){
				snap_warning("mesh rect not yet implemented"); // TODO how to handle uvs/normals?
			}

			else snap_event_redirect(SnapEngineData_event, self, EVENT, attr, value);
		}
		return NULL;
	}

	else if (EVENT == (any)"CLEAR"){
		snap_warning("Mesh clear not yet implemented"); // TODO
		return NULL;
	}

	else if (EVENT == (any)"INIT"){
		SnapEngineData_event(self, EVENT, MSG);

		// TODO points, uvs, normals, edges, faces, ...?

		// TODO point_count or vertex_count is double of number of points, then include position_data/vertex_data, texture_map_data/uv_data, normal_data, ...
		// and weave all the data together then list as "properties" in order of weaving?
		// data can be any dimension (point positions as xy or xyz)

		// also load into sets but in single array?  use markers for set spans

		return NULL;
	}

	else if (EVENT == (any)"DELETE"){
		//
	}

	else_if_isinstance(SnapMesh_event)

	return SnapEngineData_event(self, EVENT, MSG);
}


"""
