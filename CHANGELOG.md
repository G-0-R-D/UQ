
---------------
### 📌 Pinned
---------------

### 💡 Wishlist / 🕒 TODO / 🛠️ WIP
- 🖥️ *(gui)* `SnapContainer.window_event()` for handling visibility and focus/HUD protocol as well as better camera control...
		
- 🖥️/🎨 *(gui/graphics)* making a new event and asset management system (which integrates with existing protocols), instead of having to make properties for every new renderable, or setup custom rendering config for each new SnapContainer -- will also handle 'layouts'
		
- 🎨 *(graphics)* SnapContext will support context management with a ['subcontext'] property to easily do a local render and save/restore (inspired by how qt5 does `with QPainter(self) as ptr: ...`)
		
- 🎨 *(graphics)* OpenGL (this would be [@G-0-R-D](https://github.com/G-0-R-D)'s 5th(?) time wrapping it... shouldn't take too long once he starts!)
		
- 🧱/🔒 *(stability/security)* ENV.QUIT channel for things like SnapSubprocess to listen to, protected by try/except (SystemExit, KeyboardInterrupt) so everything has a chance to shutdown properly and subprocesses aren't left hanging...
		
- 🤖 *(programming)* argspec parsing with parseq (and gui debugging for parseq)
		
- 🎨/📽 *(graphics/animation)* get the animation system working via `ENV.ANIMATION.animate(...)`

	
---------------


---------------
## 2025.11.16 📢
---------------

- 📌/💪/🖥️/⌨ *(pinned/finished/gui/keyboard)* keymap is now good enough!  We'll revisit this later, but for now, if a key is incorrect then it can be reconfigured in the **`UQ/snap/os/devices/config/SnapDeviceKeyboard.json`** file.  Qt doesn't distinguish L/R for modifier keys (Shift, Ctrl, Alt, ...) so if you want to distinguish between them in your code they must be registered in the config with a given scan code like:

			# inside config/SnapDeviceKeyboard.json, remove "Shift" and replace with:
			{
				"LeftShift":{"Qt":"Key_Shift", "scan":50},
				"RightShift":{"Qt":"Key_Shift", "scan":62}
			}

	The keys are still not physical keys, but the idea of physical keys seems to be going out of style...  so the approach for a physical key would be to accept both inputs in your hotkeys.  Like "Control" + ("Period" or "Greater") to accept any '.' key input...  (it's all so messy, putting it down for now!)

	I will add that it's surprising there isn't a more robust interface to 'query' the available devices, so we could find out what physical keys are on the device, etc...  rather than flying blind and not knowing what kind of input configuration we're even dealing with!

	
- 🚛/🖥️/⌨ *(moved/gui/keyboard)* keymap logic is now merged/integrated into the **`SnapDeviceKeyboard.py`** file.  Keyboards could potentially have their own mappings...  we'll revisit this at another time.



---------------
## 2025.11.15 📢
---------------

- 📊/✍/🖥️/⌨ *(status/design/gui/keyboard)* so after much thought about it, [@G-0-R-D](https://github.com/G-0-R-D) has decided to ditch the traditional keyboard model, because developers only really have 2 concerns with the keyboard:

		1. which physical/logical key(s) are pressed?
		2. which text is coming in?

	SDL has already gone towards a text event keyboard model.  Qt is doing this too.  UQ will follow suit.  The keyboard will have logical keys, and a text event channel for all text inputs.  Shift key mapping will no longer be represented in the application (although it would still be possible to track the physical keys and map that to a keyboard state if that information is important for your project, you'd just have to do it yourself).  Keys will be identified strictly by name, scancodes will be entirely disregarded.  Hopefully this proves to be a good decision to future-proof the code as well!

	
- 🫧/🤖/🚛 *(housekeeping/programming/moved)* **`UQ/snap/programming/compiling/`** renamed the opcode-based compiler and interpreter to namespace 'User' to try to disambiguate better from the 'Internal' compiler.



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

	
