# UQ - "You" Queue

## About

Think of this project as **'technological glue'**. The goal is to be able to connect code elements together that were not originally designed to connect together, *easily.* By unifying programming languages into one central form (in c), and by presenting a generic communications interface/protocol (SnapNode protocol) that can be used to connect code elements together arbitrarily (even at runtime).  With this ability, code from different projects (and even different languages) can be made to connect together to create new behaviours and programs...

The primary focus was to make a gui/graphics library that was easy to use and maintain, while also being fully featured and fast.  The graphical concepts are abstract and general (like: image, texture, color, spline, mesh, ...), which protects against changes in the backend (opengl->vulkan?) impacting user code for features that aren't engine specific (*"draw a red rectangle"* should do the same thing with *any* backend!).

The idea of pulling in existing code and integrating it is new, but it's a natural extension to what this project has evolved into (this started as trying to make a paint program 15 years ago XD).  There is no need to write all the features and functionality alone, as there already exist so many amazing open source programs with the code components necessary to get the desired behaviour.  There just needs to be a way to integrate those projects designed with different languages into one easy to use common form...  well here it is! (maybe...)

Honestly if this just ends up being a nice python-based coding and visual programming api that compiles into c, I'm quite happy!  Integrating other languages and projects would just be a bonus, though a nice one!

>*for an in-depth technical explanation of how multiple programming languages can integrate into one common form, see **ATTEMPT TO CLARIFY WITH AN EXAMPLE** below...*


### UQ

**"You Queue"** - meaning you queue up program elements and then run them. This is a GUI-based end-user program intended to be used to connect SnapNode components together visually in a drag-and-drop fashion.

>**TODO:**
- Largely not implemented yet, but it's mostly just going to be a mainwindow with the ability to add ENV elements to the scene by name and provides a graphical type that will be able to render any arbitrary code element as either a node or using its draw method if available...

### snap

The library that implements the SnapNode protocol, and which provides the backend API to use OS-specific interfaces with a general API (things like os, graphics, gui, networking, multiprocessing, ...).  It also provides the interfaces for compiling.

---

## Disclaimer

- I'm a self-taught programmer, learning as I go (for more than a decade now); I'm an art major
- I'm brand new to git and github
- This is being released even though it's "not ready" with the hope of getting more eyes on it and feedback or contributions to make it better. The idea of compiling programming languages is a new addition, and I'm just starting to learn about it now. The graphical/gui system is much more mature.
- My coding philosophy is **"less is more"**, and I always strive to create less code and simplify structures into smaller and shorter interfaces as much as possible. I value readability over speed (and this project is not aimed at programming professionals looking to get maximum performance, but casuals / novices / grandmas(?) looking for a way to easily get their computer to do what they want it to do...)

---

## License

[MIT License](https://opensource.org/license/mit)

---

## Installation

> **Note:** I'm on Linux, not sure how to do this on other systems (but it shouldn't be too hard!)

### 1. Clone the repository

Open a terminal in the directory where you want UQ to be and type:

```bash
git clone https://github.com/G-0-R-D/UQ
```

### 2. Install Python dependencies

Using your version of Python (with pip already installed), run:

```bash
python -m pip install -r requirements.txt
```

Or manually install:

```bash
python -m pip install numpy PyQt5
```

### 3. Install compilers

Install gcc and clang:

```bash
sudo apt-get install gcc clang
```

### 4. Setup Python path

Make sure the `../UQ/snap` folder is visible to your Python install so that `from snap.SnapEnv import SnapEnv` works from anywhere you call it. 

I do this by just adding a symlink to the snap folder in my Python main directory:

```bash
ln -s /absolute/path/to/UQ/snap /absolute/path/to/python<x>/snap
```

> **Important:** Be sure to use absolute (full) paths! Relative paths don't work in symlinks...!

> **Note:** UQ does not need to be on your path, it is meant to be run as a module directly (`python UQ.py`), it just makes use of snap, so that must be on your path.

## Orientation

### `../snap/lib/core`

#### SnapNode

The base type (object) of all other types, which overrides `__getitem__`, `__setitem__`, `__delitem__` to redirect to SnapProperties.

- Use `<SnapNode>['prop']` to access a property, and `<SnapNode>.channel` to access a SnapChannel
  - **Note:** You can access properties as attributes too since they are also channels...

