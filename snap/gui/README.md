
- `SnapContainer.device_event()` should return True to accept the event, otherwise it will be propagated to the parent (if applicable, depends on event behaviour -- proximity events are always sent to all for example)

#### TODO

- Would like to actually remove the Qt backend and do something more direct but cross-platform, but have to research this...

#### `../snap/lib/os/devices/keymap`

- Needs to be figured out. I think identifying keys by name is preferable to the mess that codes are! But still the names would need to be mapped from the GUI lib or OS! Every GUI seems to have a completely different set of keycodes... help!


