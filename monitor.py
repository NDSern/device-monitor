"""
Resource Monitor Module
Tracks CPU, RAM, and NPU usage on the local machine.
"""

import os
import re
import subprocess
import psutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# RKNN NPU debug path (requires root/sudo for debugfs)
NPU_DEBUG_LOAD_PATH = "/sys/kernel/debug/rknpu/load"

# Fallback: devfreq path (aggregate load only, no per-core breakdown)
NPU_DEVFREQ_LOAD_PATH = "/sys/devices/platform/fdab0000.npu/devfreq/fdab0000.npu/load"

# Legacy per-core sysfs paths (older kernels/drivers)
NPU_LEGACY_LOAD_PATHS = [
    "/sys/class/misc/rknpu/load0",
    "/sys/class/misc/rknpu/load1",
    "/sys/class/misc/rknpu/load2",
]


class ResourceMonitor:
    """Monitors system CPU, RAM, and NPU usage."""

    @staticmethod
    def get_cpu_usage() -> float:
        """
        Get current CPU usage percentage.

        Returns:
            float: CPU usage percentage (0-100)
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        logger.info(f"CPU Usage: {cpu_percent:.1f}%")
        return cpu_percent

    @staticmethod
    def get_ram_usage() -> float:
        """
        Get current RAM usage percentage.

        Returns:
            float: RAM usage percentage (0-100)
        """
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        logger.info(f"RAM Usage: {ram_percent:.1f}% (Available: {memory.available / (1024**3):.2f} GB)")
        return ram_percent

    @staticmethod
    def _read_npu_debug_load() -> list | None:
        """
        Read per-core NPU usage from debugfs via sudo.

        The debugfs path outputs a line like:
            NPU load:  Core0: 68%, Core1: 71%, Core2:  0%,

        Returns:
            list or None: List of per-core usage floats, or None on failure.
        """
        try:
            result = subprocess.run(
                ["sudo", "cat", NPU_DEBUG_LOAD_PATH],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode != 0:
                return None
            # Parse "Core0: 68%, Core1: 71%, Core2:  0%,"
            matches = re.findall(r"Core\d+:\s*(\d+)%", result.stdout)
            if matches:
                return [float(v) for v in matches]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.debug(f"Failed to read NPU debug load: {e}")
        return None

    @staticmethod
    def _read_npu_legacy_load() -> list | None:
        """
        Read per-core NPU usage from legacy sysfs paths.

        Returns:
            list or None: List of per-core usage floats, or None if paths don't exist.
        """
        if not os.path.exists(NPU_LEGACY_LOAD_PATHS[0]):
            return None
        usage = []
        for path in NPU_LEGACY_LOAD_PATHS:
            try:
                with open(path, "r") as f:
                    usage.append(float(int(f.read().strip())))
            except (IOError, ValueError, PermissionError) as e:
                logger.warning(f"Failed to read NPU load from {path}: {e}")
                usage.append(0.0)
        return usage

    @staticmethod
    def _read_npu_devfreq_load() -> list | None:
        """
        Read aggregate NPU load from devfreq (no per-core breakdown).

        The devfreq load file outputs a line like: "100@1000000000Hz"

        Returns:
            list or None: Single-element list with aggregate usage, or None on failure.
        """
        try:
            if os.path.exists(NPU_DEVFREQ_LOAD_PATH):
                with open(NPU_DEVFREQ_LOAD_PATH, "r") as f:
                    content = f.read().strip()
                    # Format: "50@1000000000Hz"
                    load = int(content.split("@")[0])
                    return [float(load)]
        except (IOError, ValueError, PermissionError) as e:
            logger.debug(f"Failed to read NPU devfreq load: {e}")
        return None

    def get_npu_usage(self) -> list:
        """
        Get NPU core usage percentages.

        Tries multiple sources in order:
        1. debugfs per-core load (requires sudo)
        2. Legacy per-core sysfs paths
        3. devfreq aggregate load (replicated across 3 cores)

        Returns:
            list: NPU usage percentages for each of the 3 cores
        """
        # Try debugfs first (per-core data)
        npu_usage = self._read_npu_debug_load()
        if npu_usage is not None:
            logger.debug("NPU load read from debugfs")
        else:
            # Try legacy sysfs paths
            npu_usage = self._read_npu_legacy_load()
            if npu_usage is not None:
                logger.debug("NPU load read from legacy sysfs")
            else:
                # Try devfreq aggregate
                devfreq = self._read_npu_devfreq_load()
                if devfreq is not None:
                    # Replicate aggregate load across 3 cores
                    npu_usage = devfreq * 3
                    logger.debug("NPU load read from devfreq (aggregate)")
                else:
                    npu_usage = [0.0, 0.0, 0.0]
                    logger.debug("No NPU load source available")

        # Pad to 3 cores if fewer were returned
        while len(npu_usage) < 3:
            npu_usage.append(0.0)

        logger.info(f"NPU Usage: Core0={npu_usage[0]:.1f}%, Core1={npu_usage[1]:.1f}%, Core2={npu_usage[2]:.1f}%")
        return npu_usage

    @staticmethod
    def get_system_info() -> dict:
        """
        Get basic system information.

        Returns:
            dict: System info including hostname, CPU count, and total RAM
        """
        memory = psutil.virtual_memory()
        return {
            "hostname": psutil.Process().pid,  # Will be replaced with socket hostname
            "cpu_count": psutil.cpu_count(),
            "total_ram_gb": round(memory.total / (1024**3), 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def check_resources(self) -> dict:
        """
        Check all system resources and return usage data.

        Returns:
            dict: Resource usage data with CPU, RAM, and NPU percentages
        """
        import socket

        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()
        npu_usage = self.get_npu_usage()

        return {
            "hostname": socket.gethostname(),
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "npu_usage": npu_usage,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
