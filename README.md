# flightgear_interface
a python interface to set and receive data from the flightgear flight simulator
as of now you can only read values from FlightGear, if it is popular enough
i'll add setting values too, in the end it should be abel to set and read everything from FG.

here is an example code
```python
from  flightgear_interface import FG_com
import time
fgcom=FG_com(True)
fgcom.start()
fg_com.connect_and_wait_until_ready()
time.sleep(15) #wait until FG is ready
while(1):
    print(fgcom.get_param("pitch"))
fgcom.quit()
```
for feature updates, add an issue and i'll work on it.
