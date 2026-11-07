#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nothing the generator writes is taken on trust.

For the RCX and NXT editors every generated program goes through the real
nqc or nbc, and the test fails if no .rcx or .rxe comes out. Pybricks has
no compiler, so this does the nearest thing that still bites: each program
is parsed, then executed against stub pybricks modules that check their
own arguments and record every call. A wrong method name, a missing
argument or a value out of range fails here.

Devices are declared the way Pybricks does it, in a "set up" block with a
name each; every other block picks a device by that name.
"""

import json
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = "file://" + os.path.join(os.path.dirname(HERE), "pybricks-blocks.html")
RUNNER = os.path.join(HERE, "run_program.py")

bad = 0
HEAD = '<xml xmlns="https://developers.google.com/blockly/xml">'


def dev(kind, name, port=None, **fields):
    s = '<block type="pb_dev_%s"><field name="NAME">%s</field>' % (kind, name)
    if port:
        s += '<field name="PORT">%s</field>' % port
    for k, v in fields.items():
        s += '<field name="%s">%s</field>' % (k, v)
    return s + "%s</block>"


def setup(*devs, y=30):
    """A set-up block holding these devices, chained with <next>."""
    chain = ""
    for d in reversed(devs):
        chain = d % ("<next>%s</next>" % chain if chain else "")
    return ('<block type="pb_setup" x="30" y="%d"><statement name="DO">%s'
            "</statement></block>" % (y, chain)) if devs else ""


def program(body, y=30):
    return ('<block type="pb_program" x="30" y="%d"><statement name="DO">%s'
            "</statement></block>" % (y, body))


def xml(body, devs=(), setup_first=True):
    if setup_first:
        return HEAD + setup(*devs, y=30) + program(body, y=420) + "</xml>"
    # the program above its set up on the page: the declarations still have
    # to come out first in the file
    return HEAD + program(body, y=30) + setup(*devs, y=420) + "</xml>"


def n(v):
    return '<shadow type="pb_number"><field name="NUM">%s</field></shadow>' % v


def blk(t, fields=None, values=None, nxt=None):
    s = '<block type="%s">' % t
    for k, v in (fields or {}).items():
        s += '<field name="%s">%s</field>' % (k, v)
    for k, v in (values or {}).items():
        s += '<value name="%s">%s</value>' % (k, n(v))
    if nxt:
        s += "<next>%s</next>" % nxt
    return s + "</block>"


def pr(value_block):
    """screen.print of a value block, to read a sensor and log the call."""
    return ('<block type="pb_screen_print"><value name="WHAT">%s</value>'
            "</block>" % value_block)


def chain(*blocks):
    """Statement blocks one after another."""
    out = ""
    for b in reversed(blocks):
        out = (b[:-len("</block>")] + "<next>%s</next></block>" % out) \
            if out else b
    return out


def run(source):
    p = subprocess.run([sys.executable, RUNNER], input=source, text=True,
                       capture_output=True, timeout=20)
    if p.returncode != 0:
        return {"ok": False, "where": "runner", "error": p.stderr.strip()[:200]}
    return json.loads(p.stdout)


MOTOR_B = [dev("motor", "arm", "B")]

# Each case: a name, the devices, the blocks, and the calls the stubs must
# actually see. Devices are built in a fixed order (brick, motors, EV3
# sensors, NXT sensors, drive bases), whatever order they sit in.
CASES = [
    ("run_angle", MOTOR_B,
     blk("pb_run_angle", {"DEV": "arm", "THEN": "HOLD"},
         {"ANGLE": 90, "SPEED": 360}),
     [["Motor", "B"], ["run_angle", "B", 360, 90, "Stop.HOLD"]]),

    ("run_time", [dev("motor", "wheel", "A")],
     blk("pb_run_time", {"DEV": "wheel", "THEN": "BRAKE"},
         {"SPEED": 500, "TIME": 2000}),
     [["Motor", "A"], ["run_time", "A", 500, 2000, "Stop.BRAKE"]]),

    ("run_target", [dev("motor", "lift", "C")],
     blk("pb_run_target", {"DEV": "lift", "THEN": "COAST"},
         {"TARGET": -180, "SPEED": 200}),
     [["Motor", "C"], ["run_target", "C", 200, -180, "Stop.COAST"]]),

    ("run forever", [dev("motor", "fan", "D")],
     blk("pb_run", {"DEV": "fan"}, {"SPEED": 720}),
     [["Motor", "D"], ["run", "D", 720]]),

    ("dc", [dev("motor", "fan", "A")],
     blk("pb_dc", {"DEV": "fan"}, {"DUTY": -60}),
     [["Motor", "A"], ["dc", "A", -60]]),

    ("stop / brake / hold", [dev("motor", "fan", "A")],
     blk("pb_stop", {"DEV": "fan", "HOW": "stop"},
         nxt=blk("pb_stop", {"DEV": "fan", "HOW": "brake"},
                 nxt=blk("pb_stop", {"DEV": "fan", "HOW": "hold"}))),
     [["Motor", "A"], ["stop", "A"], ["brake", "A"], ["hold", "A"]]),

    ("reset_angle then wait", MOTOR_B,
     blk("pb_reset_angle", {"DEV": "arm"}, {"ANGLE": 0},
         nxt=blk("pb_wait", values={"MS": 250})),
     [["Motor", "B"], ["reset_angle", "B", 0], ["wait", 250]]),

    ("until stalled", [dev("motor", "arm", "C")],
     blk("pb_run_until_stalled", {"DEV": "arm", "THEN": "COAST"}, {"SPEED": 150}),
     [["Motor", "C"], ["run_until_stalled", "C", 150, "Stop.COAST"]]),

    # Two motors: the point of naming them. Each call has to reach the
    # motor its block names, not the other one.
    ("two motors", [dev("motor", "head", "A"), dev("motor", "arm", "C")],
     blk("pb_run", {"DEV": "arm"}, {"SPEED": 300},
         nxt=blk("pb_run", {"DEV": "head"}, {"SPEED": 100},
                 nxt=blk("pb_stop", {"DEV": "arm", "HOW": "brake"}))),
     [["Motor", "A"], ["Motor", "C"], ["run", "C", 300], ["run", "A", 100],
      ["brake", "C"]]),

    # The loop has to indent, which in Python is the structure itself.
    ("repeat 3", [dev("motor", "arm", "A")],
     '<block type="pb_repeat">'
     '<value name="TIMES">%s</value><statement name="DO">%s</statement>'
     "</block>" % (n(3), blk("pb_run_angle", {"DEV": "arm", "THEN": "HOLD"},
                             {"ANGLE": 45, "SPEED": 180})),
     [["Motor", "A"]] + [["run_angle", "A", 180, 45, "Stop.HOLD"]] * 3),

    # ------------------------------------------- NXT-style motor blocks
    # No Set up: the motor is chosen by its port and declared for you.
    ("motor run for seconds", [],
     blk("pb_motor_for", {"PORT": "B", "UNIT": "SEC"}, {"AMT": 2, "PCT": 75}),
     [["Motor", "B"], ["run_time", "B", 750, 2000, "Stop.HOLD"]]),

    ("motor run for rotations", [],
     blk("pb_motor_for", {"PORT": "A", "UNIT": "ROT"}, {"AMT": 2, "PCT": 50}),
     [["Motor", "A"], ["run_angle", "A", 500, 720, "Stop.HOLD"]]),

    ("motor run for degrees, backwards", [],
     blk("pb_motor_for", {"PORT": "C", "UNIT": "DEG"}, {"AMT": 90, "PCT": -50}),
     [["Motor", "C"], ["run_angle", "C", 500, -90, "Stop.HOLD"]]),

    ("start motor, stop, reset, count", [],
     blk("pb_motor_on", {"PORT": "B"}, {"PCT": 100},
         nxt=blk("pb_m_stop", {"PORT": "B", "HOW": "brake"},
                 nxt=blk("pb_motor_reset", {"PORT": "B"},
                         nxt=pr(blk("pb_m_angle", {"PORT": "B"}))))),
     [["EV3Brick"], ["Motor", "B"], ["run", "B", 1000], ["brake", "B"],
      ["reset_angle", "B", 0], ["angle", "B"], ["screen_print", "0"]]),

    ("motor 0 percent is stop", [],
     blk("pb_motor_for", {"PORT": "B", "UNIT": "SEC"}, {"AMT": 2, "PCT": 0}),
     [["Motor", "B"], ["stop", "B"]]),

    ("stop all, reset all", [],
     blk("pb_motor_on", {"PORT": "A"}, {"PCT": 10},
         nxt=blk("pb_motor_on", {"PORT": "C"}, {"PCT": 10},
                 nxt=blk("pb_m_stop_all", nxt=blk("pb_m_reset_all")))),
     [["Motor", "A"], ["Motor", "C"], ["run", "A", 100], ["run", "C", 100],
      ["stop", "A"], ["stop", "C"], ["reset_angle", "A", 0],
      ["reset_angle", "C", 0]]),

    # A motor that Set up already has on that port keeps its own name and
    # is not made twice.
    ("port uses the motor from Set up", [dev("motor", "arm", "B")],
     blk("pb_motor_on", {"PORT": "B"}, {"PCT": 75}),
     [["Motor", "B"], ["run", "B", 750]]),

    # ------------------------------------ the two-wheel robot
    # the speed is set once, by its own block, and used by the others
    ("set movement speed, then move", [],
     blk("pb_move_speed", values={"PCT": 80},
         nxt=blk("pb_go_for", {"DIR": "FWD", "UNIT": "SEC"}, {"AMT": 2},
                 nxt=blk("pb_spin_for", {"SIDE": "R", "UNIT": "DEG"}, {"AMT": 90},
                         nxt=blk("pb_go_start", {"DIR": "REV"},
                                 nxt=blk("pb_move_stop"))))),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive", 400, 0], ["wait", 2000], ["drive_brake"],
      ["drive_settings", None, None, 240, None], ["turn", 90, "Stop.HOLD"],
      ["drive", -400, 0], ["drive_brake"]]),

    ("movement without a speed block uses 50 %", [],
     blk("pb_go_for", {"DIR": "REV", "UNIT": "ROT"}, {"AMT": 1},
         nxt=blk("pb_spin_for", {"SIDE": "L", "UNIT": "SEC"}, {"AMT": 1})),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive_settings", 250, None, None, None], ["straight", -176, "Stop.HOLD"],
      ["drive", 0, -150], ["wait", 1000], ["drive_brake"]]),

    ("move for seconds", [],
     blk("pb_move_for", {"DIR": "FWD", "UNIT": "SEC"}, {"AMT": 1, "PCT": 75}),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive", 375, 0], ["wait", 1000], ["drive_brake"]]),

    # A+D, the kit's 56 mm wheels: one rotation is 175.93 mm
    ("set movement motors, rotations backwards", [],
     blk("pb_base_set", {"PAIR": "AD"},
         nxt=blk("pb_move_for", {"DIR": "REV", "UNIT": "ROT"},
                 {"AMT": 1, "PCT": 50})),
     [["Motor", "A"], ["Motor", "D"], ["DriveBase", "A", "D", 56, 114],
      ["drive_settings", 250, None, None, None], ["straight", -176, "Stop.HOLD"]]),

    ("turn right for seconds, left for degrees", [],
     blk("pb_turn_for", {"SIDE": "R", "UNIT": "SEC"}, {"AMT": 2, "PCT": 50},
         nxt=blk("pb_turn_for", {"SIDE": "L", "UNIT": "DEG"},
                 {"AMT": 90, "PCT": 50})),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive", 0, 150], ["wait", 2000], ["drive_brake"],
      ["drive_settings", None, None, 150, None], ["turn", -90, "Stop.HOLD"]]),

    ("start moving backwards, stop moving", [],
     blk("pb_move_start", {"DIR": "REV"}, {"PCT": 40},
         nxt=blk("pb_move_stop")),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive", -200, 0], ["drive_brake"]]),

    # tank runs the two wheel motors directly, no drive base
    ("tank", [],
     blk("pb_tank", values={"L": 50, "R": -30}),
     [["Motor", "B"], ["Motor", "C"], ["run", "B", 500], ["run", "C", -300]]),

    # The drive base declared in Set up is the robot the movement blocks
    # drive: no second one is made, and its name is used.
    ("movement uses the Set up drive base",
     [dev("motor", "left", "B"), dev("motor", "right", "C"),
      dev("drive", "chassis", LEFT="left", RIGHT="right")],
     blk("pb_move_for", {"DIR": "FWD", "UNIT": "ROT"}, {"AMT": 1, "PCT": 50},
         nxt=blk("pb_move_stop")),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive_settings", 250, None, None, None], ["straight", 176, "Stop.HOLD"],
      ["drive_brake"]]),

    ("tank on the Set up drive base motors",
     [dev("motor", "left", "A"), dev("motor", "right", "D"),
      dev("drive", "chassis", LEFT="left", RIGHT="right")],
     blk("pb_tank", values={"L": 20, "R": 40}),
     [["Motor", "A"], ["Motor", "D"], ["DriveBase", "A", "D", 56, 114],
      ["run", "A", 200], ["run", "D", 400]]),

    ("track target", [dev("motor", "arm", "A")],
     blk("pb_track_target", {"DEV": "arm"}, {"TARGET": 90}),
     [["Motor", "A"], ["track_target", "A", 90]]),

    ("motor configure", [dev("motor", "arm", "A")],
     blk("pb_motor_config", {"DEV": "arm", "WHAT": "acceleration"}, {"VAL": 2000},
         nxt=blk("pb_motor_config", {"DEV": "arm", "WHAT": "speed"}, {"VAL": 800})),
     [["Motor", "A"], ["limits", "A", None, 2000, None],
      ["limits", "A", 800, None, None]]),

    # ---------------------------------------------------------- Movement
    ("drive base configure",
     [dev("motor", "left", "B"), dev("motor", "right", "C"),
      dev("drive", "robot", LEFT="left", RIGHT="right")],
     blk("pb_drive_config", {"DEV": "robot", "WHAT": "straight_speed"}, {"VAL": 200},
         nxt=blk("pb_drive_config", {"DEV": "robot", "WHAT": "turn_rate"}, {"VAL": 90},
                 nxt=blk("pb_drive", {"DEV": "robot"}, {"SPEED": 100, "RATE": 0},
                         nxt=blk("pb_drive_stop", {"DEV": "robot", "HOW": "stop"})))),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["drive_settings", 200, None, None, None],
      ["drive_settings", None, None, 90, None],
      ["drive", 100, 0], ["drive_stop"]]),

    ("car",
     [dev("motor", "steering", "A"), dev("motor", "wheels", "B"),
      dev("car", "car", STEER="steering", DRIVE="wheels")],
     blk("pb_car_drive", {"DEV": "car", "WHAT": "drive_power"}, {"VAL": 50},
         nxt=blk("pb_car_steer", {"DEV": "car"}, {"PCT": -30},
                 nxt=blk("pb_car_drive", {"DEV": "car", "WHAT": "drive_speed"}, {"VAL": 360}))),
     [["Motor", "A"], ["Motor", "B"], ["Car", "A", "B"],
      ["car_power", 50], ["car_steer", -30], ["car_speed", 360]]),

    ("drive base",
     [dev("motor", "left", "B"), dev("motor", "right", "C"),
      dev("drive", "robot", LEFT="left", RIGHT="right")],
     blk("pb_straight", {"DEV": "robot", "THEN": "HOLD"}, {"DIST": 200},
         nxt=blk("pb_turn", {"DEV": "robot", "THEN": "BRAKE"}, {"ANGLE": -90},
                 nxt=blk("pb_drive_stop", {"DEV": "robot", "HOW": "brake"}))),
     [["Motor", "B"], ["Motor", "C"], ["DriveBase", "B", "C", 56, 114],
      ["straight", 200, "Stop.HOLD"], ["turn", -90, "Stop.BRAKE"],
      ["drive_brake"]]),

    # The drive base is written after its motors even when the block was
    # dragged out first. The motors keep the order they were set up in.
    ("drive above motors",
     [dev("drive", "robot", LEFT="l", RIGHT="r"),
      dev("motor", "r", "C"), dev("motor", "l", "B")],
     blk("pb_drive", {"DEV": "robot"}, {"SPEED": 100, "RATE": 0}),
     [["Motor", "C"], ["Motor", "B"], ["DriveBase", "B", "C", 56, 114],
      ["drive", 100, 0]]),

    # ----------------------------------------------------------- Display
    ("screen and light", [dev("brick", "ev3")],
     blk("pb_screen_clear",
         nxt=blk("pb_screen_text", values={"X": 10, "Y": 50},
                 nxt=blk("pb_screen_box", {"FILL": "TRUE"},
                         {"X1": 0, "Y1": 0, "X2": 40, "Y2": 30},
                         nxt=blk("pb_screen_circle", {"FILL": "FALSE"},
                                 {"X": 89, "Y": 64, "R": 20},
                                 nxt=blk("pb_light", {"COLOR": "ORANGE"}))))),
     [["EV3Brick"], ["screen_clear"], ["draw_text", 10, 50, ""],
      ["draw_box", 0, 0, 40, 30, True], ["draw_circle", 89, 64, 20, False],
      ["light_on", "Color.ORANGE"]]),

    # The one device that may be left out: a block needs the brick, there is
    # only one it can be, so it is added.
    ("brick not declared", [],
     blk("pb_screen_clear"),
     [["EV3Brick"], ["screen_clear"]]),

    # A brick with a name of its own is used under that name.
    ("brick renamed", [dev("brick", "brain")],
     blk("pb_screen_clear", nxt=blk("pb_beep", values={"FREQ": 500, "MS": 50})),
     [["EV3Brick"], ["screen_clear"], ["beep", 500, 50]]),

    # ------------------------------------------------------------- Sound
    ("sound", [dev("brick", "ev3")],
     blk("pb_volume", values={"VOL": 60},
         nxt=blk("pb_beep", values={"FREQ": 800, "MS": 200},
                 nxt=blk("pb_notes", {"NOTES": "C4/4 E4/4 G4/2"},
                         {"TEMPO": 120}))),
     [["EV3Brick"], ["volume", 60], ["beep", 800, 200],
      ["play_notes", ["C4/4", "E4/4", "G4/2"], 120]]),

    ("dot", [dev("brick", "ev3")],
     blk("pb_screen_pixel", values={"X": 20, "Y": 30}),
     [["EV3Brick"], ["draw_pixel", 20, 30]]),

    # ----------------------------------------------------------- Sensors
    ("sensors read", [dev("brick", "ev3"), dev("gyro", "spin", "S2")],
     blk("pb_gyro_reset", {"DEV": "spin"}, {"ANGLE": 0},
         nxt=blk("pb_screen_print")),
     [["EV3Brick"], ["GyroSensor", "S2"], ["gyro_reset", "S2", 0],
      ["screen_print", ""]]),

    ("EV3 sensors",
     [dev("brick", "ev3"), dev("touch", "bumper", "S1"),
      dev("color", "floor", "S3"), dev("ultra", "eyes", "S4"),
      dev("infra", "ir", "S2")],
     chain(pr(blk("pb_touch", {"DEV": "bumper"})),
           pr(blk("pb_reflection", {"DEV": "floor"})),
           pr(blk("pb_ambient", {"DEV": "floor"})),
           pr(blk("pb_ultra", {"DEV": "eyes"})),
           pr(blk("pb_infra", {"DEV": "ir"}))),
     [["EV3Brick"], ["TouchSensor", "S1"], ["ColorSensor", "S3"],
      ["UltrasonicSensor", "S4"], ["InfraredSensor", "S2"],
      ["pressed", "S1"], ["screen_print", "False"],
      ["reflection", "S3"], ["screen_print", "0"],
      ["ambient", "S3"], ["screen_print", "0"],
      ["distance", "S4"], ["screen_print", "0"],
      ["ir_distance", "S2"], ["screen_print", "0"]]),

    # The NXT sensors come from pybricks.nxtdevices. The touch, colour and
    # ultrasonic ones share names with the EV3 ones, so one program that has
    # both only works if each is imported under its own name.
    ("NXT sensors",
     [dev("brick", "ev3"), dev("ntouch", "nbump", "S1"),
      dev("nlight", "line", "S2"), dev("nsound", "mic", "S3"),
      dev("nultra", "sonar", "S4")],
     chain(pr(blk("pb_touch", {"DEV": "nbump"})),
           pr(blk("pb_reflection", {"DEV": "line"})),
           pr(blk("pb_ambient", {"DEV": "line"})),
           pr(blk("pb_sound_level", {"DEV": "mic"})),
           pr(blk("pb_ultra", {"DEV": "sonar"}))),
     [["EV3Brick"], ["NXTTouchSensor", "S1"], ["NXTLightSensor", "S2"],
      ["NXTSoundSensor", "S3"], ["NXTUltrasonicSensor", "S4"],
      ["nxt_pressed", "S1"], ["screen_print", "False"],
      ["nxt_reflection", "S2"], ["screen_print", "0"],
      ["nxt_ambient", "S2"], ["screen_print", "0"],
      ["nxt_intensity", "S3"], ["screen_print", "0"],
      ["nxt_distance", "S4"], ["screen_print", "0"]]),

    ("NXT colour sensor", [dev("brick", "ev3"), dev("ncolor", "paint", "S1")],
     chain(pr(blk("pb_color", {"DEV": "paint", "COLOR": "RED"})),
           pr(blk("pb_reflection", {"DEV": "paint"}))),
     [["EV3Brick"], ["NXTColorSensor", "S1"],
      ["nxt_color", "S1"], ["screen_print", "False"],
      ["nxt_color_reflection", "S1"], ["screen_print", "0"]]),

    ("colour sensor red green blue",
     [dev("brick", "ev3"), dev("color", "floor", "S3"),
      dev("ncolor", "paint", "S1")],
     chain(pr(blk("pb_rgb", {"DEV": "floor", "CH": "0"})),
           pr(blk("pb_rgb", {"DEV": "floor", "CH": "2"})),
           pr(blk("pb_rgb", {"DEV": "paint", "CH": "1"}))),
     [["EV3Brick"], ["ColorSensor", "S3"], ["NXTColorSensor", "S1"],
      ["rgb", "S3"], ["screen_print", "0"],
      ["rgb", "S3"], ["screen_print", "0"],
      ["nxt_rgb", "S1"], ["screen_print", "0"]]),

    ("EV3 and NXT touch together",
     [dev("brick", "ev3"), dev("touch", "front", "S1"),
      dev("ntouch", "back", "S2")],
     chain(pr(blk("pb_touch", {"DEV": "front"})),
           pr(blk("pb_touch", {"DEV": "back"}))),
     [["EV3Brick"], ["TouchSensor", "S1"], ["NXTTouchSensor", "S2"],
      ["pressed", "S1"], ["screen_print", "False"],
      ["nxt_pressed", "S2"], ["screen_print", "False"]]),
]


# Programs that never end, or that depend on a button nobody can press.
# Running these against the stubs would hang, so the source is read instead.
# (name, devices, body, must contain, must not contain)
TEXT_CASES = [
    # A sum in the speed stays a sum, without doubled brackets.
    ("speed from a sum", [],
     '<block type="pb_motor_on"><field name="PORT">B</field><value name="PCT">'
     '<block type="pb_arith"><field name="OP">+</field><value name="A">%s</value>'
     '<value name="B">%s</value></block></value></block>' % (n(50), n(25)),
     ["motor_b.run((50 + 25) * 10)"], ["((50 + 25))"]),

    # A motor can be declared turning the other way round, as in Pybricks.
    ("motor with forward counterclockwise",
     [dev("motor", "arm", "A", DIRN="COUNTERCLOCKWISE"), dev("motor", "leg", "B")],
     blk("pb_motor_on", {"PORT": "A"}, {"PCT": 50}),
     ["arm = Motor(Port.A, Direction.COUNTERCLOCKWISE)", "leg = Motor(Port.B)",
      "import Port, Direction", "arm.run(500)"], ["motor_a"]),

    ("print in the terminal", [],
     '<block type="pb_print_term"><value name="WHAT"><shadow type="pb_text">'
     '<field name="TEXT">abc</field></shadow></value></block>',
     ['print("abc")'], ["EV3Brick", "screen"]),

    ("speed shown as a name", [],
     blk("pb_move_speed", values={"PCT": 80},
         nxt=blk("pb_go_start", {"DIR": "FWD"}, nxt=blk("pb_go_start", {"DIR": "REV"}))),
     ["move_speed = 50", "move_speed = 80", "robot.drive(move_speed * 5, 0)",
      "robot.drive(-move_speed * 5, 0)", "wheel_diameter=56, axle_track=114"], []),

    ("no speed block, no variable", [],
     blk("pb_go_start", {"DIR": "FWD"}),
     ["robot.drive(250, 0)"], ["move_speed"]),

    ("wait in seconds", [],
     blk("pb_wait_s", values={"SEC": 2}, nxt=blk("pb_wait_s", values={"SEC": 0.5})),
     ["wait(2000)", "wait(500)", "from pybricks.tools import wait"], ["wait(2)", "wait(0.5)"]),

    ("wait from a variable", [],
     '<block type="pb_wait_s"><value name="SEC"><block type="pb_arith">'
     '<field name="OP">+</field><value name="A">%s</value><value name="B">%s</value>'
     '</block></value></block>' % (n(1), n(2)),
     ["wait((1 + 2) * 1000)"], ["wait(1 + 2 * 1000)"]),

    ("forever", [],
     '<block type="pb_forever"><statement name="DO">%s</statement></block>'
     % blk("pb_wait", values={"MS": 100}),
     ["while True:", "    wait(100)"], []),

    ("wait until touch", [dev("touch", "bumper", "S1")],
     blk("pb_wait_until").replace(
         "</block>", '<value name="COND">%s</value></block>'
         % blk("pb_touch", {"DEV": "bumper"})),
     ["while not (bumper.pressed()):", "wait(10)",
      "bumper = TouchSensor(Port.S1)"], []),

    ("brick button", [],
     '<block type="pb_if"><value name="COND">%s</value>'
     '<statement name="DO">%s</statement></block>'
     % (blk("pb_button", {"BTN": "CENTER"}), blk("pb_exit")),
     ["if (Button.CENTER in ev3.buttons.pressed()):", "raise SystemExit",
      "import Port, Button", "ev3 = EV3Brick()"], []),

    ("brick button, renamed", [dev("brick", "brain")],
     '<block type="pb_if"><value name="COND">%s</value>'
     '<statement name="DO">%s</statement></block>'
     % (blk("pb_button", {"BTN": "LEFT"}), blk("pb_exit")),
     ["brain = EV3Brick()", "Button.LEFT in brain.buttons.pressed()"],
     ["ev3 ="]),

    # The section comments Pybricks itself writes.
    ("section comments", [dev("motor", "arm", "A")],
     blk("pb_run", {"DEV": "arm"}, {"SPEED": 100}),
     ["# Set up.\narm = Motor(Port.A)\n",
      "# The main program starts here.\narm.run(100)"],
     ["# ERROR"]),

    # NXT classes are imported under their own names.
    ("NXT import aliases",
     [dev("touch", "a", "S1"), dev("ntouch", "b", "S2")],
     blk("pb_wait", values={"MS": 1}),
     ["from pybricks.ev3devices import TouchSensor\n",
      "from pybricks.nxtdevices import TouchSensor as NXTTouchSensor\n",
      "a = TouchSensor(Port.S1)", "b = NXTTouchSensor(Port.S2)"], []),

    # ------------------------------------------- what the file must say
    ("two devices, one port",
     [dev("touch", "a", "S1"), dev("gyro", "b", "S1")],
     blk("pb_wait", values={"MS": 10}),
     ["# ERROR: port S1 is used by a and b."], []),

    # a motor on A and a sensor on S1 are different ports; nothing to say
    ("motor and sensor, no clash",
     [dev("motor", "m", "A"), dev("touch", "t", "S1")],
     blk("pb_wait", values={"MS": 10}),
     [], ["# ERROR"]),

    ("two devices, one name",
     [dev("motor", "x", "A"), dev("motor", "x", "B")],
     blk("pb_wait", values={"MS": 10}),
     ["# ERROR: two devices are called x."], []),

    ("name not in set up", MOTOR_B,
     blk("pb_run", {"DEV": "ghost"}, {"SPEED": 10}),
     ["# ERROR: ghost is not in Set up"], []),

    ("wrong kind of device", [dev("touch", "bumper", "S1")],
     blk("pb_run", {"DEV": "bumper"}, {"SPEED": 10}),
     ["# ERROR: bumper is not in Set up, or is the wrong kind"], []),

    ("no device picked", MOTOR_B,
     blk("pb_run", {"DEV": ""}, {"SPEED": 10}),
     ["# ERROR: a block has no device chosen"], []),

    ("car without motors",
     [dev("car", "car", STEER="a", DRIVE="b")],
     blk("pb_car_steer", {"DEV": "car"}, {"PCT": 0}),
     ["# ERROR: car car needs two motors that are in Set up."],
     ["Car(a, b"]),

    ("car, same motor twice",
     [dev("motor", "m", "A"), dev("car", "car", STEER="m", DRIVE="m")],
     blk("pb_car_steer", {"DEV": "car"}, {"PCT": 0}),
     ["# ERROR: car car needs two different motors."], []),

    ("drive base without motors",
     [dev("drive", "robot", LEFT="l", RIGHT="r")],
     blk("pb_straight", {"DEV": "robot", "THEN": "HOLD"}, {"DIST": 10}),
     ["# ERROR: drive base robot needs two motors that are in Set up."],
     ["DriveBase(l, r"]),

    ("drive base, same motor twice",
     [dev("motor", "m", "A"),
      dev("drive", "robot", LEFT="m", RIGHT="m")],
     blk("pb_straight", {"DEV": "robot", "THEN": "HOLD"}, {"DIST": 10}),
     ["# ERROR: drive base robot needs two different motors."], []),

    ("name Python would refuse", [dev("motor", "wait", "A")],
     blk("pb_wait", values={"MS": 10}),
     ["# ERROR: wait cannot be a device name"], []),

    ("two bricks", [dev("brick", "a"), dev("brick", "b")],
     blk("pb_wait", values={"MS": 10}),
     ["# ERROR: there is more than one EV3 brick"], []),
]


def main():
    global bad

    def fail(name, msg):
        global bad
        print("%-26s FALLO  %s" % (name, msg))
        bad += 1

    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page()
        page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:200]))
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")
        page.wait_for_timeout(250)

        def load(x):
            return page.evaluate("x => window.__load(x)", x)

        def rename(a, b):
            # typing in the field; Blockly delivers the change event on the
            # next tick, which is when every block that picks it follows
            page.evaluate("([a, b]) => window.__rename(a, b)", [a, b])
            page.wait_for_timeout(80)
            return page.evaluate("window.__code()")

        # ---- the page as it opens: the example must be clean
        src = page.evaluate("window.__code()")
        warns = page.evaluate("window.__warnings()")
        if "# ERROR" in src or warns:
            fail("example", "el ejemplo tiene errores: %s %s" % (warns, src))
        else:
            print("%-26s OK     sin errores ni avisos" % "example")

        for name, devs, body, want in CASES:
            src = load(xml(body, devs))
            r = run(src)
            if not r["ok"]:
                fail(name, "%s: %s" % (r["where"], r["error"]))
                print("".join("    " + l + "\n" for l in src.split("\n")))
                continue
            if "# ERROR" in src:
                fail(name, "el programa se declara con errores")
                print("".join("    " + l + "\n" for l in src.split("\n")))
                continue
            if r["log"] != want:
                fail(name, "los dispositivos recibieron otra cosa")
                print("   esperado: %s" % want)
                print("   recibido: %s" % r["log"])
                continue
            print("%-26s OK     %d llamadas" % (name, len(r["log"])))

        # ---- the same, with the program above its set up on the page
        name, devs, body, want = CASES[8]
        src = load(xml(body, devs, setup_first=False))
        r = run(src)
        if r["ok"] and r["log"] == want:
            print("%-26s OK     set up debajo del programa, sale arriba"
                  % "order on the page")
        else:
            fail("order on the page", r.get("error") or r.get("log"))

        # ---- things that cannot be run: with stubs they never finish ----
        for name, devs, body, want_in, want_out in TEXT_CASES:
            src = load(xml(body, devs))
            missing = [w for w in want_in if w not in src]
            present = [w for w in want_out if w in src]
            if missing or present:
                print("%-26s FALLO" % name)
                for w in missing:
                    print("   falta: %s" % w)
                for w in present:
                    print("   sobra: %s" % w)
                print("".join("    " + l + "\n" for l in src.split("\n")))
                bad += 1
            else:
                print("%-26s OK     revisado por texto" % name)

        # ---- the pictures: each one is run, rasterised and checked by pixel
        sys.path.insert(0, HERE)
        from raster import raster
        # (picture, [(x, y, black?)])  one point inside the shape, one outside
        PIX = {
            "happy":   [(89, 104, 1), (89, 90, 0), (66, 46, 1), (89, 40, 0)],
            "sad":     [(89, 88, 1), (89, 100, 0), (66, 52, 1), (89, 40, 0)],
            "serious": [(89, 92, 1), (89, 70, 0), (66, 50, 1), (112, 50, 1)],
            "open":    [(55, 64, 1), (55, 50, 0), (123, 64, 1), (89, 64, 0)],
            "closed":  [(55, 78, 1), (55, 64, 0), (123, 78, 1), (89, 70, 0)],
            "smile":   [(89, 94, 1), (89, 80, 0), (66, 50, 1), (89, 40, 0)],
            "wink":    [(66, 50, 1), (112, 50, 1), (112, 60, 0), (89, 94, 1)],
            "unsure":  [(66, 50, 1), (89, 94, 1), (89, 70, 0), (112, 50, 1)],
            "heart":   [(63, 48, 1), (89, 100, 1), (89, 26, 0), (20, 100, 0)],
            "heart_small": [(75, 54, 1), (89, 80, 1), (89, 34, 0), (30, 80, 0)],
            "zzz":     [(55, 16, 1), (55, 41, 1), (55, 66, 1), (30, 40, 0)],
            "bubble":  [(89, 11, 1), (89, 40, 0), (59, 48, 1), (16, 50, 1), (34, 100, 1), (89, 100, 0)],
            "thumbup": [(70, 40, 1), (22, 90, 1), (30, 40, 0), (120, 78, 0), (120, 70, 1)],
            "thumbdown": [(70, 88, 1), (22, 37, 1), (30, 88, 0), (120, 49, 0), (120, 56, 1)],
            "cross":   [(89, 64, 1), (89, 20, 0), (50, 64, 0), (60, 28, 1)],
            "check":   [(60, 98, 1), (110, 60, 1), (60, 60, 0), (130, 100, 0)],
            "question": [(89, 20, 1), (89, 42, 0), (89, 80, 1), (89, 110, 1), (60, 70, 0)],
            "stop":    [(89, 10, 1), (36, 12, 0), (89, 30, 0), (77, 64, 1), (89, 64, 0)],
            "teeth":   [(11, 60, 1), (89, 64, 1), (50, 48, 0), (64, 48, 1)],
            "teeth_small": [(31, 60, 1), (88, 52, 1), (79, 52, 0), (89, 64, 1)],
            "fangs":   [(36, 34, 1), (36, 64, 0), (49, 93, 1), (49, 66, 0), (89, 64, 0), (89, 10, 0)],
            "up":      [(89, 20, 1), (60, 20, 0), (89, 110, 1), (60, 110, 0)],
            "down":    [(89, 108, 1), (60, 108, 0), (89, 20, 1), (60, 20, 0)],
            "left":    [(20, 64, 1), (20, 20, 0), (150, 64, 1), (150, 20, 0)],
            "right":   [(158, 64, 1), (158, 20, 0), (30, 64, 1), (30, 20, 0)],
        }
        os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
        for pic, pts in PIX.items():
            body = blk("pb_picture", {"PIC": pic})
            src = load(xml(body, [dev("brick", "ev3")]))
            r = run(src)
            nm = "picture " + pic
            if not r["ok"]:
                fail(nm, "%s: %s" % (r["where"], r["error"]))
                print("".join("    " + l + "\n" for l in src.split("\n")))
                continue
            if "def draw_" not in src or src.count("draw_") < 2:
                fail(nm, "no escribio la funcion")
                continue
            im = raster(r["draw"])
            im.convert("L").resize((178 * 3, 128 * 3)).save(
                os.path.join(HERE, "out", "pic_%s.png" % pic))
            bad_pts = [(x, y, want) for x, y, want in pts
                       if (im.getpixel((x, y)) == 0) != bool(want)]
            if bad_pts:
                fail(nm, "pixeles que no son lo esperado: %s" % bad_pts)
            else:
                print("%-26s OK     %d llamadas, forma comprobada" % (nm, len(r["draw"])))
        # the same picture twice in one program: one function, two calls
        src = load(xml(blk("pb_picture", {"PIC": "happy"},
                           nxt=blk("pb_picture", {"PIC": "happy"})),
                       [dev("brick", "ev3")]))
        if src.count("def draw_happy_face") == 1 and src.count("draw_happy_face()\n") == 2 \
                and "from pybricks.parameters import Port, Color" in src:
            print("%-26s OK     una funcion, dos llamadas, Color importado" % "picture twice")
        else:
            fail("picture twice", src)

        # the EV3's own pictures: the real names, the right import
        for nm in ("ANGRY", "SLEEPING", "DIZZY", "WINKING", "NEUTRAL", "THUMBS_UP",
                   "QUESTION_MARK", "TIRED_LEFT", "CRAZY_1", "KNOCKED_OUT"):
            src = load(xml(blk("pb_image", {"IMG": nm}), [dev("brick", "ev3")]))
            r = run(src)
            if (r["ok"] and ["load_image", "ImageFile." + nm] in r["log"]
                    and "from pybricks.media.ev3dev import ImageFile\n" in src):
                print("%-26s OK     load_image(ImageFile.%s)" % ("image " + nm.lower(), nm))
            else:
                fail("image " + nm.lower(), "%s\n%s" % (r, src))

        # Save as / Open: the project text brings back the same blocks
        before = page.evaluate("window.__code()")
        txt = page.evaluate("window.__projectText()")
        page.evaluate("x => window.__load('<xml xmlns=\"https://developers.google.com/blockly/xml\"></xml>')")
        empty = page.evaluate("window.__code()")
        after = page.evaluate("x => window.__load(x)", txt)
        if txt.startswith("<xml") and empty != before and after == before:
            print("%-26s OK     guardar y abrir devuelve los mismos bloques" % "save and open")
        else:
            fail("save and open", "antes:\n%s\ndespues:\n%s" % (before, after))

        # Dropping a Movement block puts the robot in Set up (what the person
        # sees), once, and not while a program loads
        def drop(types):
            page.evaluate("""(ts) => { ts.forEach(t => {
                const b = Blockly.getMainWorkspace().newBlock(t); b.initSvg(); b.render(); }); }""", types)
            page.wait_for_timeout(150)
            return page.evaluate("window.__code()")
        load('<xml xmlns="https://developers.google.com/blockly/xml"></xml>')
        c1 = drop(["pb_go_for"])
        c2 = drop(["pb_spin_for", "pb_go_start"])
        if ("left_motor = Motor(Port.B)" in c1 and "right_motor = Motor(Port.C)" in c1
                and "robot = DriveBase(left_motor, right_motor" in c1
                and c2.count("DriveBase(") == 1 and c2.count("Motor(Port.B)") == 1):
            print("%-26s OK     Set up con los dos motores y el drive base, una sola vez" % "movement fills Set up")
        else:
            fail("movement fills Set up", c1 + "\n----\n" + c2)
        # an existing Setup block gets it appended; the motors already on B and C are reused
        load(xml('', [dev("brick", "ev3"), dev("motor", "wheel_l", "B")]))
        c3 = drop(["pb_move_stop"])
        if ("wheel_l = Motor(Port.B)" in c3 and "right_motor = Motor(Port.C)" in c3
                and "DriveBase(wheel_l, right_motor" in c3 and c3.count("Motor(Port.B)") == 1):
            print("%-26s OK     reusa el motor que ya estaba en B" % "Set up reuses a motor")
        else:
            fail("Set up reuses a motor", c3)
        # nothing is added when a drive base is already there
        load(xml('', [dev("motor", "l", "A"), dev("motor", "r", "D"),
                      dev("drive", "chassis", LEFT="l", RIGHT="r")]))
        c4 = drop(["pb_go_for"])
        if c4.count("DriveBase(") == 1 and "chassis = DriveBase(l, r" in c4 and "left_motor" not in c4:
            print("%-26s OK     no agrega otro si ya hay drive base" % "Set up left alone")
        else:
            fail("Set up left alone", c4)

        # ---- renaming a device carries every block that picks it ----
        two = xml(chain(blk("pb_run", {"DEV": "arm"}, {"SPEED": 100}),
                        blk("pb_run", {"DEV": "elbow"}, {"SPEED": 50}),
                        blk("pb_stop", {"DEV": "arm", "HOW": "brake"})),
                  [dev("motor", "arm", "A"), dev("motor", "elbow", "B")])
        load(two)
        src = rename("arm", "shoulder")
        r = run(src)
        if ("shoulder = Motor(Port.A)" in src and "shoulder.run(100)" in src
                and "shoulder.brake()" in src and "arm" not in src
                and "elbow.run(50)" in src and r["ok"]):
            print("%-26s OK     un nombre nuevo llega a todos los bloques"
                  % "rename")
        else:
            fail("rename", "no siguio al dispositivo:\n" + src)

        # A name another device has is refused, so two blocks can never end
        # up meaning the same name.
        src = rename("shoulder", "elbow")
        if "shoulder = Motor(Port.A)" in src and "# ERROR" not in src:
            print("%-26s OK     no deja repetir un nombre"
                  % "rename to a taken name")
        else:
            fail("rename to a taken name", src)

        src = rename("shoulder", "wait")
        if "shoulder = Motor(Port.A)" in src:
            print("%-26s OK     no deja usar una palabra de Python"
                  % "rename to a Python word")
        else:
            fail("rename to a Python word", src)

        # Typed text is tidied into something Python accepts.
        src = rename("shoulder", "my arm!")
        if "my_arm = Motor(Port.A)" in src and "my_arm.run(100)" in src:
            print("%-26s OK     'my arm!' queda my_arm" % "name tidied")
        else:
            fail("name tidied", src)

        # ---- warnings on the blocks themselves ----
        load(xml(blk("pb_run", {"DEV": "ghost"}, {"SPEED": 10}), MOTOR_B))
        w = page.evaluate("window.__warnings()")
        if len(w) == 1 and "ghost" in w[0]:
            print("%-26s OK     avisa que ghost no esta en Set up"
                  % "warning: missing")
        else:
            fail("warning: missing", w)
        load(xml(blk("pb_wait", values={"MS": 1}),
                 [dev("motor", "x", "A"), dev("motor", "x", "B")]))
        w = page.evaluate("window.__warnings()")
        if len(w) == 2 and all("Two devices are called x" in t for t in w):
            print("%-26s OK     avisa en los dos bloques"
                  % "warning: same name")
        else:
            fail("warning: same name", w)
        load(xml(blk("pb_wait", values={"MS": 1}),
                 [dev("touch", "a", "S1"), dev("color", "b", "S1")]))
        w = page.evaluate("window.__warnings()")
        if len(w) == 2 and all("Port S1 is used by a and b" in t for t in w):
            print("%-26s OK     avisa del puerto repetido"
                  % "warning: same port")
        else:
            fail("warning: same port", w)

        # ---- a new block asks for a free name and a free port ----
        load(xml(blk("pb_wait", values={"MS": 1}),
                 [dev("motor", "motor", "A"), dev("motor", "motor2", "B")]))
        got = page.evaluate("""() => {
          var w = Blockly.getMainWorkspace();
          var b = w.newBlock('pb_dev_motor');
          var t = w.newBlock('pb_dev_touch');
          return [b.getFieldValue('NAME'), b.getFieldValue('PORT'),
                  t.getFieldValue('NAME'), t.getFieldValue('PORT')];
        }""")
        if got == ["motor3", "C", "touch", "S1"]:
            print("%-26s OK     motor3 en C, touch en S1"
                  % "fresh name and port")
        else:
            fail("fresh name and port", got)

        # ---- devices belong under Set up, actions under the program ----
        res = page.evaluate("""() => {
          var w = Blockly.getMainWorkspace();
          var k = new Blockly.ConnectionChecker();
          var c = { canConnect: function (a, b) { return k.doTypeChecks(a, b); } };
          var m = w.newBlock('pb_dev_motor'), r = w.newBlock('pb_run');
          var s = w.newBlock('pb_setup'), p = w.newBlock('pb_program');
          var f = w.newBlock('pb_forever');
          return {
            devUnderSetup: c.canConnect(m.previousConnection,
                              s.getInput('DO').connection, false),
            devUnderProgram: c.canConnect(m.previousConnection,
                              p.getInput('DO').connection, false),
            devUnderLoop: c.canConnect(m.previousConnection,
                              f.getInput('DO').connection, false),
            actUnderProgram: c.canConnect(r.previousConnection,
                              p.getInput('DO').connection, false),
            actUnderSetup: c.canConnect(r.previousConnection,
                              s.getInput('DO').connection, false)
          };
        }""")
        want = {"devUnderSetup": True, "devUnderProgram": False,
                "devUnderLoop": False, "actUnderProgram": True,
                "actUnderSetup": False}
        if res == want:
            print("%-26s OK     cada bloque solo cabe donde debe"
                  % "where blocks fit")
        else:
            fail("where blocks fit", res)

        # ---- My Blocks: Python runs top to bottom, so the def has to come
        # above the call or the program dies on NameError ----
        mine = (HEAD +
                setup(dev("brick", "ev3"), y=500) +
                '<block type="procedures_defnoreturn" x="30" y="300">'
                '<field name="NAME">beep twice</field><statement name="STACK">'
                + blk("pb_beep", values={"FREQ": 440, "MS": 80},
                      nxt=blk("pb_beep", values={"FREQ": 660, "MS": 80}))
                + "</statement></block>"
                '<block type="pb_program" x="30" y="30"><statement name="DO">'
                '<block type="procedures_callnoreturn">'
                '<mutation name="beep twice"></mutation></block>'
                "</statement></block></xml>")
        src = load(mine)
        r = run(src)
        want = [["EV3Brick"], ["beep", 440, 80], ["beep", 660, 80]]
        if not r["ok"]:
            fail("my block", "%s: %s" % (r["where"], r["error"]))
        elif r["log"] != want:
            fail("my block", r["log"])
        elif src.index("def beep_twice") > src.index("beep_twice()\n"):
            fail("my block", "la definicion va despues de la llamada")
        else:
            print("%-26s OK     definida antes de llamarla" % "my block")

        # ---- Variables: every one starts at 0, so reading one that was
        # never written runs instead of dying ----
        var = (HEAD +
               '<variables><variable id="c">count</variable></variables>'
               '<block type="pb_program" x="30" y="30"><statement name="DO">'
               '<block type="variables_set">'
               '<field name="VAR" id="c">count</field>'
               '<value name="VALUE">' + n(5) + "</value>"
               '<next><block type="math_change">'
               '<field name="VAR" id="c">count</field>'
               '<value name="DELTA">' + n(2) + "</value>"
               '<next><block type="pb_screen_print"><value name="WHAT">'
               '<block type="variables_get">'
               '<field name="VAR" id="c">count</field></block>'
               "</value></block></next></block></next></block>"
               "</statement></block></xml>")
        src = load(var)
        r = run(src)
        if r["ok"] and r["log"] == [["EV3Brick"], ["screen_print", "7"]]:
            print("%-26s OK     5 + 2 = 7 en el ladrillo" % "variables")
        else:
            fail("variables", r.get("error") or r.get("log"))

        # An empty workspace must still produce something importable.
        src = load(xml(""))
        r = run(src)
        print("%-26s %s" % ("programa vacio", "OK" if r["ok"] else "FALLO"))
        if not r["ok"]:
            bad += 1

        # Only what was set up is declared.
        src = load(xml(blk("pb_run", {"DEV": "arm"}, {"SPEED": 100}), MOTOR_B))
        extra = [p for p in "ACD" if ("Port." + p) in src]
        if extra:
            fail("declares what is set up", "puertos de mas: %s" % extra)
        else:
            print("%-26s OK     solo declara lo que esta en Set up"
                  % "declares what is set up")

        # Stop is imported only when a block actually asks for one.
        if "import Port, Stop" in src:
            fail("imports", "importa Stop sin necesitarlo")
        else:
            print("%-26s OK     no importa Stop de mas" % "imports")

        br.close()

    print("\nFALLOS: %d" % bad)
    raise SystemExit(1 if bad else 0)


main()
