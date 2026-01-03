//! EDI format detection and parsing module.
//!
//! Supports ANSI X12 and EDIFACT formats.

use std::io::{BufReader, Read};

/// ISA has fixed width elements. These positions should all have the same separator.
/// 103 is the official element separator position.
const ISA_ELEMENT_SEP_POSITIONS: [usize; 16] = [
    3, 6, 17, 20, 31, 34, 50, 53, 69, 76, 81, 83, 89, 99, 101, 103,
];

/// Separator configuration for EDI documents.
#[derive(Debug, Clone, PartialEq)]
pub struct Sep {
    /// Element separator (field separator)
    pub element: char,
    /// Segment separator (line terminator)
    pub segment: char,
    /// Subelement separator (composite element separator)
    pub subelement: char,
    /// Suffix between ISA header and GS segment (or UNA and UNB)
    pub suffix: String,
    /// Release/escape character (EDIFACT uses `?`)
    pub release: Option<char>,
    /// Escape character (for X12, currently unused)
    pub escape: Option<char>,
    /// Repetition separator (newer formats)
    pub repetition: Option<char>,
    /// Whether file has CRLF inserted every 80 characters
    pub hard_wrap: bool,
}

impl Sep {
    /// Create a new separator configuration with required fields.
    pub fn new(element: char, segment: char, subelement: char, suffix: String) -> Self {
        Sep {
            element,
            segment,
            subelement,
            suffix,
            release: None,
            escape: None,
            repetition: None,
            hard_wrap: false,
        }
    }
}

/// Detect EDI format and extract separator configuration from text.
///
/// Supports:
/// - ANSI X12 (starts with "ISA")
/// - EDIFACT with UNA header (starts with "UNA")
/// - EDIFACT without UNA header (starts with "UNB")
pub fn detect(text: &str) -> Option<Sep> {
    let bytes = text.as_bytes();

    // EDI X12: begins with ISA (106 chars) followed by a GS segment
    if text.starts_with("ISA") && bytes.len() >= 110 {
        return detect_x12(text, bytes);
    }

    // EDIFACT UNA: begins with UNA followed by UNB or UNG
    if text.starts_with("UNA") && bytes.len() >= 13 {
        if let Some(pos) = text[3..13.min(text.len())].find("UN") {
            return detect_edifact_una(text, pos + 3);
        }
    }

    // EDIFACT no UNA: begins with UNB followed by UNH
    if text.starts_with("UNB") && bytes.len() >= 13 {
        if text[3..13.min(text.len())].contains("UN") {
            return detect_edifact_no_una(text);
        }
    }

    eprintln!(
        "Found something that doesn't look like EDI: {:?}",
        &text[..8.min(text.len())]
    );
    None
}

/// Detect ANSI X12 format separators.
fn detect_x12(text: &str, bytes: &[u8]) -> Option<Sep> {
    // Check if GS is in expected position
    let gs_range = &text[106..110.min(text.len())];
    if !gs_range.contains("GS") {
        print_x12_error(text);
        return None;
    }

    // Verify all element separator positions have the same character
    let first_sep = bytes[3] as char;
    for &pos in &ISA_ELEMENT_SEP_POSITIONS {
        if pos >= bytes.len() || bytes[pos] as char != first_sep {
            print_x12_error(text);
            return None;
        }
    }

    // Find GS position for suffix
    let gs_pos = text[106..].find("GS").map(|p| p + 106).unwrap_or(106);
    let suffix = text[106..gs_pos].to_string();

    // Extract separators from positions 103-105
    let element = bytes[103] as char;
    let subelement = bytes[104] as char;
    let segment = bytes[105] as char;

    // X12 before repetition has 'U' at position 82
    let repetition = if bytes[82] as char != 'U' {
        Some(bytes[82] as char)
    } else {
        None
    };

    let mut sep = Sep::new(element, segment, subelement, suffix);
    sep.repetition = repetition;

    // Check for hard wrap
    detect_hard_wrap(text, &mut sep);

    Some(sep)
}

/// Detect EDIFACT format with UNA header.
fn detect_edifact_una(text: &str, un_pos: usize) -> Option<Sep> {
    let bytes = text.as_bytes();

    // UNA header: UNA:+.? '
    // Position 3: subelement (:)
    // Position 4: element (+)
    // Position 5: decimal (.)
    // Position 6: release (?)
    // Position 7: repetition (space if not used)
    // Position 8: segment (')
    let subelement = bytes[3] as char;
    let element = bytes[4] as char;
    let release = bytes[6] as char;
    let segment = bytes[8] as char;

    // Find UN position for suffix
    let suffix = text[9..un_pos].to_string();

    // Repetition separator (space means not used)
    let repetition = if bytes[7] as char != ' ' {
        Some(bytes[7] as char)
    } else {
        None
    };

    let mut sep = Sep::new(element, segment, subelement, suffix);
    sep.release = Some(release);
    sep.repetition = repetition;

    // Check for hard wrap
    detect_hard_wrap(text, &mut sep);

    Some(sep)
}

