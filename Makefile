constituency-weights:
	cd constituencies && python calibrate.py

format:
	black . -l 79

docker-build:
	docker build -t constituency-weights . -f docker/constituencies.Dockerfile --secret id=POLICYENGINE_GITHUB_MICRODATA_AUTH_TOKEN
