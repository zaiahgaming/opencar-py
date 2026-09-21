# vehicle_profile.py — Real opendbc CAN signal profiles
# These match the verified signal IDs from commaai/opendbc
#
# Each profile maps the key CAN arbitration IDs and scaling factors
# needed to decode raw CAN frames into human-readable vehicle data.
#
# References:
#   https://github.com/commaai/opendbc
#   https://github.com/commaai/openpilot/tree/master/selfdrive/car

PROFILES = {
    'toyota': {
        # ---- Speed ----
        'speed_id':     0x0B4,   # SPEED message (11-bit ID 180)
        'speed_signal': 'SPEED',
        'speed_factor': 0.01,    # raw uint16 * 0.01 = km/h
        'speed_is_mph': False,   # output is km/h; hardware.py converts
        # ---- RPM ----
        'rpm_id':       0x1C4,   # ENG1F07 (11-bit ID 452)
        'rpm_factor':   0.78125, # raw uint16 * 0.78125 = RPM
        # ---- Gear ----
        'gear_id':      0x3BC,   # ECT1S92 (11-bit ID 956)
        #   gear nibble: data[0] & 0x0F  → 0=P 1=R 2=N 3=D
        # ---- ADAS / ACC ----
        'acc_id':       0x343,   # ACC1S03 (11-bit ID 835)
        #   acc_active bit: data[0] & 0x01
        # ---- LKA ----
        'lka_id':       0x262,   # EPS_STATUS (11-bit ID 610)
    },

    'honda': {
        # ---- Speed ----
        'speed_id':     0x158,   # ENGINE_DATA — XMISSION_SPEED at byte 0-1
        'speed_signal': 'XMISSION_SPEED',
        'speed_factor': 0.01,    # raw uint16 LE * 0.01 = km/h
        'speed_is_mph': False,
        # ---- RPM ----
        'rpm_id':       0x158,   # ENGINE_DATA — ENGINE_RPM at bytes 2-3
        'rpm_factor':   1.0,
        # ---- Gear ----
        'gear_id':      0x1A3,   # GEARBOX_AUTO
        # ---- ADAS / ACC ----
        'acc_id':       0x17C,   # POWERTRAIN_DATA
        # ---- LKA ----
        'lka_id':       0x296,
    },

    'gm': {
        # ---- Speed ----
        'speed_id':     0x3E9,   # ECMVehicleSpeed
        'speed_signal': 'VehicleSpeed',
        'speed_factor': 0.01,    # raw * 0.01 = mph (GM uses native mph)
        'speed_is_mph': True,    # already in mph; no km/h conversion needed
        # ---- RPM ----
        'rpm_id':       0x0C9,   # ECMEngineStatus
        'rpm_factor':   0.25,    # raw * 0.25 = RPM
        # ---- Gear ----
        'gear_id':      0x135,   # ECMPRDNL
        # ---- ADAS / ACC ----
        'acc_id':       0x370,   # ASCMActiveCruiseControlStatus
        # ---- LKA ----
        'lka_id':       0x184,
    },

    'ford': {
        # ---- Speed ----
        'speed_id':     0x415,   # BrakeSysFeatures
        'speed_signal': 'VehicleSpd',
        'speed_factor': 0.01,    # raw * 0.01 = km/h
        'speed_is_mph': False,
        # ---- RPM ----
        'rpm_id':       0x201,   # EngVehicleSpThrottle
        'rpm_factor':   2.0,     # raw * 2.0 = RPM
        # ---- Gear ----
        'gear_id':      0x176,   # PowertrainData_10
        # ---- ADAS / ACC ----
        'acc_id':       0x186,   # ACCDATA
        # ---- LKA ----
        'lka_id':       0x3CA,
    },
}

# Gear nibble → human-readable label (used by all profiles unless overridden)
GEAR_LABELS = {
    0: 'P',
    1: 'R',
    2: 'N',
    3: 'D',
    4: 'L',
    7: 'S',   # Sport (some models)
}
