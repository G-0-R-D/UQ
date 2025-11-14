

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

### `../snap/lib/programming/parsing/parseq`

This is my own parser design. It's designed to be as easy to use as possible, with very straightforward syntax and the ability to parse in layers (makes ignoring irrelevant whitespace easy to do, without having to add it to the grammar - just capture what you care about in layer 1, and check for patterns in it in layer 2).

- Backend is complete, frontend needs work, but I haven't needed to work on it in quite a while. The plan now is to have the languages parse their AST for me, removing the need to even have a parser! Although I imagine it may still come in handy...

- **"parseq"** as in "parse sequence" - it can handle sequences of anything
  - Also it's a Star Wars joke/reference (when Han says "parsec" to mean speed, when it's actually a measure of distance.) Parseq is really fast :) (even in Python!)
  - Parseq is fast because of its multi-pass approach: when the upper levels fail to match it just drops down to level 1 (tokens still completed) rather than all the way back to characters...


