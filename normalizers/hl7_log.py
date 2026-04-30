import datetime
from utils.mdc_registry import decode_mdc
from model import NormalizedEvent


def parse_hl7_timestamp(ts):
    try:
        return datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
    except Exception:
        return None


def normalize_hl7_log(file_path):
    #print("✅ HL7 normalizer called with file:", file_path)
    events = []

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("MSH"):
                continue

            fields = line.split("|")
            ts = parse_hl7_timestamp(fields[6])

            event = NormalizedEvent(
                timestamp=ts,
                source="HL7",
                subsystem="HL7_INTERFACE",
                severity="INFO",
                event_type="HL7_MESSAGE",
                message=f"HL7 {fields[8]} received",
                context={
                    "message_type": fields[8],
                    "message_control_id": fields[9],
                    "sending_app": fields[2],
                    "sending_facility": fields[3]
                },
                raw=line.strip()
            )
            
            if line.startswith("OBX"):
                fields = line.split("|")

                # HL7 OBX layout (simplified):
                # OBX|1|NM|MDC_CODE^desc||value|units|...
                mdc_field = fields[3] if len(fields) > 3 else ""
                value = fields[5] if len(fields) > 5 else None
                unit = fields[6] if len(fields) > 6 else None

                if "^" in mdc_field:
                    mdc_code = mdc_field.split("^")[0]
                else:
                    mdc_code = mdc_field

                meta = decode_mdc(mdc_code)

                if meta["parameter"] == "UNKNOWN":
                    continue  # Ignore unmapped MDC codes for now

                events.append(
                    NormalizedEvent(
                        timestamp=ts,  # reuse message timestamp
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
                        raw=line.strip()
                    )
                )

            events.append(event)
           # print("🔎 HL7 events created:", len(events))
            """ events.append(
                NormalizedEvent(
                    timestamp=None,
                    source="HL7",
                    subsystem="HL7_DEBUG",
                    severity="INFO",
                    event_type="DEBUG",
                    message="HL7 normalizer executed",
                    context={"file": file_path},
                    raw=None
                )
            ) """


    return events