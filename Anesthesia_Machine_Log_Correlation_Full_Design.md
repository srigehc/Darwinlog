# Anesthesia Machine Log Correlation – End-to-End Context, Design, and Architecture

## 1. Background and Initial Context

This work focuses on **post-processing and verification of anesthesia machine logs** produced by multiple subsystems. The logs are generated as part of normal machine operation during clinical use.

The primary objective is **not analytics, prediction, or AI-first modeling**, but a **deterministic verification task**:

> *Ensure that user actions captured at the SYSTEM level are consistently reflected in downstream logs (SBX, Do‑Com, HL7), and identify where coverage is missing or intentionally absent.*

This document consolidates:
- the original architectural intent,
- the current normalized state of the logs,
- the correct correlation strategy,
- and the design decisions that led to the final approach.

---

## 2. Log Sources and Their Responsibilities

### 2.1 SYSTEM Logs (UI / User Interaction Logs)

**Definition**  
SYSTEM logs capture **every user interaction at the machine UI**.

Examples include:
- changing FiO2
- adjusting pressure limits
- selecting ventilation modes
- acknowledging alarms
- navigating UI screens

**Why these logs matter**  
SYSTEM logs represent *what the user explicitly did*. They are the only authoritative source for user actions.

**Key property**  
SYSTEM is the **baseline and anchor** for correlation.

---

### 2.2 SBX Logs (Internal State + Patient Data)

**Definition**  
SBX logs are the richest internal logs produced by the machine. They include:
- device configuration
- internal state transitions
- alarm limits
- ventilation parameters
- patient vitals and derived values

**Important characteristics**
- High volume
- One SYSTEM action may affect multiple SBX parameters
- Periodic refreshes and snapshots are expected

**Role in correlation**  
SBX should reflect *most* SYSTEM actions, but not necessarily in a 1:1 mapping.

---

### 2.3 Do‑Com Logs (Control / Configuration Interface)

**Definition**  
Do‑Com logs represent the command‑level configuration and control interface of the machine.

They typically include lines such as:
- `set Plimit = 45`
- `set FiO2 = 75`
- `set Gas Control Mode = e`

**Important characteristics**
- Less rich than SBX
- Structured in timestamped blocks
- Multiple `set` entries per timestamp

**Role in correlation**  
Do‑Com is expected to capture **most configuration‑related SYSTEM actions**.

---

### 2.4 HL7 Logs (External / EMR Output)

**Definition**  
HL7 logs represent data sent externally to clinical information systems (EMR).

These logs include:
- selected device settings
- patient vitals
- active ventilation modes

**Important characteristics**
- Intentionally limited in scope
- Reporting‑oriented, not complete
- Not all SYSTEM actions are expected to appear

**Role in correlation**  
HL7 provides **external visibility**, not full coverage.

---

## 3. High-Level Architecture (Simple View)

```
SYSTEM Log (Raw)          Communication Output (HL7 etc)
       │                            │
       ▼                            ▼
┌────────────────────────────────────────┐
│ 1️⃣ Parsing & Normalization Layer      │
└────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────┐
│ 2️⃣ Event Correlation Engine            │
│    (time, event, parameter mapping)    │
└────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────┐
│ 3️⃣ Rule-Based Validation               │
│    (must-pass coverage checks)          │
└────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────┐
│ 4️⃣ AI / ML Deviation Detector          │
│    (optional, future enhancement)       │
└────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────┐
│ 5️⃣ Report & Explainability             │
└────────────────────────────────────────┘
```

This document primarily addresses **layers 1 and 2**, and defines the contract needed for layer 3.

---

## 4. Current State: Parsing and Normalization

✅ Parsing and normalization have been completed for:
- SYSTEM
- SBX
- Do‑Com
- HL7

All logs now share:
- a common timestamp format
- a unified JSON structure
- normalized fields such as `source`, `event_type`, `message`, and `context`

This creates a **single unified event stream** suitable for correlation.

---

## 5. Correlation Goal (Restated Precisely)

> For **each SYSTEM event**, determine whether a corresponding or related event exists in:
> - SBX
> - Do‑Com
> - HL7

The outcome for each SYSTEM event is a **coverage result**, not a causal judgment.

---

## 6. Correct Correlation Direction

### ✅ SYSTEM-anchored correlation

```
SYSTEM event
   ├─ present in SBX ?
   ├─ present in Do‑Com ?
   └─ present in HL7 ?
```

**Why SYSTEM is the anchor**
- SYSTEM defines what must be validated
- Other logs are evaluated *against* SYSTEM events

---

## 7. Time Windows

Correlation uses **time windows** to account for propagation delays:

- SYSTEM → SBX: ±10 seconds
- SYSTEM → Do‑Com: ±10 seconds
- SYSTEM → HL7: up to +30 seconds

These windows reflect **logging and communication latency**, not causality.

---

## 8. Expected Correlation Outcomes

### Example result

```json
{
  "system_time": "2026-04-22T11:40:44.504",
  "system_event": "User set FiO2 to 75%",
  "SBX_present": true,
  "DoCom_present": true,
  "HL7_present": false
}
```

**Interpretation**
- Missing HL7 is likely expected
- SBX and Do‑Com coverage is correct

---

## 9. Coverage Expectations (By Design)

| SYSTEM Action | SBX | Do‑Com | HL7 | Comment |
|-------------|-----|--------|-----|--------|
| Set pressure limit | ✅ | ✅ | ❌ | HL7 design limitation |
| Vent mode change | ✅ | ✅ | ✅ | Must be visible everywhere |
| Alarm threshold | ✅ | ✅ | ❌ | Expected absence in HL7 |
| Gas flow | ✅ | ✅ | ✅ | Depends on mode/config |
| UI navigation | ❌ | ❌ | ❌ | Correct |

---

## 10. What This System Explicitly Does NOT Do

- Causal or intent inference
- Behavior prediction
- Clinical correctness validation
- Statistical or ML-based analytics (yet)

Those may be added later, but are **out of scope** for this phase.

---

## 11. Design Choices Summary

- ✅ SYSTEM-centric correlation
- ✅ Presence/absence validation
- ✅ Deterministic windows
- ✅ No hard-coded 1:1 mappings
- ✅ Missing ≠ defect by default

---

## 12. Final Status

- Parsing & normalization ✅ complete
- Correlation strategy ✅ defined
- Engine implementation ✅ straightforward
- Ready for coverage analysis and reporting

---
