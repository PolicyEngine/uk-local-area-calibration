constituency-weights:
	cd constituencies && python calibrate.py

format:
	black . -l 79
