# EFN Utility Adapter - Rust SDK

An Axum implementation of the EFN Utility Provider Adapter.

## Quickstart
1. Set your secret: `export EFN_API_SECRET="your_secret"`
2. Run the server: `cargo run`

## Customization
Open `src/main.rs` and implement the `validate` and `dispense` handlers to integrate with your internal systems.
