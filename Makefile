.PHONY: env build up down shell logs build-ros rosdep clean-volumes x11 \
        build-official up-official down-official shell-official logs-official build-ros-official clean-volumes-official

# ── Setup ──────────────────────────────────────────────────────────────────────
env:
	@echo "Updating .env with host user identity..."
	@sed -i "s/^USER_UID=.*/USER_UID=$(shell id -u)/" .env
	@sed -i "s/^USER_GID=.*/USER_GID=$(shell id -g)/" .env
	@echo "  UID=$(shell id -u)  GID=$(shell id -g)"
	@echo "Done. Review .env before running 'make build'."

# ── ROS1 Noetic ───────────────────────────────────────────────────────────────
build:
	docker compose build

x11:
	xhost +local:docker

up: 
	docker compose up -d
	@echo "Container started. Attach with: make shell"

down:
	docker compose down

shell:
	docker compose exec ros-noetic bash

logs:
	docker compose logs -f ros-noetic

build-ros:
	docker compose exec ros-noetic bash -c \
	  "source /opt/ros/noetic/setup.bash && cd \$$ROS_WS && catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release && catkin build"

rosdep:
	docker compose exec ros-noetic bash -c \
	  "source /opt/ros/noetic/setup.bash && cd \$$ROS_WS && rosdep install --from-paths src --ignore-src -r -y"

clean-volumes:
	@echo "WARNING: This deletes all catkin build artifacts (build/, devel/, log/)."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v