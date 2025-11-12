
---
### 2025.11.11 📢
---

### ❗ Refactoring
- *(programming)* re-organized compiler code for the SnapInternalCompiler, going with a design that should be more future-proof and make it easier for subclasses to "opt-in" to operations instead of just inheriting them all...  also implemented using methods instead of conditionals, cleaner.

### 📝 Documentation
- *(pending)* in the process of creating README.md files in the directories of interest (graphics, programming, etc...) to go into detail instead of trying to cram everything in the main README.md

### 🧠 Learning
- *(housekeeping)* Learned how to make a nice changelog [https://github.com/orhun/git-cliff/blob/main/CHANGELOG.md]

#### 💡 WISHLIST / TODO / WIP
- *(graphics/text)* Accurate Glyph Metrics from Qt5 (I think I know of a way to do it...)
- *(gui)* window_event() for handling visibility and focus/HUD protocol as well as better camera control...
- *(gui/graphics)* making a new event and asset management system (which integrates with existing protocols), instead of having to make properties for every new renderable, or setup custom rendering config for each new SnapContainer -- will also handle 'layouts'
- *(graphics)* SnapContext will support context management with a ['subcontext'] property to easily do a local render and save/restore
>inspired by how qt5 does `with QPainter(self) as ptr: ...`
- *(graphics)* OpenGL (this would be my 5th(?) time wrapping it... shouldn't take too long once I start!
- *(stability/security)* ENV.QUIT channel for things like SnapSubprocess to listen to, protected by try/except (SystemExit, KeyboardInterrupt) so everything has a chance to shutdown properly and subprocesses aren't left hanging...
- *(gui/keyboard) gen a keymap for the default keyboard layout that is compatible with qt5 so keyboard events can be used...
- *(programming/core)* argspec parsing with parseq (and gui debugging for parseq)
- *(graphics/animation)* get the animation system working via ENV.ANIMATION.animate(...)

---
### 2025.11.10 📢
---

### 🧠 Learning
- *(git)* learned how to accept a pull request!

### 👑 New Contributors 🎖️
* **@Shmalikov** made *THE FIRST* contribution in [#1](https://github.com/G-0-R-D/UQ/pull/1)