- `__snap_data__` is a special implementation of a dict (missing keys just result in no-op, so `del self.__snap_data__['x']` quietly does nothing if there is no 'x', and `self.__snap_data__['x']` returns None if there is no 'x')

#### `@SnapChannel` decorator

Represents an event, action, or other "behaviour" -- something that you do or something that happens...

- Can **send** (immediately sends to all listeners of this channel) or **emit** (queues up sending until the next mainloop iteration; asynchronous events)

- Implemented as a `def method(self, MSG)` where MSG is a `SnapMessage()` instance (part of how communication is standardized) with a docstring to describe acceptable arguments:
  - **Note:** Docstrings aren't actually used anywhere yet, and the syntax is not finalized...
  - `""` empty string means this is not intended to be used as a connectible interface (might only emit, no input)
  - `"()"` means no args means anything can be connected to it (it doesn't use the message)
  - `"(type)"` or `"(type!)"` or `"(type?)"` mean arg, required arg, or optional arg, with only a type descriptor
  - `"(type name)"` or `"(type name!)"` or `"(type name?)"` is same but with a name attached as well
    - (messages will try to connect names together, or possibly allow re-mapping names by type when a connection is negotiated -- TODO...)

- A channel is identified by its name, same name means same channel
  - (usually connective behaviour is done per-element, where two code objects are connected directly to each other in a hard coupling. Listeners actually just "subscribe" to the name of the channel, not the actual channel itself)
  - i.e. listeners are stored on the `SnapNode.__snap_listeners__` under the channel name, not on the SnapChannel!

#### `@SnapProperty` decorator

Represents a type, or at least a data-based access point. Data can be generated dynamically when requested.

- Implemented using a class and a `def set(self, MSG)`, `def get(self, MSG)` and `def delete(self, MSG)` with a docstring in each:
  - `"()->type"` if '->' comes after parenthesis then it is the return value (just a type)
  - **Note:** If a get() accepts args then it is preferable to use `node.prop.get(args...)`

- Is a subclass of channel so can also send/emit like a channel
  - Call `self.changed(property=value)` when data changes and SnapNode will emit through that property for you

> **Important:** `self` inside of the set/get/delete implementations is the instance that owns the property! Not the property itself...

#### `@myproperty.alias`

Allows for mapping multiple names to the same channel or property implementation.

#### Connecting

Runnable (python) example:

```
from snap.SnapEnv import SnapEnv

ENV = SnapEnv()
SnapNode = ENV.SnapNode

class Example(SnapNode):

    @ENV.SnapChannel
    def channel(self, MSG):
        "(str hello!)"
        ENV.snap_out('hello', MSG.kwargs['hello'])

a, b = Example(), Example()
a.channel.listen(b.channel)
a.channel.send(hello='world')  # NOTE: emit won't do anything unless running a mainloop...
    # >> in b.channel: "hello world"
a.channel.ignore(b.channel)
```

**Note:** The docstrings aren't really used yet, but even in the final version it will be possible to force a connection even if there is no docstring, or the docstring suggests incompatibility, it will be up to the user there will just be a warning.

#### SnapMessage

A way of standardizing communication structures, following the **`(*args, **kwargs)`** concept in Python where unused params are just quietly ignored, ensures that all communicable interfaces share the same "call signature" (they just accept a single MSG argument).

- `MSG.args`: positional arguments (tuple)
- `MSG.kwargs`: keyword arguments (dict)
- `MSG.source`: the SnapNode instance that did the send/emit creating the message
- `MSG.channel`: the channel (str) that originated the message

> Messages should be treated as immutable; don't change them.  If 2-way communcation is required then pass a mutable type like a dict or list to be filled in by the receiver (but beware multiple receivers can connect to emitted messages!)

#### `snap_debug.py`

`ENV.snap_out`, `ENV.snap_warning`, `ENV.snap_error`, etc. give the line number and module path (so you don't have to try to find out 'where did I put that print statement?' -- and they could be replaced with redirects to be silent, or log output, etc...)

#### TODO

- Once the SnapNode protocol was built I just started using it, since I knew the API wouldn't change much... but that means the decorator / bound API could still use more work! Specifically: reduce the number of calls (if possible), and make things a bit more sleek under the hood so it performs better

- Better debug info too... we get like 5 stack traces before the one we're interested in!

- The primitives API will likely just be phased out, it was from an earlier design and only the SnapBytes with the numpy backend is currently useful... using the Python syntax as input means Python primitives will be available when compiled (as long as the c backend API provides them)
  - The original idea was to make properties the raw primitives themselves (like listen to an int directly for changes) but then I realized that properties are actually attributes of a parent type, and don't exist on their own! So this idea is no longer in play.
    - To phrase another way: a property change is an event of the parent SnapNode, not of the property (data) itself because the property (data) doesn't (necessarily) exist at all!
      - aka. if I have an int property that is created on get() (not locally assigned) then how do I listen to the int? I can't. It's a new one each time it is accessed! But I can listen to the property for its get() events (and that property belongs to the parent SnapNode).

---

### `../snap/SnapEnv.py`

- **ENV** is a concept I came up with to remove the need of modules to know anything about the context in which they are running. Module 'imports' (`getattr(ENV, 'x')`) can be changed in ENV before calling the module, making it possible to redirect things, and presents interesting opportunities for adapters... I'm thinking it could be useful for legacy code (imagine being able to use the latest HD VR keyboard on an old game that was designed to use a regular keyboard, by just writing an adapter and assigning the adapter as the ENV keyboard...)

- Allows for modules to be included into the 'global' (ENV) namespace through build(ENV), while also removing the need for import statements (they just access what they need from the ENV, which allows it to potentially be changed even at runtime -- like to redirect print statements to logfiles, or change a device like a keyboard to some futuristic VR keyboard adapter instead...)
	- modules can be run directly with main(ENV)

- User Applications can import `snap.SnapEnv` and subclass it to define their own ENV, and register themselves as an importable package using `SnapEnv.__register_package__("/root/of/package")` which will then allow imports subordinate to that package using `SnapEnv.__build__("package.x")`

- The idea is also that ENV can represent a sandbox or isolation of a runnable program, and could be discarded when finished so that only necessary components are loaded when they are needed (TODO...)

- General practice is to put the `ENV.__build__` commands into `__init__.py` files, so we can just import packages by building the folder containing the `__init__.py` file...

- `ENV.__build__('path.to.module')` calls the `def build(ENV)` function in 'module'

### `../snap/lib/graphics`

`SnapMatrix` → `SnapMetrics` → `SnapContainer` → **user** is the basic intended design. Use `SnapContainer` (or subclass) as the base for all of your renderable elements.

#### SnapMatrix

The base class so that transformables can inherit from it (while also implementing an actual 'matrix' property for the low-level matrix data).

- Matrix format is always 3D, to make things simpler -- optimizations may be considered later

#### SnapMetrics

Adds the concept of an 'extents' which is a min/max point (x,y,z) of a bounding rect. Extents cannot rotate (you rotate the owning matrix instead) and cannot be negative (max >= min must always be true).

#### paint

Color elements (color, gradient, texture, ...)

#### shape

Shape elements (path or mesh; connected points)

#### `draw()` method

Can be implemented directly on the container for hard-coded render instructions, or a shader can be assigned, making render logic changeable at runtime (like change the theme to another one...)

#### `lookup()` method

A single pixel render used to find what is "under the mouse" while respecting clipping masks and other render configuration, and making it possible to consider things like pixel opacity.

- This is used by the GUI for interactions

#### SnapContext

Render interface that presents generalized draw instructions that should be available in just about any backend engine. These are the ones prefixed with `cmd_` meaning "command".

#### Engines

The backend implementations for handling the rendering, they subclass the generic shape/paint types and for the most part just handle I/O operations to get the data in and out of the engine...

#### TODO

- Make it possible to remap coordinate systems in ENV (by swapping the matrix with one that will convert the coordinates internally by doing a fake parent transform using the parent space)

### `../snap/lib/gui`

- `SnapContainer.device_event()` should return True to accept the event, otherwise it will be propagated to the parent (if applicable, depends on event behaviour -- proximity events are always sent to all for example)

#### TODO

- Would like to actually remove the Qt backend and do something more direct but cross-platform, but have to research this...

#### `../snap/lib/os/devices/keymap`

- Needs to be figured out. I think identifying keys by name is preferable to the mess that codes are! But still the names would need to be mapped from the GUI lib or OS! Every GUI seems to have a completely different set of keycodes... help!

### `../snap/lib/parsing/parseq`

This is my own parser design. It's designed to be as easy to use as possible, with very straightforward syntax and the ability to parse in layers (makes ignoring irrelevant whitespace easy to do, without having to add it to the grammar - just capture what you care about in layer 1, and check for patterns in it in layer 2).

- Backend is complete, frontend needs work, but I haven't needed to work on it in quite a while. The plan now is to have the languages parse their AST for me, removing the need to even have a parser! Although I imagine it may still come in handy...

- **"parseq"** as in "parse sequence" - it can handle sequences of anything
  - Also it's a Star Wars joke/reference (when Han says "parsec" to mean speed, when it's actually a measure of distance.) Parseq is really fast :) (even in Python!)
  - Parseq is fast because of its multi-pass approach: when the upper levels fail to match it just drops down to level 1 (tokens still completed) rather than all the way back to characters...

