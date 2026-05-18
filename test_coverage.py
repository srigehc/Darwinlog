from analysis.Rule_engine.coverage_summary import load_normalized_and_correlation, generate_coverage_summary

events = load_normalized_and_correlation()
summary, missing = generate_coverage_summary(events)

print('COVERAGE REPORT (MEANINGFUL EVENTS ONLY)')
print('=' * 60)
print(f"OVERALL: Total={summary['overall']['total']}, SBX={summary['overall']['SBX_coverage_pct']}%, DoCom={summary['overall']['DOCOM_coverage_pct']}%, HL7={summary['overall']['HL7_coverage_pct']}%")
print()
print('BY EVENT TYPE:')
for t in sorted(summary['by_type'].keys()):
    s = summary['by_type'][t]
    print(f"  {t:20} Total={s['total']:3d}, SBX={s['SBX_coverage_pct']:5.1f}%, DoCom={s['DOCOM_coverage_pct']:5.1f}%, HL7={s['HL7_coverage_pct']:5.1f}%")