/// Detect EDIFACT format without UNA header (uses defaults).
fn detect_edifact_no_una(text: &str) -> Option<Sep> {
    // Default EDIFACT separators
    let element = '+';
    let subelement = ':';
    let segment = '\'';
    let release = '?';
    let repetition = '*';

    // Find suffix between first segment terminator and next UN segment
    let suffix = if let Some(seg_pos) = text.find('\'') {
        // Look for "UN" after the first segment terminator
        if let Some(un_pos) = text[seg_pos + 1..].find("UN") {
            text[seg_pos + 1..seg_pos + 1 + un_pos].to_string()
        } else {
            String::new()
        }
    } else {
        String::new()
    };

    let mut sep = Sep::new(element, segment, subelement, suffix);
    sep.release = Some(release);
    sep.repetition = Some(repetition);

    // Check for hard wrap
    detect_hard_wrap(text, &mut sep);

    Some(sep)
}

/// Detect if the file has hard-wrapped lines (CRLF every 80 characters).
fn detect_hard_wrap(text: &str, sep: &mut Sep) {
    let bytes = text.as_bytes();
    if bytes.len() > 246
        && bytes[80] == b'\r'
        && bytes[81] == b'\n'
        && bytes[162] == b'\r'
        && bytes[163] == b'\n'
        && bytes[244] == b'\r'
        && bytes[245] == b'\n'
    {
        sep.hard_wrap = true;
    }
}

/// Print X12 ISA header error message.
fn print_x12_error(text: &str) {
    let isa_example = "ISA*00*          *00*          *ZZ*SOMEBODYELSE   *ZZ*MAYBEYOU       *171231*2359*U*00401*000012345*0*P*:~";
    eprintln!("Invalid X12 ISA Header (expected 16 fixed width fields, 106 characters wide)");
    eprintln!("Expected: {}", isa_example);
    eprintln!("Received: {}", &text[..106.min(text.len())]);
}

/// Iterator that reads an EDI document and yields lines/segments.
pub struct EdiDocumentReader<R: Read> {
    reader: BufReader<R>,
    sep: Sep,
    buffer: Vec<u8>,
    done: bool,
}

impl<R: Read> EdiDocumentReader<R> {
    /// Create a new reader with detected separators.
    pub fn new(reader: R, sep: Sep) -> Self {
        EdiDocumentReader {
            reader: BufReader::new(reader),
            sep,
            buffer: Vec::with_capacity(1024),
            done: false,
        }
    }
}

impl<R: Read> Iterator for EdiDocumentReader<R> {
    type Item = String;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }

        let segment_byte = self.sep.segment as u8;
        let release_byte = self.sep.release.map(|c| c as u8);

        loop {
            let mut byte = [0u8; 1];
            match self.reader.read(&mut byte) {
                Ok(0) => {
                    // EOF
                    self.done = true;
                    if self.buffer.is_empty() {
                        return None;
                    }
                    let line = String::from_utf8_lossy(&self.buffer).trim().to_string();
                    self.buffer.clear();
                    return if line.is_empty() { None } else { Some(line) };
                }
                Ok(_) => {
                    let b = byte[0];

                    // Skip CR/LF if hard_wrap is enabled
                    if self.sep.hard_wrap && (b == b'\r' || b == b'\n') {
                        continue;
                    }

                    self.buffer.push(b);

                    // Check for segment terminator (not preceded by escape/release character)
                    if b == segment_byte {
                        let escaped = if let Some(rel) = release_byte {
                            self.buffer.len() >= 2 && self.buffer[self.buffer.len() - 2] == rel
                        } else {
                            false
                        };

                        if !escaped {
                            let line = String::from_utf8_lossy(&self.buffer).trim().to_string();
                            self.buffer.clear();
                            if !line.is_empty() {
                                return Some(line);
                            }
                        }
                    }
                }
                Err(_) => {
                    self.done = true;
                    return None;
                }
            }
        }
    }
}

/// Read an EDI document from a string and return an iterator of segments.
pub fn read_document_str(text: &str) -> Option<impl Iterator<Item = String>> {
    let sep = detect(text)?;
    Some(EdiDocumentReader::new(std::io::Cursor::new(text.to_string()), sep))
}

/// Read an EDI document from a reader, using the provided text for detection.
pub fn read_document<R: Read>(reader: R, peek_text: &str, filename: &str) -> Option<impl Iterator<Item = String>> {
    let sep = detect(peek_text);
    match sep {
        Some(s) => Some(EdiDocumentReader::new(reader, s)),
        None => {
            eprintln!("Skipping...{}", filename);
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_x12() {
        let isa = "ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~GS*PO*test";
        let sep = detect(isa).unwrap();
        assert_eq!(sep.element, '*');
        assert_eq!(sep.segment, '~');
        assert_eq!(sep.subelement, '^');
        assert!(sep.repetition.is_none());
    }

    #[test]
    fn test_detect_edifact_una() {
        let una = "UNA:+.? 'UNB+IATB:1+test";
        let sep = detect(una).unwrap();
        assert_eq!(sep.element, '+');
        assert_eq!(sep.segment, '\'');
        assert_eq!(sep.subelement, ':');
        assert_eq!(sep.release, Some('?'));
    }

    #[test]
    fn test_detect_edifact_no_una() {
        // UNB without UNA header - needs "UN" within positions 3-13 (e.g., "UNOC" syntax ID)
        let unb = "UNB+UNOC:3+sender:id+receiver:id+date:time+ref'UNH+1+ORDERS:D:96A:UN'";
        let sep = detect(unb).unwrap();
        assert_eq!(sep.element, '+');
        assert_eq!(sep.segment, '\'');
        assert_eq!(sep.subelement, ':');
        assert_eq!(sep.release, Some('?'));
    }
}
