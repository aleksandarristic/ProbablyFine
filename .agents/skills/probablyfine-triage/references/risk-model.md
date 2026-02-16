# Risk Model Summary

Custom deterministic risk score is integer 0..100:

```
RiskScoreRaw = 100 * (
  0.30*SeveritySub +
  0.25*ThreatSub +
  0.15*ExposureSub +
  0.15*ImpactReqSub +
  0.10*RuntimeSub +
  0.05*FixSub
)
```

`RiskScore = round(RiskScoreRaw)` clamped to 0..100.

Subscores:
- `SeveritySub`: Critical 1.00, High 0.75, Medium 0.50, Low 0.25, Unknown 0.10
- `ThreatSub`: E:A 1.00, E:F 0.75, E:P 0.50, E:U 0.25, E:X 0.10
- `ExposureSub`: MAV:N 1.00, MAV:A 0.60, MAV:L 0.30, MAV:X 0.50
- `ImpactReqSub`: any H 1.00, any M 0.70, all L 0.40, else 0.50
- `RuntimeSub`: runtime 1.00, unknown 0.70, build-only 0.30
- `FixSub`: fix known 1.00, fix unknown 0.60
