# UQ - "You" Queue

## About

Think of this project as **'technological glue'**. The goal is to be able to connect code elements together that were not originally designed to connect together, *easily.* By unifying programming languages into one central form (in c), and by presenting a generic communications interface/protocol (SnapNode protocol) that can be used to connect code elements together arbitrarily (even at runtime).  With this ability, code from different projects (and even different languages) can be made to connect together to create new behaviours and programs...

The primary focus was to make a gui/graphics library that was easy to use and maintain, while also being fully featured and fast.  The graphical concepts are abstract and general (like: image, texture, color, spline, mesh, ...), which protects against changes in the backend (opengl->vulkan?) impacting user code for features that aren't engine specific (*"draw a red rectangle"* should do the same thing with *any* backend!).

The idea of pulling in existing code and integrating it is new, but it's a natural extension to what this project has evolved into (this started as trying to make a paint program 15 years ago XD).  More recently I realized, there is no need to write all the features and functionality alone, as there already exist so many amazing open source programs with the code components necessary to get the desired behaviour.  There just needs to be a way to integrate those projects designed with different languages into one easy to use common form...  well here it is! (maybe...)

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
python -m pip install numpy PyQt5 PyOpenGL
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

### `UQ/snap/core`

>*see: [UQ/snap/core/README.md](https://github.com/G-0-R-D/UQ/tree/main/snap/core/README.md)*

### `UQ/snap/graphics`

>*see: [UQ/snap/graphics/README.md](https://github.com/G-0-R-D/UQ/tree/main/snap/graphics/README.md)*

### `UQ/snap/gui`

>*see: [UQ/snap/gui/README.md](https://github.com/G-0-R-D/UQ/tree/main/snap/gui/README.md)*

### `UQ/snap/programming`

>*see: [UQ/snap/programming/README.md](https://github.com/G-0-R-D/UQ/tree/main/snap/programming/README.md)*

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
