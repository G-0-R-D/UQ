
---------------
### 📌 Pinned
---------------

### 💡 Wishlist / 🕒 TODO / 🛠️ WIP
- 🖥️ *(gui)* `SnapContainer.window_event()` for handling visibility and focus/HUD protocol as well as better camera control...
		
- 🖥️/🎨 *(gui/graphics)* making a new event and asset management system (which integrates with existing protocols), instead of having to make properties for every new renderable, or setup custom rendering config for each new SnapContainer -- will also handle 'layouts'
		
- 🎨 *(graphics)* SnapContext will support context management with a ['subcontext'] property to easily do a local render and save/restore (inspired by how qt5 does `with QPainter(self) as ptr: ...`)
		
- 🎨 *(graphics)* OpenGL (this would be [@G-0-R-D](https://github.com/G-0-R-D)'s 5th(?) time wrapping it... shouldn't take too long once he starts!)
		
- 🧱/🔒 *(stability/security)* ENV.QUIT channel for things like SnapSubprocess to listen to, protected by try/except (SystemExit, KeyboardInterrupt) so everything has a chance to shutdown properly and subprocesses aren't left hanging...
		
- 🖥️/⌨ *(gui/keyboard)* gen a keymap for the default keyboard layout that is compatible with qt5 so keyboard events can be used...
		
- 🤖 *(programming)* argspec parsing with parseq (and gui debugging for parseq)
		
- 🎨/📽 *(graphics/animation)* get the animation system working via `ENV.ANIMATION.animate(...)`

	
---------------


---------------
## 2025.11.14 📢
---------------

- 📊/🎨/𝐓 *(report/graphics/text)* Polished up text metrics a bit more. Seems to all be working, but some features still missing (like subline extents).  Done working on it for now...



---------------
## 2025.11.13 📢
---------------

### 📌 pinned / 💪 finished
- 🎨/𝐓 *(graphics/text)* Accurate Glyph Metrics from Qt5!  [@G-0-R-D](https://github.com/G-0-R-D) has implemented it using QTextCursor! (previous web-searches for "text metrics in Qt5" never made any reference to the cursor...).  There is still a bit more TODO on it, but it's there!

		
- 🚛/🎨/𝐓 *(moved/graphics/text)* Text metrics are being merged back into the SnapText class itself.

		
- ✨/🎪/🎨/𝐓 *(new/demo/graphics/text)* **`UQ/demo/snap/graphics/TextMetricsDemo.py`**

	
### 🫧 Housekeeping
- 🚛 *(moved)* removed **`snap/lib`** so it is just **`snap`** now, as [@G-0-R-D](https://github.com/G-0-R-D) now understands 'lib' means something else! (this was named long ago, before he knew what a lib was XD)

		
- 📚 *(docs)* added `PyOpenGL` to pip **`requirements.txt`** and in **`README.md`**

	

---------------
## 2025.11.12 📢
---------------

### 🐛 Bugs
- 😺 *(git)* new .gitignore had a definition for **`lib/`** which was ignoring updates in the **`snap/lib`** folder!  commented it out, and a few more...  (this project isn't intended to integrate other packages *directly*, so .gitignore shouldn't be much of an issue.)

	
### 📚 Documentation
- 💪 *(finished)* **`CHANGELOG.md`** is now generated from an xml template (and [@G-0-R-D](https://github.com/G-0-R-D) will be using it for documentation as well shortly...)

	

---------------
## 2025.11.11 📢
---------------

### ❗ Refactoring
- 🚛/🤖 *(moved/programming)* re-organized compiler code for the SnapInternalCompiler, going with a design that should be more future-proof and make it easier for subclasses to "opt-in" to operations instead of just inheriting them all...  also implemented using methods instead of conditionals, cleaner.
		
- 🚛/🤖 *(moved/programming)* moved **`snap/lib/parsing`** folder into **`snap/lib/programming/parsing`** since parsing is really a programming concept, and the docs should be together too.

	
### 📚 Documentation
- 🕒 *(pending)* in the process of creating README.md files in the directories of interest (graphics, programming, etc...) to go into detail instead of trying to cram everything in the main **`README.md`**

	
### 🧠 Learning
- 🫧 *(maintenance)* [@G-0-R-D](https://github.com/G-0-R-D) Learned [how to make a nice changelog](https://github.com/orhun/git-cliff/blob/main/CHANGELOG.md)

	
### 📌 pinned / 💡 Wishlist / 🕒 TODO / 🛠️ WIP
- 🎨/𝐓 *(graphics/text)* Accurate Glyph Metrics from Qt5 ([@G-0-R-D](https://github.com/G-0-R-D) might know of a way to do it...)
		
- 🖥️ *(gui)* `SnapContainer.window_event()` for handling visibility and focus/HUD protocol as well as better camera control...
		
- 🖥️/🎨 *(gui/graphics)* making a new event and asset management system (which integrates with existing protocols), instead of having to make properties for every new renderable, or setup custom rendering config for each new SnapContainer -- will also handle 'layouts'
		
- 🎨 *(graphics)* SnapContext will support context management with a ['subcontext'] property to easily do a local render and save/restore (inspired by how qt5 does `with QPainter(self) as ptr: ...`)
		
- 🎨 *(graphics)* OpenGL (this would be [@G-0-R-D](https://github.com/G-0-R-D)'s 5th(?) time wrapping it... shouldn't take too long once he starts!)
		
- 🧱/🔒 *(stability/security)* ENV.QUIT channel for things like SnapSubprocess to listen to, protected by try/except (SystemExit, KeyboardInterrupt) so everything has a chance to shutdown properly and subprocesses aren't left hanging...
		
- 🖥️/⌨ *(gui/keyboard)* gen a keymap for the default keyboard layout that is compatible with qt5 so keyboard events can be used...
		
- 🤖 *(programming)* argspec parsing with parseq (and gui debugging for parseq)
		
- 🎨/📽 *(graphics/animation)* get the animation system working via `ENV.ANIMATION.animate(...)`

	

---------------
## 2025.11.10 📢
---------------

### 🧠 Learning
- 😺 *(git)* [@G-0-R-D](https://github.com/G-0-R-D) learned how to accept a pull request!

	
### 🎖️ Contributions
* 👑 *(contributor)* [@Shmalikov](https://github.com/Shmalikov) made ***THE FIRST*** contribution in [[#1](https://github.com/G-0-R-D/UQ/pull/1)]

	
