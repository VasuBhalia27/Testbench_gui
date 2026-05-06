"""Timing profile values for automation speed tuning.

Set environment variable ``AUTOMATION_SPEED`` to ``fast`` to reduce fixed
delays and shorten total execution time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TimingProfile:
    supply_off_wait: float
    supply_on_wait: float
    first_run_fw_init_wait: float
    before_go_wait: float
    bat_initial_wait: float
    bat_retry_wait: float
    led_stabilize_wait: float
    led_off_stabilize_wait: float
    motor_actuate_wait: float
    eos_mode_switch_wait: float
    eos_reset_stabilize_wait: float
    eos_measure_wait: float
    eos_clear_wait: float
    eos_set_process_wait: float
    sg1_measure_wait: float
    sg2_flag_wait: float
    sg2_reset_wait: float
    sg2_measure_wait: float
    capa_retry_timeout: float
    capa_retry_interval: float
    stable_poll_interval: float
    can_response_timeout: float
    lin_response_timeout: float


NORMAL = TimingProfile(
    supply_off_wait=2.0,    # increased 1.0→2.0 s: allow more time for supply rails to discharge
    supply_on_wait=5.0,     # increased 3.0→5.0 s: bench PSU needs more time to reach full voltage before ADC reads
    first_run_fw_init_wait=5.0,
    before_go_wait=0.2,
    bat_initial_wait=5.0,   # increased 3.0→5.0 s: ADC needs more stabilisation time on tester bench
    bat_retry_wait=8.0,     # increased 5.0→8.0 s: give supply more time between retries
    led_stabilize_wait=0.5,
    led_off_stabilize_wait=2.0,   # increased: LED voltage needs ~2 s to discharge to ≤ 10 mV
    motor_actuate_wait=1.0,
    eos_mode_switch_wait=0.2,
    eos_reset_stabilize_wait=0.3,
    eos_measure_wait=0.4,
    eos_clear_wait=0.2,
    eos_set_process_wait=0.6,
    sg1_measure_wait=3.0,   # increased 0.8→3.0: firmware needs ~3 s to compute SG OpAmp values
    sg2_flag_wait=0.2,
    sg2_reset_wait=0.3,
    sg2_measure_wait=3.0,   # increased 0.8→3.0: firmware needs ~3 s to compute SG OpAmp values
    capa_retry_timeout=3.0,   # 15.0→3.0: retry window for CAPA DID until values meet threshold
    capa_retry_interval=0.25,
    stable_poll_interval=0.25,
    can_response_timeout=5.0,  # max seconds to poll for CanRxDataValid after send_did
    lin_response_timeout=5.0,  # max seconds to poll for LinRxDataValid after send_did
)

FAST = TimingProfile(
    supply_off_wait=0.5,
    supply_on_wait=1.0,
    first_run_fw_init_wait=3.0,
    before_go_wait=0.2,
    bat_initial_wait=0.5,
    bat_retry_wait=2.0,
    led_stabilize_wait=0.5,
    led_off_stabilize_wait=2.0,
    motor_actuate_wait=0.3,
    eos_mode_switch_wait=0.2,
    eos_reset_stabilize_wait=0.5,
    eos_measure_wait=0.5,
    eos_clear_wait=0.2,
    eos_set_process_wait=0.8,
    sg1_measure_wait=3.0,
    sg2_flag_wait=0.2,
    sg2_reset_wait=0.2,
    sg2_measure_wait=3.0,
    capa_retry_timeout=3.0,
    capa_retry_interval=0.25,
    stable_poll_interval=0.25,
    can_response_timeout=5.0,
    lin_response_timeout=5.0,
)


def get_timing_profile() -> TimingProfile:
    speed = os.getenv("AUTOMATION_SPEED", "normal").strip().lower()
    if speed == "fast":
        return FAST
    return NORMAL


TIMING = get_timing_profile()
