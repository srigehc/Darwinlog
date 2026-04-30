def decode_mdc(mdc_code):
    return MDC_REGISTRY.get(
        mdc_code,
        {
            "parameter": "UNKNOWN",
            "domain": "UNKNOWN",
            "unit": None,
            "type": "UNKNOWN"
        }
    )

MDC_REGISTRY = {
    # ECG
    "MDC_ECG_HEART_RATE_CONFIG": {
        "parameter": "Heart Rate",
        "domain": "ECG",
        "unit": "bpm",
        "type": "MEASUREMENT"
    },
    "MDC_ECG_V_P_C_RATE_CONFIG": {
        "parameter": "PVC Rate",
        "domain": "ECG",
        "unit": "bpm",
        "type": "MEASUREMENT"
    },

    # Respiration
    "MDC_RESP_RATE_CONFIG": {
        "parameter": "Respiratory Rate",
        "domain": "RESP",
        "unit": "breaths/min",
        "type": "MEASUREMENT"
    },
    "MDC_TIME_PD_APNEA_CONFIG": {
        "parameter": "Apnea Time",
        "domain": "RESP",
        "unit": "seconds",
        "type": "ALARM"
    },

    # SpO2
    "MDC_PULS_OXIM_SAT_O2_CONFIG": {
        "parameter": "SpO2",
        "domain": "OXIMETRY",
        "unit": "%",
        "type": "MEASUREMENT"
    },
    "MDC_PULS_OXIM_PULS_RATE_CONFIG": {
        "parameter": "Pulse Rate",
        "domain": "OXIMETRY",
        "unit": "bpm",
        "type": "MEASUREMENT"
    },

    # Blood Pressure
    "MDC_PRESS_BLD_NONINV_SYS_CONFIG": {
        "parameter": "NIBP Systolic",
        "domain": "BP",
        "unit": "mmHg",
        "type": "MEASUREMENT"
    },
    "MDC_PRESS_BLD_NONINV_DIA_CONFIG": {
        "parameter": "NIBP Diastolic",
        "domain": "BP",
        "unit": "mmHg",
        "type": "MEASUREMENT"
    },
    "MDC_PRESS_BLD_NONINV_MEAN_CONFIG": {
        "parameter": "NIBP Mean",
        "domain": "BP",
        "unit": "mmHg",
        "type": "MEASUREMENT"
    },

    # CO2
    "MDC_CONC_AWAY_CO2_ET_CONFIG": {
        "parameter": "EtCO2",
        "domain": "CAPNOGRAPHY",
        "unit": "mmHg",
        "type": "MEASUREMENT"
    },
    "MDC_CO2_RESP_RATE_CONFIG": {
        "parameter": "CO2 RR",
        "domain": "CAPNOGRAPHY",
        "unit": "breaths/min",
        "type": "MEASUREMENT"
    },

    # Agent
    "MDC_CONC_AWAY_SEVOFL_ET_SETTING": {
        "parameter": "EtSevo",
        "domain": "ANESTHETIC_AGENT",
        "unit": "%",
        "type": "SETTING"
    },
}