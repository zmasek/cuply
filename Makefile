red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

up:
	@echo "${green}>>> Running the project${reset}"
	sudo chmod 777 /dev/ttyACM0
	sudo docker-compose up -d

down:
	@echo "${green}>>> Stopping the project${reset}"
	sudo docker-compose down

test:
	@echo "${green}>>> Running tests${reset}"
	@$(MAKE) up
	sudo docker-compose -f docker-compose.yml exec backend coverage run --source='.' manage.py test
	sudo docker-compose -f docker-compose.yml exec backend coverage report -m
