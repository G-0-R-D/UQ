
# GRAPHICS
### BASICS
> SnapMatrix -> SnapMetrics -> SnapContainer -> **user** is the basic intended design. Use `SnapContainer` (or a subclass) as the base for all of your renderable elements.

>TODO:explain: each class is designed/intended to be a 'one size fits all format' which is why I chose 3D matrix even for 2D operations, as an interface, we go with the fullest representation (RGBA) and then in the backend we'll worry about optimizations
	-- this increases compatibility as types end up being the same more often (rather than 2D/3D matrix being incompatible -- they don't have to be!  many operations could work between them, a 2D matrix is just a 3D matrix ignoring changes to the 3rd axis)

## SnapMatrix

# TODO the SnapMatrix is an interface, snap_matrix_t is the data

This is the base class of all transformables.  Implements a **'matrix'** `SnapProperty` for low-level `snap_matrix_t` datatype (a ctypes double[16] representation of the matrix).  The idea is to present a high-level user-friendly `SnapMatrix` class for ease of use, while also exposing the low-level `snap_matrix_t` and associated `snap_matrix_x` operators to perform quicker matrix operations when it matters.

The operations that return a new `SnapMatrix` are implemented via the SnapProperty interface (['inverted'], ['identity'], ...), while the in-place operations act on the internal ['matrix'] data.  The ['matrix'] belongs to the `SnapMatrix`, so changes made to it will apply to the `SnapMatrix` unless a new one is assigned like: `SnapMatrix()['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)`.

>TODO:explain: matrix format is always 3D, to make things simpler -- optimizations may be considered later

> can inherit from it (while also implementing an actual 'matrix' property for the low-level matrix data).

>TODO:explain: matrix can be thought of as an orientation in space, and represents a kind of container for all it's child items...

```
M = SnapMatrix()
m = M['matrix']
O = SnapMatrix(matrix=m)['translated']
```

## SnapMetrics

Adds the concept of an 'extents' which is a min/max point (x,y,z) of a bounding rect. Extents cannot rotate (you rotate the owning matrix instead) and cannot be negative (max >= min must always be true).

>TODO:explain: adds an extents (size) to the concept of a matrix
	-- lots of sizing api components that reference extents internally, so just have to update extents for all of them to work...
>TODO:explain: fit() system (why no Layout() class like gui always has...)
	-- also: layouts can be managed by new asset manager

#### paint

Color elements (color, gradient, texture, ...)

#### shape

Shape elements (path or mesh; connected points)

- (TODO: shape/shader model and shapes can be added to scene (only need a draw and render_items property to render...))

# SnapContainer

>TODO:explain: this is the base class for renderables, provides interface, event manager, asset manager...

#### `draw()` method

Can be implemented directly on the container for hard-coded render instructions, or a shader can be assigned, making render logic changeable at runtime (like change the theme to another one...)

>TODO:explain: it is safe to add any SnapNode to a renderable scene, but it will only transform if it implements a ['render_matrix'].get(), and children are accessed via ['render_items'] or ['lookup_items']
	# TODO: phase out 'lookup_items'?   lookup can use same items, and then they decide if they do anything with the lookup() call themselves...

#### `lookup()` method

A single pixel render used to find what is "under the mouse" while respecting clipping masks and other render configuration, and making it possible to consider things like pixel opacity.

- This is used by the GUI for interactions

## SnapContext

Render interface that presents generalized draw instructions that should be available in just about any backend engine. These are the ones prefixed with `cmd_` meaning "command".

## Engines

The backend implementations for handling the rendering, they subclass the generic shape/paint types and for the most part just handle I/O operations to get the data in and out of the engine...

#### TODO

- Make it possible to remap coordinate systems in ENV (by swapping the matrix with one that will convert the coordinates internally by doing a fake parent transform using the parent space)

>TODO: see UQ/demos/graphics/...

