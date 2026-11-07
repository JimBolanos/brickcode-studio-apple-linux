# Pybricks Blocks

A visual block editor that writes Pybricks Python for the LEGO MINDSTORMS
EV3. Drag blocks, copy the Python, paste it into Pybricks.

Eleven categories: Setup first, then the ten of the NQC/NXC editor beside
it, in the MINDSTORMS Robot Inventor palette: Motors, Movement, Display,
Sound, Events, Control, Sensors, Operators, Variables and My Blocks.

## Set up

Devices are declared the way Pybricks' own editor does it. A **set up**
block holds one block per device, each with a name you choose:

```
set up
  EV3 brick named  ev3
  motor named      arm1   on port B
  touch sensor named touch on port S1
  drive base named robot  left motor arm1  right motor arm2 ...
```

Every other block then picks a device from a list of those names, so
`arm1.run_angle(...)` reads as what it does and two motors of the same kind
cannot be mixed up. The Setup category has the EV3 sensors (touch, colour,
gyro, ultrasonic, infrared) and the NXT ones (touch, light, colour, sound,
ultrasonic), a motor, a drive base, a car and the brick.

- Rename a device and every block that picked it follows.
- Names are unique and cannot be a Python or Pybricks word; the field
  refuses them.
- A block pointing at a missing device, two devices on one port or two with
  one name get a warning triangle, and the file says so with an
  `# ERROR:` line at the top.
- The brick is the one device that may be left out: if a block needs it and
  none is set up, `ev3 = EV3Brick()` is added.
- The NXT touch, colour and ultrasonic sensors share their names with the
  EV3 ones, so they are imported as `NXTTouchSensor` and so on and both
  kinds can sit in one program.
- Devices are written at the top in a fixed order (brick, motors, sensors,
  drive bases) wherever the blocks sit on the page, so a drive base always
  comes after its motors.

The signatures come from
[pybricks/pybricks-api](https://github.com/pybricks/pybricks-api), not from
the rendered documentation. They disagree in places: the v2 docs say the
gyro takes `positive_direction`, and the API source says `direction`.

`pybricks-blocks.html` is one self-contained file: Blockly and every style
are inlined, so it works from `file://` with no network and no account.

## Where the code goes

The EV3 is not supported by **code.pybricks.com**. Two routes work:

- **labs.pybricks.com**, the beta site, with the EV3 firmware installed,
  connected over USB. This is where Pybricks' own EV3 support lives, and
  its maintainers describe it as not yet ready for casual use.
- **ev3dev**, the older route: save the program as `main.py` on the brick's
  SD card image and run it there.

The generated program suits both, because for motors the two APIs are the
same call for call — `run_angle(speed, rotation_angle, then, wait)` either
way, in °/s, degrees and milliseconds.

## Why there are stub modules

The RCX and NXT editors are kept honest by their compilers: every generated
program goes through the real `nqc` or `nbc`, and the test fails if no
`.rcx` or `.rxe` comes out. That is what caught `OUT_A + OUT_C`, which
compiles cleanly and drives the wrong motor on an NXT.

Pybricks has no compiler, so `test/stubs/pybricks/` is the substitute: fake
`ev3devices`, `parameters` and `tools` modules that check their own
arguments and record every call. Generated programs are parsed and then
**run** against them, and the test compares what the motor actually
received. A wrong method name, a missing argument or a value out of range
fails there.

```
cd test
python3 gen.py
```

Needs playwright with chromium. Each program runs in a subprocess, so one
that loops forever cannot take the suite with it.

## Building

```
python3 build.py
```

Inlines `blockly.min.js` and the icon sprite into `index.html` to produce
`pybricks-blocks.html`. Edit `index.html`, never the built file.

## What is deliberately missing

`speaker.say()` and `speaker.set_volume()` exist on the ev3dev build and not
on the newer firmware, so they are left out: everything the editor writes
runs on both. That is also why the motor blocks were easy — for motors the
two APIs are the same call for call.

Not yet: the infrared beacon and remote, `draw_image`, fonts, `StopWatch`,
the `arc` and `move_by` moves a drive base can do, the NXT temperature,
energy-meter and Vernier sensors, and NXT motors.

Blockly 13.4.0, Apache 2.0.
