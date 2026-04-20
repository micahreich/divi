#!/bin/bash
set -e

# ─── Fix named-volume ownership ───────────────────────────────────────────────
for dir in "${ROS_WS}/build" "${ROS_WS}/devel" "${ROS_WS}/log"; do
    if [ -d "$dir" ] && [ "$(stat -c %u "$dir")" != "$(id -u)" ]; then
        sudo chown -R "$(id -u):$(id -g)" "$dir"
    fi
done

# ─── Source ROS1 ──────────────────────────────────────────────────────────────
source /opt/ros/noetic/setup.bash

# Configure workspace to extend system ROS if not already done
if [ ! -f "${ROS_WS}/.catkin_tools/profiles/default/config.yaml" ]; then
    cd "${ROS_WS}" && catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release
fi

# Source workspace overlay if it has been built
if [ -f "${ROS_WS}/devel/setup.bash" ]; then
    source "${ROS_WS}/devel/setup.bash"
fi

# ─── Helpful banner ───────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   ROS1 Noetic — development shell            ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  ROS_WS     : ${ROS_WS}"
echo "║  ROS distro : $(printenv ROS_DISTRO)"
if [ -f "${ROS_WS}/devel/setup.bash" ]; then
echo "║  Workspace  : built ✓"
else
echo "║  Workspace  : not built yet — run: catkin build"
fi
echo "╚══════════════════════════════════════════════╝"
echo ""

exec "$@"
