import TimeTracker


if TimeTracker.is_connected():
	TimeTracker.Timer().endTimer()
else:
	print("Please check your internet connection.")