### `../snap/lib/programming`

This is the core functionality, and the newest module. The objective is to be able to take an existing code project (in any *supported* language) and 'pull it in' either by compiling it or interpreting it, into a 'generalized' format implemented in ANSI C (`-std=c89`) which should hopefully be very portable...

- Clear and easy to read and understand code is far more valuable to me than fast but hard to read code...

- Python decoding is largely finished (so take a look):

```bash
python snap/lib/programming/language/python/SnapPythonLanguageDecoder.py
```

- C/C++ is being worked on using JSON AST from clang (trying to find a way to get complete AST list...)

- Planning on Java next, more to come!

#### `../programming/include/`

The implementation of the C backend, largely a work in progress! Will be able to say `#include "snap.h"` to use.

- Modules will be built into header files with a `<MODULE_NAME>_MAINBODY(ENV)` which represents the 'run' of the module (code that runs if you imported the module in Python)
- Compilation would create a `main.c` with initialization of the ENV, include all modules, and then call `MAINBODY(ENV)` of each imported module

#### `../programming/include/snap/core/snap_types.h`

`SnapObject_t*` defines the basic object type interface, `SnapEnv_data_t*` will be the `__bytes__` of `../programming/include/snap/types/SnapEnv.py`

#### `../programming/SnapInternalCompiler.py`

