[package]
name = "camel-processors"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "data_preprocessor"
path = "src/data_preprocessor.rs"

[[bin]]
name = "performance_analyzer"
path = "src/performance_analyzer.rs"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"
chrono = { version = "0.4", features = ["serde"] }
rayon = "1.7"
ndarray = "0.15"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"