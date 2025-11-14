
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

- General practice is to put the `ENV.__build__()` commands into `__init__.py` files, so we can just import packages by building the folder containing the `__init__.py` file...

- `ENV.__build__('path.to.module')` calls the `def build(ENV)` function in 'module'