Working on using this (old) design to compile a usable core while being able to type Python to implement :)

Try it out:

```bash
python snap/lib/programming/SnapInternalCompiler.py
```

#### `../programming/project/SnapProject.py`

- This is my main focus right now, once this is complete navigating through code will be much easier...

- Primary API (with GUI) to be able to navigate through code to find components you need... try:

```bash
python snap/lib/programming/project/SnapProject.py
```

#### TODO

**All of it!**

The idea is to map the concepts presented by the coding language into a more generalized language-neutral form (but based largely on the design concepts of Python: object orientation, async, ...), so they can play nicely together, making it very easy to pull parts of a project or the whole thing into an ENV to run and do what you want to do with it...

**Key insight:** Languages usually provide their own AST output, so if we just convert that to JSON with generalized (language-neutral) descriptions then we could support potentially any/all languages by:

- Re-organizing the AST into new structures that perform equivalent behaviour (using existing node types)
- **AND/OR:** Defining new operations (or adding extra behaviour to existing operations) in the compiler (when necessary)

**Op-codes are C functions** that perform operations on the current ENV and stack...

- By compiling to C, it's easier than going to assembly (with all the hardware versions, C handles the compiling to assembly part)
- C allows for higher-level abstraction and reasoning, and makes it easier to implement more complex data structures for the compiler to make use of (representing classes and functions, and making everything a `SnapObject_t*` type...)
  - I have no idea how I would even begin representing object orientation in pure assembly!

**Current status:** I've actually only had the concept of compiling other projects into a common source in mind for a few months now, so lots of TODO! Gonna try to get the `SnapProgrammingLanguageCompiler.py` working by following `Python-3.12.3/Python/compile.c` at https://www.python.org/downloads/release/python-3123/ and referring to this guide: https://realpython.com/cpython-source-code-guide/#core-compilation-process

