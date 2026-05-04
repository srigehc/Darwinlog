import datetime
from utils.mdc_registry import decode_mdc
from model import NormalizedEvent


def parse_hl7_timestamp(ts):
    """Parse HL7 timestamp format: YYYYMMDDHHmmss[+/-offset]"""
    if not ts:
        return None
    try:
        # Remove timezone info if present (e.g., +0530 or -0400)
        ts_clean = ts.split('+')[0].split('-')[0][:14]
        return datetime.datetime.strptime(ts_clean, "%Y%m%d%H%M%S")
    except Exception as e:
        return None


def normalize_hl7_log(file_path):
    events = []
    current_message_ts = None

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Skip JSON metadata lines
            if line.startswith("{") or line.startswith("}") or line.startswith('"'):
                continue

            if line.startswith("MSH"):
                # Parse MSH segment for timestamp
                fields = line.split("|")
                if len(fields) > 6:
                    current_message_ts = parse_hl7_timestamp(fields[6])
                    
                    # Create MSH event with proper timestamp
                    msg_type = fields[8] if len(fields) > 8 else "UNKNOWN"
                    msg_control_id = fields[9] if len(fields) > 9 else ""
                    
                    events.append(
                        NormalizedEvent(
                            timestamp=current_message_ts,
                            source="HL7",
                            subsystem="HL7_MESSAGE",
                            severity="INFO",
                            event_type="HL7_MESSAGE",
                            message=f"HL7 {msg_type} message received",
                            context={
                                "message_type": msg_type,
                                "message_control_id": msg_control_id,
                                "sending_app": fields[2] if len(fields) > 2 else "",
                                "sending_facility": fields[3] if len(fields) > 3 else ""
                            },
                            raw=line
                        )
                    )

            elif line.startswith("OBX"):
                # Parse OBX (observation) segment
                fields = line.split("|")
                
                # OBX|seq|datatype|MDC_CODE^description||value|units|...
                mdc_field = fields[3] if len(fields) > 3 else ""
                value = fields[5] if len(fields) > 5 else None
                unit = fields[6] if len(fields) > 6 else None

                if "^" in mdc_field:
                    mdc_code = mdc_field.split("^")[0]
                else:
                    mdc_code = mdc_field

                meta = decode_mdc(mdc_code)

                if meta["parameter"] != "UNKNOWN":
                    events.append(
                        NormalizedEvent(
                            timestamp=current_message_ts,  # Use MSH timestamp
                            source="HL7",
                            subsystem="HL7_OBSERVATION",
                            severity="INFO",
                            event_type=meta["category"],
                            message=f"{meta['parameter']} = {value} {meta['unit']}",
                            context={
                                "parameter": meta["parameter"],
                                "domain": meta["domain"],
                                "value": value,
                                "unit": meta["unit"],
                                "mdc_code": mdc_code
                            },
                            raw=line
                        )
                    )

    return events