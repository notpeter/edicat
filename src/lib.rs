//! EDIcat - Print and concatenate EDI files.
//!
//! A library for parsing and formatting EDI (Electronic Data Interchange) files.
//! Supports ANSI X12 and EDIFACT formats.

pub mod edi;

pub use edi::{detect, read_document, read_document_str, EdiDocumentReader, Sep};

/// Version of the edicat library.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