- Python has many custom op codes (see https://docs.python.org/3/library/dis.html#python-bytecode-instructions) so the idea of creating custom op-codes to support features from other languages doesn't seem so far-fetched...

- Most languages have common concepts (classes/types, functions, ints, floats, ...) so generalizing to a common form for at least those should be easy enough...

- Wish me luck! (and thanks for any help!)

---

# ATTEMPT TO CLARIFY WITH AN EXAMPLE:

Let's consider an example of what it could mean to compile languages into a shared form by considering something most languages have in common, a function definition:

### in python:
```python
def sum(a, b):
	return a + b
```

### in c:
```c
int sum(int a, int b){
	return a + b;
}
```

### in java (forbids static functions btw...):
```java
public class Boilerplate {
    public int sum(int a, int b) {
        return a + b;
    }
}

```
The java example just means we wouldn't be able to have a function on it's own, so it would be a method of a class instead...  but the ideas still map readily!  When using the java code you would be expected to call Boilerplate().add(...) anyway, so java code would be internally consistent...

### now the same function represented in snap (-std=89 c) as a generalized concept of a function taking 2 ints (this code is very oversimplified, and won't run, but is conceptually accurate):

```c
typedef struct SnapObject_t {

	/* all types are implemented as a SnapObject_t*, with a function handler representing both the id() and the callable interface */

	SnapObject_t* (*__type__)(SnapObject_t* ENV, const char* ATTR, SnapObject_t* MSG);
	SnapObject_t* __dict__; /* where user callables are stored */
	ssize_t __bytes_size__; /* sizeof __bytes__ */
	char* __bytes__; /* any arbitrary data associated with the type (int* for int type, the actual number -- type decides what this is and manages it itself) */

	/* ... see ../UQ/snap/lib/programming/include/snap/core/snap_types.h for the full (current) implementation design ... */

} SnapObject_t;

SnapObject_t* function_type(SnapObject_t* ENV, const char* ATTR, SnapObject_t* MSG){

	/* const char* address will be the same 'identity' for the same word, this is exploited for readability! */

	if ((void*)ATTR == (void*)"__call__"){

		SnapObject_t* a = _msg_unpack(MSG, "a");
		SnapObject_t* b = _msg_unpack(MSG, "b");

		/* could do isinstance check to make sure a and b are ints, if the input language is strict-typed like c then we would... */

		/* then this would call the a.__add__(b) logic (not shown here) */
		return _call(ENV, a, "__add__", _msg(_arg(b)));
	}
}

int main(int argc, char* argv){

	SnapObject_t* ENV = malloc(...); /* basically just a custom class acting like a namespace to store attrs... */

	/* _new() would just assign the SnapObject_t* members to init stuff, and call the "__init__"|"__new__" methods of the type... */
	SnapObject_t* function = _new(ENV, function_type);

	/* a and b would be initializations of int types as well */

	SnapObject_t* _return = _call(ENV, &function, "__call__", _msg(_a2(a, b)));

	/* _return will be SnapObject_t* int_type with the answer assigned to it's __bytes__ member... */

	return 0;
}

```
> **Note:** The design of the backend is largely still a work in progress, so **the above code is very likely to change and wouldn't run**, it's just meant to briefly illustrate the concept.
>> **also note: the above code would be *auto-generated* and *not* typed out by hand!**

Then consider the 'generalized' ast form (in language-neutral json) of a function definition that could support the function description of each input language (this would just be the method part if the input is java):

```python
{
	'__type__':'function',
	'name':'sum',
	'arguments':[
		# 'data_type' would just mean do an isintance(arg, int) or raise in the call...
		{'__type__':'name', 'value':'a', 'data_type':'int'},
		{'__type__':'name', 'value':'b', 'data_type':'int'}],
	'body':[
		{'__type__':'return', 'target':{
			'__type__':'binary_operation',
			'operands':[
				{'__type__':'name', 'value':'a'}, {'__type__':'name', 'value':'b'},
			],
			'operator':'add',
			}}
		],
}
```

Everything you need to know about the function in all 3 input languages would be representable by this ast form (except java would be a method inside a class).  So if we have the ast from each language in json, translate that json into generalized form (or support the new unique idea in the backend if it can't be generalized), then we could theoretically bring in new languages by translating them to the *common* or *generalized* output and then connecting those components together since they are now the *same types* in the *same language* :)

Now, we just have to represent the above as a series of opcodes, and we're there XD!  (actually the op-based compiler would be at the user-level, the backed implementations would compile to non-asynchronous interfaces (no yield statements!)).  This means a lot of the backend can actually be written in python syntax.  I'm thinking of using "snapc:" strings to 'switch' into c code where needed while in the .py files...


## Closing

If you've read all this, I thank you very much for doing so! I appreciate your interest, and look forward to your feedback and input! Cheers!

**-Gord**
