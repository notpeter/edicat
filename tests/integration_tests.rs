//! Integration tests for edicat.

use edicat::edi::{detect, read_document_str};

#[test]
fn test_x12_linebreaks() {
    let po3040 = concat!(
        "ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~",
        "GS*PO*0011223456*999999999*950120*0147*5*X*003040~",
        "ST*850*000000001~",
        "BEG*00*SA*95018017***950118~",
        "N1*SE*UNIVERSAL WIDGETS~",
        "N3*375 PLYMOUTH PARK*SUITE 205~",
        "N4*IRVING*TX*75061~",
        "N1*ST*JIT MANUFACTURING~",
        "N3*BUILDING 3B*2001 ENTERPRISE PARK~",
        "N4*JUAREZ*CH**MEX~",
        "N1*AK*JIT MANUFACTURING~",
        "N3*400 INDUSTRIAL PARKWAY~",
        "N4*INDUSTRIAL AIRPORT*KS*66030~",
        "N1*BT*JIT MANUFACTURING~",
        "N2*ACCOUNTS  PAYABLE DEPARTMENT~",
        "N3*400 INDUSTRIAL PARKWAY~",
        "N4*INDUSTRIAL AIRPORT*KS*66030~",
        "PO1*001*4*EA*330*TE*IN*525*VN*X357-W2~",
        "PID*F****HIGH PERFORMANCE WIDGET~",
        "SCH*4*EA****002*950322~",
        "CTT*1*1~",
        "SE*20*000000001~",
        "GE*1*5~",
        "IEA*1*000000005~"
    );

    let result: Vec<String> = read_document_str(po3040).unwrap().collect();

    // Build expected: each segment on its own line
    let expected_lines: Vec<String> = po3040
        .split('~')
        .filter(|s| !s.is_empty())
        .map(|s| format!("{}~", s))
        .collect();

    assert_eq!(result, expected_lines);
}

#[test]
fn test_edifact_linebreaks() {
    let iatb = concat!(
        "UNA:+.? '",
        "UNB+IATB:1+6XPPC:ZZ+LHPPC:ZZ+940101:0950+1'",
        "UNH+1+PAORES:93:1:IA'",
        "MSG+1:45'",
        "IFT+3+XYZCOMPANY AVAILABILITY'",
        "ERC+A7V:1:AMD'",
        "IFT+3+NO MORE FLIGHTS'",
        "ODI'",
        "TVL+240493:1000::1220+FRA+JFK+DL+400+C'",
        "PDI++C:3+Y::3+F::1'",
        "APD+74C:0:::6++++++6X'",
        "TVL+240493:1740::2030+JFK+MIA+DL+081+C'",
        "PDI++C:4'",
        "APD+EM2:0:1630::6+++++++DA'",
        "UNT+13+1'",
        "UNZ+1+1'"
    );

    let result: Vec<String> = read_document_str(iatb).unwrap().collect();

    // Build expected: each segment on its own line
    let expected_lines: Vec<String> = iatb
        .split('\'')
        .filter(|s| !s.is_empty())
        .map(|s| format!("{}'", s))
        .collect();

    assert_eq!(result, expected_lines);
}

#[test]
fn test_detect_x12_separators() {
    let isa = "ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~GS*PO*test";
    let sep = detect(isa).unwrap();

    assert_eq!(sep.element, '*');
    assert_eq!(sep.segment, '~');
    assert_eq!(sep.subelement, '^');
    assert!(sep.repetition.is_none()); // 'U' means no repetition separator
    assert!(!sep.hard_wrap);
}

#[test]
fn test_detect_edifact_una_separators() {
    let una = "UNA:+.? 'UNB+IATB:1+6XPPC:ZZ+LHPPC:ZZ+940101:0950+1'";
    let sep = detect(una).unwrap();

    assert_eq!(sep.element, '+');
    assert_eq!(sep.segment, '\'');
    assert_eq!(sep.subelement, ':');
    assert_eq!(sep.release, Some('?'));
    assert!(sep.repetition.is_none()); // space means no repetition separator
    assert!(!sep.hard_wrap);
}

#[test]
fn test_detect_edifact_no_una() {
    // UNB without UNA header - needs "UN" within positions 3-13 (e.g., "UNOC" syntax ID)
    let unb = "UNB+UNOC:3+sender:id+receiver:id+date:time+ref'UNH+1+ORDERS:D:96A:UN'";
    let sep = detect(unb).unwrap();

    // Default EDIFACT separators
    assert_eq!(sep.element, '+');
    assert_eq!(sep.segment, '\'');
    assert_eq!(sep.subelement, ':');
    assert_eq!(sep.release, Some('?'));
    assert_eq!(sep.repetition, Some('*'));
    assert!(!sep.hard_wrap);
}

#[test]
fn test_invalid_edi() {
    let invalid = "NOTEDI*random*data";
    let sep = detect(invalid);
    assert!(sep.is_none());
}

#[test]
fn test_x12_with_repetition_separator() {
    // ISA with repetition separator (not 'U' at position 82)
    let isa = "ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*^*00501*000000005*0*P*:~GS*PO*test";
    let sep = detect(isa).unwrap();

    assert_eq!(sep.element, '*');
    assert_eq!(sep.segment, '~');
    assert_eq!(sep.subelement, ':');
    assert_eq!(sep.repetition, Some('^')); // Position 82 has '^' instead of 'U'
}
