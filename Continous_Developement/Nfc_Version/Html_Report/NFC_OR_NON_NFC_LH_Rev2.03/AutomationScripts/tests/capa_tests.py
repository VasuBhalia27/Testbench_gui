"""CAPA test cases — thin wrappers around CapaTest.

The full automation logic lives in automation/core/capa_test.py.
This file is kept as a reference for the two test case identifiers.

TC_CAPA_01: Unlock Sensor Active  — requires physical touch on sensor.
TC_CAPA_02: Unlock Sensor Inactive — resting / default state.
"""

from AutomationScripts.backend_adapter.capa_service import read_capa_values


def run_suite():
	"""Execute CAPA tab checks for active and inactive unlock conditions."""
	data = read_capa_values("capa_suite")

	unlock = float(data.get("TestFw_CapaUnlockSensorValue", 0.0) or 0.0)
	approach = float(data.get("TestFw_CapaApproachSensorValue", 0.0) or 0.0)
	lock = float(data.get("TestFw_CapaLockSensorValue", 0.0) or 0.0)
	unlock_flag = float(data.get("TestFw_CapaUnlock", 0.0) or 0.0)
	approach_flag = float(data.get("TestFw_CapaApproach", 0.0) or 0.0)
	lock_flag = float(data.get("TestFw_CapaLock", 0.0) or 0.0)

	# Per-sensor thresholds — Lock and Unlock channels read ~8996/8989 in hardware.
	UNLOCK_THRESHOLD  = 8900.0
	APPROACH_THRESHOLD = 8900.0
	LOCK_THRESHOLD    = 8900.0
	active_pass = (
		unlock > UNLOCK_THRESHOLD and approach > APPROACH_THRESHOLD and lock > LOCK_THRESHOLD
		and unlock_flag == 1.0 and approach_flag == 1.0 and lock_flag == 1.0
	)
	inactive_pass = (
		unlock <= UNLOCK_THRESHOLD and approach <= APPROACH_THRESHOLD and lock <= LOCK_THRESHOLD
		and unlock_flag == 0.0 and approach_flag == 0.0 and lock_flag == 0.0
	)

	common_observed = (
		f"unlock={unlock:.1f}, approach={approach:.1f}, lock={lock:.1f}, "
		f"flags=({int(unlock_flag)}, {int(approach_flag)}, {int(lock_flag)})"
	)

	return [
		{
			"TestCaseID": "TC_CAPA_01",
			"TestName": "CAPA unlock active",
			"MeasuredValue": unlock,
			"MeasuredStr": common_observed,
			"Expected": "unlock/lock > 8900, approach > 8900, all flags = 1",
			"Status": "PASS" if active_pass else "FAIL",
			"Details": "Requires physical touch/input on sensor",
		},
		{
			"TestCaseID": "TC_CAPA_02",
			"TestName": "CAPA unlock inactive",
			"MeasuredValue": unlock,
			"MeasuredStr": common_observed,
			"Expected": "unlock/lock <= 8900, approach <= 8900, all flags = 0",
			"Status": "PASS" if inactive_pass else "FAIL",
			"Details": "Resting sensor state check",
		},
	]


def execute_all_capa_tests() -> list:
	"""Execute all CAPA tab tests."""
	return run_suite()
