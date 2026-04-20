# ─── Base Image ───────────────────────────────────────────────────────────────
# Ubuntu 20.04 (Focal) — ROS 1 Noetic's officially supported OS.
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ─── ROS Noetic from source (apt) ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    lsb-release \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
      http://packages.ros.org/ros/ubuntu focal main" \
      > /etc/apt/sources.list.d/ros1.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-desktop-full \
    python3-rosdep \
    python3-rosinstall \
    python3-rosinstall-generator \
    python3-wstool \
    python3-catkin-tools \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init && rosdep update

# ─── User Setup ───────────────────────────────────────────────────────────────
ARG USERNAME=rosdev
ARG USER_UID=1000
ARG USER_GID=1000

RUN set -e; \
    if getent group ${USER_GID} > /dev/null 2>&1; then \
        EXISTING_GROUP=$(getent group ${USER_GID} | cut -d: -f1); \
        if [ "${EXISTING_GROUP}" != "${USERNAME}" ]; then \
            groupmod -n ${USERNAME} ${EXISTING_GROUP}; \
        fi; \
    else \
        groupadd -g ${USER_GID} ${USERNAME}; \
    fi; \
    if getent passwd ${USER_UID} > /dev/null 2>&1; then \
        EXISTING_USER=$(getent passwd ${USER_UID} | cut -d: -f1); \
        if [ "${EXISTING_USER}" != "${USERNAME}" ]; then \
            usermod -l ${USERNAME} -d /home/${USERNAME} -m ${EXISTING_USER}; \
        fi; \
    else \
        useradd -u ${USER_UID} -g ${USER_GID} -m -s /bin/bash ${USERNAME}; \
    fi

RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 0440 /etc/sudoers.d/${USERNAME}

RUN usermod -aG video,dialout,audio,plugdev ${USERNAME} 2>/dev/null; \
    usermod -aG render ${USERNAME} 2>/dev/null || true

# ─── Extra System Packages ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    git \
    vim \
    nano \
    tmux \
    htop \
    v4l-utils \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# ─── Workspace Layout ─────────────────────────────────────────────────────────
ENV ROS_WS=/home/${USERNAME}/ros_ws

RUN mkdir -p ${ROS_WS}/src && \
    chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

# ─── Entrypoint ───────────────────────────────────────────────────────────────
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ${USERNAME}
WORKDIR ${ROS_WS}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
