esp8266 project

using micropython with esp8266-20170108-v1.8.7.bin


### connect to esp8266

-   plugin device
-   check `dmesg` for '/dev/ttyUSB*' i.e., `dmesg | grep /dev/ttyUSB*`
-   run:  `picocom /dev/ttyUSB0 -b115200`
-   you are now in the REPL

### transfer files 

- install [ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy)
- use ampy: `ampy --port /dev/ttyUSB0 ls'
- 


hacks
1. receiving strange memory error?
```
>>> 
>>> 
PYB: sof#12 ets_task(40100164, 3, 3fff829c, 4)
The FAT filesystem starting at sector 153 with size 866 sectors appears to
be corrupted. If you had important data there, you may want to make a flash
snapshot to try to recover it. Otherwise, perform factory reprogramming
of MicroPython firmware (completely erase flash, followed by firmware
programming).

The FAT filesystem starting at sector 153 with size 866 sectors appears to
be corrupted. If you had important data there, you may want to make a flash
snapshot to try to recover it. Otherwise, perform factory reprogramming
of MicroPython firmware (completely erase flash, followed by firmware
programming).

Traceback (most recent call last):
    File "_boot.py", line 11, in <module>
    File "inisetup.py", line 36, in setup
    File "inisetup.py", line 21, in check_bootsec
    File "inisetup.py", line 33, in fs_corrupted

```


clean filesystem
```
import uos
import flashbdev
uos.VfsFat.mkfs(flashbdev.bdev)
```
