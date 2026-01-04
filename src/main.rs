//! EDIcat - Print and concatenate EDI files.
//!
//! A command-line utility that formats EDI files by adding newlines between segments.

use std::fs::File;
use std::io::{self, BufRead, BufReader, IsTerminal, Read, Write};
use std::process::ExitCode;

use clap::Parser;

use edicat::edi::{detect, EdiDocumentReader};

/// Print and concatenate EDI.
#[derive(Parser, Debug)]
#[command(name = "edicat", version, about, long_about = None)]
struct Args {
    /// Filename(s) or - for stdin
    #[arg(value_name = "filenames")]
    filenames: Vec<String>,

    /// Number the output lines, starting at 1.
    #[arg(short = 'n', long = "lineno")]
    line_numbers: bool,
}

/// Process files and output formatted EDI.
fn output(filenames: &[String], line_numbers: bool) -> i32 {
    let mut ret_code = 0;
    let stdout = io::stdout();
    let mut handle = stdout.lock();

    let files: Vec<String> = if filenames.is_empty() {
        vec!["-".to_string()]
    } else {
        filenames.to_vec()
    };

    for filename in &files {
        let mut lineno: usize = 0;
        match process_file(filename, line_numbers, &mut lineno, &mut handle) {
            Ok(count) => {
                if count == 0 {
                    ret_code = 1;
                }
            }
            Err(e) => {
                if e.kind() == io::ErrorKind::BrokenPipe {
                    // Suppress broken pipe errors (e.g., when piped to `head`)
                    break;
                }
                eprintln!("Error processing {}: {}", filename, e);
                ret_code = 1;
            }
        }
    }

    ret_code
}

/// Process a single file and write output.
fn process_file(
    filename: &str,
    line_numbers: bool,
    lineno: &mut usize,
    handle: &mut io::StdoutLock,
) -> io::Result<usize> {
    let mut count = 0;

    if filename == "-" {
        // Read from stdin
        let stdin = io::stdin();
        let mut stdin_lock = stdin.lock();

        // Peek at the beginning to detect format
        let mut peek_buf = vec![0u8; 512];
        let peek_len = stdin_lock.read(&mut peek_buf)?;
        peek_buf.truncate(peek_len);

        let peek_text = String::from_utf8_lossy(&peek_buf);
        if let Some(sep) = detect(&peek_text) {
            // Create a chain of the peeked bytes and the rest of stdin
            let combined = std::io::Cursor::new(peek_buf).chain(stdin_lock);
            let reader = EdiDocumentReader::new(combined, sep);

            for line in reader {
                write_line(handle, &line, *lineno, line_numbers)?;
                *lineno += 1;
                count += 1;
            }
        } else {
            eprintln!("Skipping...stdin");
        }
    } else {
        // Read from file
        let file = File::open(filename)?;
        let mut buf_reader = BufReader::new(file);

        // Peek at the beginning to detect format
        let peek_buf = buf_reader.fill_buf()?;
        let peek_text = String::from_utf8_lossy(peek_buf);
        let peek_owned = peek_text.to_string();

        if let Some(sep) = detect(&peek_owned) {
            let reader = EdiDocumentReader::new(buf_reader, sep);

            for line in reader {
                write_line(handle, &line, *lineno, line_numbers)?;
                *lineno += 1;
                count += 1;
            }
        } else {
            eprintln!("Skipping...{}", filename);
        }
    }

    Ok(count)
}

/// Write a line with optional line number.
fn write_line(
    handle: &mut io::StdoutLock,
    line: &str,
    lineno: usize,
    line_numbers: bool,
) -> io::Result<()> {
    if line_numbers {
        writeln!(handle, "{:>6}\t{}", lineno + 1, line)
    } else {
        writeln!(handle, "{}", line)
    }
}

fn main() -> ExitCode {
    let args = Args::parse();

    // If no filenames and stdin is a TTY, show help and exit
    if args.filenames.is_empty() && io::stdin().is_terminal() {
        // Re-parse with --help to show help message
        let _ = Args::try_parse_from(["edicat", "--help"]);
        return ExitCode::from(1);
    }

    let code = output(&args.filenames, args.line_numbers);
    ExitCode::from(code as u8)
}
