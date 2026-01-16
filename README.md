## Known Limitations

### 1. Page Reference Confusion (CRITICAL)

The model misinterprets page references as clinical values when they use comparison operators:

- Extracts "Chest pain > 37°C" when the source means "Chest pain (see Page 37)"
- Extracts "Fits ≥ 19" when the source means "(see Page 19)"

**Impact**: A patient with 18 fits would incorrectly NOT trigger the emergency pathway.

**Root cause**: Symbol-based page references (>, ≥) are being parsed as clinical thresholds.

### 2. Conditional Logic Extraction (PARTIAL)

The model may miss conditional gates in decision trees:

- Example: "Give Sodium Chloride" extracted as immediate step, but the "IF Ketones Present" condition is not explicitly linked in the logic tree

**Impact**: Treatment steps may appear unconditional when they should be gated by test results.
