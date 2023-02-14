# DreamMachineFan
A python script to control the fan of a Unifi Dream Machine SE depending on system temperature.

# Disclaimer
Use on your own risk. This script will modify your Dream Machine's fan configuration.
It will not set speeds not seen for existing firmware versions, but there are several
assumptions which are not necessarily correct.

# Introduction
Unifi's Dream Machine SE doesn't adjust fan speeds dynamically depending on board and other 
system temperatures. This results in high values being applied to cover worst case
temperature scenarios.

This script will constantly monitor system temperature and adjust the speeds for fans 2-4
so a setpoint / target temperature is kept. The script uses a state of the art algorithm
to adjust this speed - a PID controller. For more information see the Wikipedia article on
https://en.wikipedia.org/wiki/PID_controller.

Instead of re-implementing a PID controller, this script uses simple-pid as published by
Martin Lundberg https://github.com/m-lundberg/simple-pid - thanks a lot!

# Installation
- Enable ssh for your Dream Machine and log in as root.
- To allow a full restore, memorize your Dream Machine's default fan value by entering `cat /sys/class/hwmon/hwmon0/device/pwm2` on the command line; memorize the number shown (I will refer to this number as DEFAULTSPEEDMEMORIZED)
- Check if python3 is preinstalled by entering `python3`
- In case it isn't, install it using `apt-get install python3`
- Install Python dist utilities using `apt-get install python3-distutils`
- Install `pip`: `curl "https://bootstrap.pypa.io/get-pip.py" > get-pip.py; python3 get-pip.py`
- Install simple-pid: `pip install simple-pid`
- Finally, load the script `dream_machine_fan.py` as provided in this repository

# Running the Script
Before running the script, open `dream_machine_fan.py` with your favorite editor and check the
global definitions marked with `# configure here`. They allow you to adjust a number of values
I have selected for my own system. As most of these follow assumptions (see Disclaimer), I
want to comment on them here:
- `target_temperature` is the set point temperature the script will try to meet; I have entered
45 (degree Centigrade) although this value looks ridiculous low for a electronic system; values
documentated as 'critical' by Unifi are by far higher
- `sensors_temperature_tag` select the temperature used to compare the current state against the
set point; I use `temp1:` without any knowledge where it is measure and what its meaning is;
alternatives are listed; according to what I have seen, all temperatures reported by Unifi's
`sensors` tool are related and change in parallel; a safer approach would be to read all temps
reported and use the max
- `loop_seconds` is part of the PID controller tuning which is made up from the number of
iterations done for a certain time period (this value) and the three factors Kp, Ki, Kd set in
the script using `pid = PID(-1.0, -0.1, 0, setpoint=target_temperature)`; I haven't played a lot
with these - someone with better knowledge of PID controllers and electronic hardware may
find better tunings (thanks for feedback) for fans / temperatures; for me, these parameters
stabilize fan speed after a few minutes
- `min_pwm2` and `max_pwm2` are the boundaries of fan (pwm2) values actually set; the script will
never set fan speeds outside this range - so it is your insurance to keep this in a range you
have seen in official firmware

O.k. so we are ready to test operation by entering
```
> python3 dream_machine_fan.py
```

This will start to spit out log entries that show the temperature and fan speed developement.
```
controlling DreamMachineSE fans 2-4 to keep temperature at 45.0°C
temperature is 45.8°C, setting fan to 89
temperature is 45.8°C, setting fan to 90
temperature is 46.0°C, keeping fan at 90
temperature is 45.8°C, setting fan to 91
temperature is 45.8°C, keeping fan at 91
temperature is 45.8°C, keeping fan at 91
temperature is 45.8°C, setting fan to 92
temperature is 46.0°C, keeping fan at 92
temperature is 46.0°C, setting fan to 93
temperature is 45.8°C, keeping fan at 93
temperature is 45.8°C, setting fan to 94
temperature is 46.0°C, keeping fan at 94
temperature is 45.8°C, setting fan to 95
...
temperature is 45.2°C, keeping fan at 118
temperature is 45.0°C, setting fan to 119
temperature is 45.0°C, setting fan to 118
temperature is 45.2°C, keeping fan at 118
temperature is 45.0°C, setting fan to 119
temperature is 45.0°C, setting fan to 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
temperature is 45.0°C, keeping fan at 118
...
```

![Temperature development](./figure_1.png?raw=true "Temperature development")

I suggest to monitor what is happening for an hour. Once you see it is fine in your environment and converges towards the set point temperature, you can make the script a permanent background process.

[TODO] descibe how to run the script on reboot using cron, pipe output to a log file and rotate that log so it doesn't use up a lot of space

# Uninstalling / Return to Factory Settings
That's easy:
- return to the default fan speed by entering `echo DEFAULTSPEEDMEMORIZED > /sys/class/hwmon/hwmon0/device/pwm2` (see Installation section)
- stop the process and delete `dream_machine_fan.py`

