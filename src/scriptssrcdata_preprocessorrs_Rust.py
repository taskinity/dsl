//! High-performance data preprocessing in Rust
//! Optimized for SIMD operations and parallel processing

use anyhow::{Context, Result};
use clap::Parser;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::time::Instant;

#[derive(Parser, Debug)]
#[command(name = "data_preprocessor")]
#[command(about = "High-performance data preprocessing")]
struct Args {
    #[arg(long)]
    input: String,
    
    #[arg(long)]
    output: Option<String>,
}

#[derive(Debug, Deserialize)]
struct InputData {
    #[serde(default)]
    data: Vec<f64>,
    #[serde(default)]
    batch_data: Vec<Vec<f64>>,
    #[serde(default)]
    config: ProcessingConfig,
}

#[derive(Debug, Deserialize)]
struct ProcessingConfig {
    #[serde(default = "default_batch_size")]
    batch_size: usize,
    #[serde(default = "default_normalize")]
    normalize: bool,
    #[serde(default = "default_parallel")]
    parallel: bool,
    #[serde(default = "default_simd")]
    simd_enabled: bool,
}

fn default_batch_size() -> usize { 32 }
fn default_normalize() -> bool { true }
fn default_parallel() -> bool { true }
fn default_simd() -> bool { true }

impl Default for ProcessingConfig {
    fn default() -> Self {
        Self {
            batch_size: default_batch_size(),
            normalize: default_normalize(),
            parallel: default_parallel(),
            simd_enabled: default_simd(),
        }
    }
}

#[derive(Debug, Serialize)]
struct ProcessingResult {
    timestamp: String,
    processor: String,
    processing_time_ms: f64,
    input_size: usize,
    output_size: usize,
    batches_processed: usize,
    preprocessed_data: Vec<Vec<f64>>,
    statistics: DataStatistics,
}

#[derive(Debug, Serialize)]
struct DataStatistics {
    mean: f64,
    std_dev: f64,
    min: f64,
    max: f64,
    total_elements: usize,
}

struct DataPreprocessor {
    config: ProcessingConfig,
}

impl DataPreprocessor {
    fn new(config: ProcessingConfig) -> Self {
        Self { config }
    }

    fn preprocess(&self, input: InputData) -> Result<ProcessingResult> {
        let start_time = Instant::now();
        
        // Determine data to process
        let data_to_process = if !input.batch_data.is_empty() {
            input.batch_data
        } else if !input.data.is_empty() {
            vec![input.data]
        } else {
            return Err(anyhow::anyhow!("No data provided"));
        };

        // Process in batches
        let batches: Vec<Vec<Vec<f64>>> = data_to_process
            .chunks(self.config.batch_size)
            .map(|chunk| chunk.to_vec())
            .collect();

        let processed_batches: Vec<Vec<f64>> = if self.config.parallel {
            batches
                .into_par_iter()
                .map(|batch| self.process_batch(batch))
                .collect()
        } else {
            batches
                .into_iter()
                .map(|batch| self.process_batch(batch))
                .collect()
        };

        // Flatten results
        let flattened: Vec<f64> = processed_batches
            .iter()
            .flatten()
            .copied()
            .collect();

        // Calculate statistics
        let stats = self.calculate_statistics(&flattened);

        // Reshape back to batches
        let final_batches: Vec<Vec<f64>> = processed_batches;

        let processing_time = start_time.elapsed().as_secs_f64() * 1000.0;

        Ok(ProcessingResult {
            timestamp: chrono::Utc::now().to_rfc3339(),
            processor: "rust_data_preprocessor".to_string(),
            processing_time_ms: processing_time,
            input_size: data_to_process.len(),
            output_size: final_batches.len(),
            batches_processed: final_batches.len(),
            preprocessed_data: final_batches,
            statistics: stats,
        })
    }

    fn process_batch(&self, batch: Vec<Vec<f64>>) -> Vec<f64> {
        let flattened: Vec<f64> = batch.into_iter().flatten().collect();
        
        if self.config.normalize {
            self.normalize_data(flattened)
        } else {
            flattened
        }
    }

    fn normalize_data(&self, data: Vec<f64>) -> Vec<f64> {
        if data.is_empty() {
            return data;
        }

        let mean = data.iter().sum::<f64>() / data.len() as f64;
        let variance = data
            .iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f64>() / data.len() as f64;
        let std_dev = variance.sqrt();

        if std_dev == 0.0 {
            return data;
        }

        if self.config.simd_enabled {
            // Use SIMD-like operations with rayon
            data.into_par_iter()
                .map(|x| (x - mean) / std_dev)
                .collect()
        } else {
            data.into_iter()
                .map(|x| (x - mean) / std_dev)
                .collect()
        }
    }

    fn calculate_statistics(&self, data: &[f64]) -> DataStatistics {
        if data.is_empty() {
            return DataStatistics {
                mean: 0.0,
                std_dev: 0.0,
                min: 0.0,
                max: 0.0,
                total_elements: 0,
            };
        }

        let mean = data.iter().sum::<f64>() / data.len() as f64;
        let variance = data
            .iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f64>() / data.len() as f64;
        let std_dev = variance.sqrt();
        let min = data.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max = data.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));

        DataStatistics {
            mean,
            std_dev,
            min,
            max,
            total_elements: data.len(),
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Read input file
    let input_content = fs::read_to_string(&args.input)
        .with_context(|| format!("Failed to read input file: {}", args.input))?;

    // Parse input JSON
    let input_data: InputData = serde_json::from_str(&input_content)
        .with_context(|| "Failed to parse input JSON")?;

    // Load configuration from environment if available
    let mut config = input_data.config;
    if let Ok(batch_size) = std::env::var("CONFIG_BATCH_SIZE") {
        config.batch_size = batch_size.parse().unwrap_or(config.batch_size);
    }
    if let Ok(normalize) = std::env::var("CONFIG_NORMALIZE") {
        config.normalize = normalize.parse().unwrap_or(config.normalize);
    }

    // Process data
    let preprocessor = DataPreprocessor::new(config);
    let result = preprocessor.preprocess(input_data)?;

    // Output results
    let output_json = serde_json::to_string_pretty(&result)
        .with_context(|| "Failed to serialize output")?;

    if let Some(output_file) = args.output {
        fs::write(&output_file, output_json)
            .with_context(|| format!("Failed to write output file: {}", output_file))?;
    } else {
        println!("{}", output_json);
    }

    Ok(())
}