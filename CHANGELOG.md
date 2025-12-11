
---------------
### 📌 Pinned
---------------

### 💡 Wishlist / 🕒 TODO / 🛠️ WIP
- 🖥️ *(gui)* `SnapContainer.window_event()` for handling visibility and focus/HUD protocol as well as better camera control...
		
- 🖥️/🎨 *(gui/graphics)* making a new event and asset management system (which integrates with existing protocols), instead of having to make properties for every new renderable, or setup custom rendering config for each new SnapContainer -- will also handle 'layouts'
		
- 🎨 *(graphics)* SnapContext will support context management with a ['subcontext'] property to easily do a local render and save/restore (inspired by how qt5 does `with QPainter(self) as ptr: ...`)
		
- 🤖 *(programming)* argspec parsing with parseq (and gui debugging for parseq)
		
- 🎨/📽 *(graphics/animation)* get the animation system working via `ENV.ANIMATION.animate(...)`

	
---------------


---------------
## 2025.12.10 📢
---------------

- 🎧/💪 *(audio/finished)* not gonna lie, been struggling (very part-time) to get proper audio playback from Qt5.  Works but still more to do on it.

	
- 🏁/❗/💎 *(performance/refactoring/core)* got a performance boost by changing the `SnapNode.__getitem__` api to access the class properties instead of bound properties



---------------
## 2025.12.03 📢
---------------

- 🛠️/📺/🎧 *(WIP/media/audio)* using qt5 for audio playback (since we're already using it anyway) in **`..UQ/snap/media/SnapAudio.py`**

	
- 📌/💪/🧱/🔒 *(pinned/finished/stability/security)* ENV.QUIT channel for things like SnapSubprocess to listen to...  just do `ENV.QUIT.listen(self.__delete__)` to ensure a proper (and timely) cleanup.



---------------
## 2025.12.02 📢
---------------

- 💪/🎨 *(finished/graphics)* ShaderToy is starting to take shape!  check out **`../UQ/demo/snap/graphics/opengl/shadertoy/ShaderToy.py`**

	
- 🚛 *(moved)*  Rhobidium ShaderToy to proper Rhodium.py name (but it will be integrated into the ShaderToy app once multi-buffers are supported)

	
- 📢 *(announcement)* sorry for the delay in updates, was trying to get the shadertoy app to function at a basic level and have had very little time to work on it!  [@G-0-R-D](https://github.com/G-0-R-D) will try to be more consistent with smaller updates going forward!



---------------
## 2025.11.28 📢
---------------

- 📌/💪/🎨 *(pinned/done/graphics)* After a good nights sleep and a bit of thought, [@G-0-R-D](https://github.com/G-0-R-D) did just a little reconfiguring of the rendering system and now we have toplevel OpenGL rendering (without a blit!) and a single OpenGL context used by all!  The answer was to re-use the initial Qt5 OpenGL window for primary OpenGL rendering, and subsequent windows will just be regular QWidgets that would blit from OpenGL into QImage format for their display (so we always have only one OpenGL window / context globally).

	Still more work to do, but check out **`../UQ/demo/snap/graphics/opengl/shadertoy/Rhobidium.py`** now! :)



---------------
## 2025.11.26 📢
---------------

- 📌/💪/🎨 *(pinned/done/graphics)* OpenGL is being marked as complete.  It'll keep getting worked on, but it's not the priority right now.  Top-level gui opengl rendering is aborted, since Qt attempts to do 'smart' context switching (despite being told not to with AA_ShareOpenGLContexts!), and the design of snap was to only have 1 opengl context so it would require a complete redesign to do anything else.  Rather than try to muck around with it, we'll just init one OpenGL context with a hidden Qt window and just blit the GPU image to the CPU and accept the cost for the simplicity!  This may be revisited later.



---------------
## 2025.11.25 📢
---------------

- 🛠️/🎨 *(WIP/graphics)* struggling to get opengl blit to work with Qt5, but pushing the changes anyway cause it has been awhile and a lot has been changed.  Just enable the 'USING_OPENGL' variable in **`../UQ/snap/gui/Qt5/SnapQt5.py`** if you want to tinker with the blit

	
- 🐛 *(bug)* window with opengl is a bit more stable now, but it crashes if the window is resized to a smaller size... (but not a bigger one...) it probably has something to do with the way framebuffers are being rapidly created and destroyed in the context currently XD, will get to it when I find the time!  If anyone finds any fixes for any problems please do let [@G-0-R-D](https://github.com/G-0-R-D) know!  Thanks! :)



---------------
## 2025.11.24 📢
---------------

- ✨/🎪 *(new/demo)* making tutorials as demos (just to get started), like: **`UQ/demo/snap/tutorial/core/basics_of_snap_protocol.py`**

	
- 🛠️/🎨/🧠 *(WIP/graphics/learning)* figured out how to setup the opengl gui context using Qt



---------------
## 2025.11.22 📢
---------------

- 🎨/✨/🎪 *(graphics/new/demo)* **`UQ/demo/snap/graphics/opengl/shadertoy/Rhobidium.py`** now runs...  but still lots to do!

	
- 🛠️/⚠️/❗ *(WIP/major/refactoring)* currently working on a redesign of the core, but hopefully it doesn't impact existing code too much...



---------------
## 2025.11.20 📢
---------------

- 🎨/✨ *(graphics/new)* new opengl obj reader (untested)



---------------
## 2025.11.19 📢
---------------

- 📊 *(progress)* working on opengl, image can open and save now

	
- 🧠/😺 *(learning/git)* [@G-0-R-D](https://github.com/G-0-R-D) should be able to do a merge with conflicts now...



---------------
## 2025.11.18 📢
---------------

- 🛠️ *(WIP)* working on OpenGL, brought some old code in, but it doesn't work yet...

	
* 👑 *(contributor)* [@Shmalikov](https://github.com/Shmalikov) made another contribution in [[#2](https://github.com/G-0-R-D/UQ/pull/2)]



---------------
## 2025.11.17 📢
---------------

- 🖥️/🎨/✍ *(gui/graphics/design)* event and asset managers can be easily implemented using python properties, which create the instance locally if it doesn't exist, then return it...  simple!  (was going to do something much more complex with decorators!)



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

	
