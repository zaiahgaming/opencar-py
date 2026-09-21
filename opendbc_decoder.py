#!/usr/bin/env python3
"""
opendbc_decoder.py — High-performance CAN frame decoding powered by commaai/opendbc.

Integrates with opendbc's automotive DBC library (60+ makes/models) and provides:
1. Native DBC frame decoding using opendbc.can.parser.get_raw_value
2. Pre-configured vehicle mapping (Toyota, Honda, Ford, GM, Hyundai/Kia, VW, Tesla, BMW, etc.)
3. Fallback ISO 15765-4 OBD-II PID decoder (0x7DF -> 0x7E8) for standard OBD-2 port taps
"""

import os
import time
import logging
from typing import Optional, Dict, Any

log = logging.getLogger('opencar.opendbc')

try:
    from opendbc.can.dbc import DBC
    from opendbc.can.parser import get_raw_value
    HAVE_OPENDBC = True
except ImportError:
    HAVE_OPENDBC = False
    log.warning("opendbc package not installed. Run 'pip install opendbc' for full DBC support.")

# Standard default DBCs by car make
DEFAULT_DBC_MAP = {
    'toyota':        'toyota_prius_2010_pt',
    'toyota_modern': 'toyota_2017_ref_pt',
    'toyota_tss2':   'toyota_tss2_adas',
    'honda':         'acura_ilx_2016_nidec',
    'acura':         'acura_ilx_2016_nidec',
    'ford':          'ford_fusion_2018_pt',
    'gm':            'gm_global_a_chassis',
    'cadillac':      'cadillac_ct6_powertrain',
    'hyundai':       'hyundai_kia_generic',
    'kia':           'hyundai_kia_generic',
    'vw':            'vw_mqb',
    'volkswagen':    'vw_mqb',
    'audi':          'vw_mqb',
    'tesla':         'tesla_can',
    'bmw':           'bmw_e9x_e8x',
    'mazda':         'mazda_2017',
    'nissan':        'nissan_xterra_2011',
    'chrysler':      'chrysler_cusw',
}

# Gear value mapping to standard PRND labels
GEAR_MAP = {
    0: 'P',
    1: 'R',
    2: 'N',
    3: 'D',
    4: 'L',
    5: 'S',
    6: 'M',
    'P': 'P', 'R': 'R', 'N': 'N', 'D': 'D', 'L': 'L', 'S': 'S', 'B': 'B'
}


class OpenDBCDecoder:
    """
    Decodes raw CAN messages using commaai/opendbc definitions.
    """

    def __init__(self, profile_name: str = 'toyota', dbc_name: Optional[str] = None):
        self.profile_name = profile_name.lower()
        self.dbc_name = dbc_name or DEFAULT_DBC_MAP.get(self.profile_name, 'toyota_prius_2010_pt')
        self.dbc = None
        self.signal_lut: Dict[int, list] = {}
        
        if HAVE_OPENDBC:
            try:
                self.dbc = DBC(self.dbc_name)
                self._build_lut()
                log.info("[OpenDBC] Loaded DBC '%s' with %d messages", self.dbc_name, len(self.dbc.msgs))
            except Exception as e:
                log.error("[OpenDBC] Failed to load DBC '%s': %s", self.dbc_name, e)

    def _build_lut(self):
        """Build fast lookup table: arbitration_id -> list of (sig, target_attr, transform)"""
        self.signal_lut.clear()
        if not self.dbc:
            return

        for addr, msg in self.dbc.msgs.items():
            for sname, sig in msg.sigs.items():
                upper_name = sname.upper()
                
                # Speed
                if upper_name in ('SPEED', 'VEHICLE_SPEED', 'WHEEL_SPEED_FL', 'V_VEH', 'WHEELSPEED_FL'):
                    # opendbc speeds are usually in km/h; check if GM/native mph
                    factor = 0.621371 if 'GM' not in self.dbc_name.upper() else 1.0
                    self._add_signal(addr, sig, 'speed_mph', lambda v, f=factor: abs(v * f))
                
                # RPM
                elif upper_name in ('RPM', 'ENGINE_RPM', 'MOTOR_RPM', 'ENGSPEED', 'N_ENG'):
                    self._add_signal(addr, sig, 'rpm', lambda v: max(0.0, float(v)))
                    
                # Gear
                elif upper_name in ('GEAR', 'PRNDL', 'CURRENT_GEAR', 'GEAR_STEP', 'TRANSMISSION_GEAR'):
                    self._add_signal(addr, sig, 'gear', lambda v: GEAR_MAP.get(int(v), str(v)))
                    
                # Engine Coolant Temp
                elif upper_name in ('COOLANT_TEMP', 'ENGINE_TEMP', 'ENG_TEMP', 'T_ENG', 'MOTORTEMP'):
                    # typically in Celsius -> Fahrenheit
                    self._add_signal(addr, sig, 'engine_temp_f', lambda v: (v * 1.8) + 32.0 if v < 80 else v)
                    
                # Cruise / ACC
                elif upper_name in ('ACC_ACTIVE', 'MAIN_ON', 'CRUISE_STATE', 'CRUISE_ACTIVE'):
                    self._add_signal(addr, sig, 'acc_active', lambda v: bool(v))

    def _add_signal(self, addr: int, sig: Any, target_attr: str, transform):
        if addr not in self.signal_lut:
            self.signal_lut[addr] = []
        self.signal_lut[addr].append((sig, target_attr, transform))

    def decode(self, can_id: int, data: bytes, state: Any) -> bool:
        """
        Decodes a single CAN frame.
        Returns True if any vehicle state attribute was updated.
        """
        updated = False

        # 1. Check opendbc DBC signals
        if can_id in self.signal_lut:
            for sig, target_attr, transform in self.signal_lut[can_id]:
                try:
                    raw = get_raw_value(data, sig)
                    if sig.is_signed:
                        raw -= ((raw >> (sig.size - 1)) & 0x1) * (1 << sig.size)
                    val = raw * sig.factor + sig.offset
                    val = transform(val)
                    state.set(target_attr, val)
                    updated = True
                except Exception:
                    pass

        # 2. Universal ISO 15765-4 OBD-II response decoding (0x7E8 - 0x7EF)
        if 0x7E8 <= can_id <= 0x7EF and len(data) >= 3:
            # Mode 01 response: [length, 0x41, pid, A, B, ...]
            if data[1] == 0x41:
                pid = data[2]
                if pid == 0x0C and len(data) >= 5:   # Engine RPM
                    rpm = ((data[3] << 8) | data[4]) / 4.0
                    state.set('rpm', rpm)
                    updated = True
                elif pid == 0x0D and len(data) >= 4: # Vehicle Speed (km/h -> mph)
                    speed_mph = data[3] * 0.621371
                    state.set('speed_mph', speed_mph)
                    updated = True
                elif pid == 0x05 and len(data) >= 4: # Engine Coolant Temp (°C -> °F)
                    temp_f = (data[3] - 40) * 1.8 + 32.0
                    state.set('engine_temp_f', temp_f)
                    updated = True
                elif pid == 0x11 and len(data) >= 4: # Throttle position (%)
                    throttle = (data[3] * 100.0) / 255.0
                    state.set('throttle', throttle)
                    updated = True
                elif pid == 0x2F and len(data) >= 4: # Fuel tank level (%)
                    fuel_pct = (data[3] * 100.0) / 255.0
                    state.set('fuel_level', fuel_pct / 100.0)
                    updated = True

        return updated
