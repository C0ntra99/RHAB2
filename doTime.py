import time, datetime, random

load = ["|", "/", "-", "\\"]
counter = 0

while True:
	now = datetime.datetime.now()
	currDate = "{:02}/{:02}/{:04}".format(now.month, now.day, now.year)
	if now.hour >= 12:
		currTime = "{:02d}:{:02d}:{:02d} {:s}".format(now.hour % 12, now.minute, now.second, "PM")
	elif now.hour > 12:
		currTime = "{:2d}:{:2d}:{:02d} {:s}".format(now.hour, now.minute, now.second, "PM")
	else:
		currTime = "{:02d}:{:02d}:{:02d} {:s}".format(now.hour, now.minute, now.second, "AM")
	
	print("\rWelcome to {0:s} {1:s}. {2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s}{2:s} {3:s}".format(currDate, currTime, load[counter % len(load)], str(random.randint(0,1))), end="")
	if counter % len(load) == len(load) - 1:
		counter = 0
	else:
		counter += 1
	time.sleep(.125)