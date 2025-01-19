import TimeTracker
import sys


if TimeTracker.is_connected():
	# Get the argument passed from Shortcuts
	if len(sys.argv) > 1:
	    user_input = sys.argv[1]


	    TimeTracker.Timer().startTimer(user_input)
		
	else:
	    TimeTracker.Timer().startTimer()
else:
	print("Please check your internet connection.")
