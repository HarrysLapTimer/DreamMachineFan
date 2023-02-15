#   dream_machine_fan.py
#
#   Harald Schlangmann, February 2023
#   https://github.com/HarrysLapTimer/DreamMachineFan

import os, time, subprocess, re
from simple_pid import PID

#   configure here
target_temperature = 45
sensors_temperature_tag = "temp1:" # or "Board Temp:" or "temp3:"
loop_seconds = 5 # adjust slowly, wait 5 seconds between every fan adjustment
min_pwm2 = 89 # seen for OS v3.0.13
max_pwm2 = 150 # seen for OS v3.0.16
pwm2_file = "/sys/class/hwmon/hwmon0/device/pwm2"

#   our controller system - a Unifi Dream Machine's fan
class DreamMachineSE(object):

    #   initialize
    def __init__(self):
        self.pwm2 = None

    #   set a new fan speed (pwm2) and return the current temperature
    def update(self, pwm2):

        #   read temperature
        temperature = None
        with subprocess.Popen(['sensors'], stdout=subprocess.PIPE) as proc:
            for line in proc.stdout:
                output_row = line.decode("utf-8").rstrip().split()
                if len(output_row)>0 and output_row[0] == sensors_temperature_tag:
                    m = re.search("[0-9]+\.[0-9]+", output_row[1])
                    if m:
                        temperature = float(m.group(0))

        #   write pwm2 in case it is changed
        if pwm2 is not None:
            pwm2 = int(pwm2)
            if pwm2 != self.pwm2:
                self.pwm2 = pwm2
                print(u"{:s}\ttemperature is {:.1f}°C, setting fan to {:.0f}".format(time.ctime(), temperature, pwm2))
                with open(pwm2_file, 'w') as writer:
                    writer.write(str(pwm2))
            else:
                print(u"{:s}\ttemperature is {:.1f}°C, keeping fan at {:.0f}".format(time.ctime(), temperature, pwm2))

        return temperature

controlled_system = DreamMachineSE()

#   our PID controller (see https://en.wikipedia.org/wiki/PID_controller)

#   tuning uses negative values to increase fan speed when temperature is too high and vice versa
#   current settings use Proprortional, Integral, but no Derivative gain of PID controller
pid = PID(-1.0, -0.1, 0, setpoint=target_temperature)
pid.output_limits = (min_pwm2, max_pwm2) # limit pwm2 to valid / proofen values

print(u"controlling DreamMachineSE fans 2-4 to keep temperature at {:.1f}°C".format(target_temperature))

#   run the loop setting a fan speed and reacting on temperature changes
temperature = controlled_system.update(None)

while True:
    #   memorize start time to make every loop the same duration
    start_time = time.time()

    #   compute new output from the PID according to the systems current temperature
    pwm2 = pid(temperature)

    #   feed the PID output to the system and get its current temperature
    temperature = controlled_system.update(pwm2)

    #   allow temperature to adjust based on changed fan speed
    processing_seconds = time.time() - start_time
    if processing_seconds<loop_seconds:
        time.sleep(loop_seconds-processing_seconds)

# vim: tabstop=4 shiftwidth=4 noexpandtab
