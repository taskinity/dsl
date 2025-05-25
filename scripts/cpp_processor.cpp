/**
 * C++ High-Performance Post-Processor
 * Optimized algorithms for real-time processing
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <map>
#include <sstream>

// Simple JSON-like structure for this example
struct Detection {
    std::string object_type;
    double confidence;
    std::vector<double> bbox;
    std::string position;
};

struct ProcessingResult {
    std::vector<Detection> optimized_detections;
    double processing_time_ms;
    int original_count;
    int filtered_count;
    std::string algorithm_used;
};

class CPPPostProcessor {
private:
    double nms_threshold;
    double confidence_threshold;
    std::string algorithm;

public:
    CPPPostProcessor() {
        // Load configuration from environment variables
        nms_threshold = std::getenv("CONFIG_NMS_THRESHOLD") ? 
            std::stod(std::getenv("CONFIG_NMS_THRESHOLD")) : 0.5;
        confidence_threshold = std::getenv("CONFIG_CONFIDENCE_THRESHOLD") ? 
            std::stod(std::getenv("CONFIG_CONFIDENCE_THRESHOLD")) : 0.6;
        algorithm = std::getenv("CONFIG_ALGORITHM") ? 
            std::getenv("CONFIG_ALGORITHM") : "fast_nms";
    }

    ProcessingResult processDetections(const std::vector<Detection>& detections) {
        auto start = std::chrono::high_resolution_clock::now();
        
        std::vector<Detection> filtered = filterByConfidence(detections);
        std::vector<Detection> optimized;
        
        if (algorithm == "fast_nms") {
            optimized = fastNonMaxSuppression(filtered);
        } else if (algorithm == "sort_confidence") {
            optimized = sortByConfidence(filtered);
        } else {
            optimized = filtered;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        ProcessingResult result;
        result.optimized_detections = optimized;
        result.processing_time_ms = duration.count() / 1000.0;
        result.original_count = detections.size();
        result.filtered_count = optimized.size();
        result.algorithm_used = algorithm;
        
        return result;
    }

private:
    std::vector<Detection> filterByConfidence(const std::vector<Detection>& detections) {
        std::vector<Detection> filtered;
        for (const auto& det : detections) {
            if (det.confidence >= confidence_threshold) {
                filtered.push_back(det);
            }
        }
        return filtered;
    }

    std::vector<Detection> fastNonMaxSuppression(const std::vector<Detection>& detections) {
        if (detections.empty()) return {};

        std::vector<Detection> sorted_detections = detections;
        std::sort(sorted_detections.begin(), sorted_detections.end(),
                  [](const Detection& a, const Detection& b) {
                      return a.confidence > b.confidence;
                  });

        std::vector<Detection> result;
        std::vector<bool> suppressed(sorted_detections.size(), false);

        for (size_t i = 0; i < sorted_detections.size(); ++i) {
            if (suppressed[i]) continue;

            result.push_back(sorted_detections[i]);

            for (size_t j = i + 1; j < sorted_detections.size(); ++j) {
                if (suppressed[j]) continue;

                double iou = calculateIoU(sorted_detections[i].bbox, sorted_detections[j].bbox);
                if (iou > nms_threshold) {
                    suppressed[j] = true;
                }
            }
        }

        return result;
    }

    std::vector<Detection> sortByConfidence(const std::vector<Detection>& detections) {
        std::vector<Detection> sorted_detections = detections;
        std::sort(sorted_detections.begin(), sorted_detections.end(),
                  [](const Detection& a, const Detection& b) {
                      return a.confidence > b.confidence;
                  });
        return sorted_detections;
    }

    double calculateIoU(const std::vector<double>& box1, const std::vector<double>& box2) {
        if (box1.size() < 4 || box2.size() < 4) return 0.0;

        double x1 = std::max(box1[0], box2[0]);
        double y1 = std::max(box1[1], box2[1]);
        double x2 = std::min(box1[2], box2[2]);
        double y2 = std::min(box1[3], box2[3]);

        if (x2 <= x1 || y2 <= y1) return 0.0;

        double intersection = (x2 - x1) * (y2 - y1);
        double area1 = (box1[2] - box1[0]) * (box1[3] - box1[1]);
        double area2 = (box2[2] - box2[0]) * (box2[3] - box2[1]);
        double union_area = area1 + area2 - intersection;

        return union_area > 0 ? intersection / union_area : 0.0;
    }
};

// Simple JSON parsing (in real implementation, use proper JSON library)
std::vector<Detection> parseDetections(const std::string& json_str) {
    std::vector<Detection> detections;
    
    // This is a simplified parser - in production use nlohmann/json or similar
    // For demo purposes, create mock detections
    Detection det1;
    det1.object_type = "person";
    det1.confidence = 0.85;
    det1.bbox = {100, 100, 200, 300};
    det1.position = "center";
    
    Detection det2;
    det2.object_type = "car";
    det2.confidence = 0.92;
    det2.bbox = {300, 150, 450, 280};
    det2.position = "right";
    
    detections.push_back(det1);
    detections.push_back(det2);
    
    return detections;
}

std::string formatOutput(const ProcessingResult& result) {
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"timestamp\": \"2024-01-01T12:00:00Z\",\n";
    oss << "  \"processor\": \"cpp_postprocessor\",\n";
    oss << "  \"algorithm_used\": \"" << result.algorithm_used << "\",\n";
    oss << "  \"processing_time_ms\": " << result.processing_time_ms << ",\n";
    oss << "  \"original_count\": " << result.original_count << ",\n";
    oss << "  \"filtered_count\": " << result.filtered_count << ",\n";
    oss << "  \"optimized_detections\": [\n";
    
    for (size_t i = 0; i < result.optimized_detections.size(); ++i) {
        const auto& det = result.optimized_detections[i];
        oss << "    {\n";
        oss << "      \"object_type\": \"" << det.object_type << "\",\n";
        oss << "      \"confidence\": " << det.confidence << ",\n";
        oss << "      \"position\": \"" << det.position << "\",\n";
        oss << "      \"bbox\": [" << det.bbox[0] << ", " << det.bbox[1] 
            << ", " << det.bbox[2] << ", " << det.bbox[3] << "]\n";
        oss << "    }";
        if (i < result.optimized_detections.size() - 1) oss << ",";
        oss << "\n";
    }
    
    oss << "  ]\n";
    oss << "}\n";
    
    return oss.str();
}

int main(int argc, char* argv[]) {
    std::string input_file;
    std::string output_file;
    
    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg.find("--input=") == 0) {
            input_file = arg.substr(8);
        } else if (arg.find("--output=") == 0) {
            output_file = arg.substr(9);
        }
    }
    
    if (input_file.empty()) {
        std::cerr << "Error: Input file required (--input=file.json)" << std::endl;
        return 1;
    }
    
    try {
        // Read input file
        std::ifstream file(input_file);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open input file: " << input_file << std::endl;
            return 1;
        }
        
        std::string json_content((std::istreambuf_iterator<char>(file)),
                                 std::istreambuf_iterator<char>());
        file.close();
        
        // Parse detections
        std::vector<Detection> detections = parseDetections(json_content);
        
        // Process with C++ optimizer
        CPPPostProcessor processor;
        ProcessingResult result = processor.processDetections(detections);
        
        // Format output
        std::string output = formatOutput(result);
        
        // Write output
        if (!output_file.empty()) {
            std::ofstream outfile(output_file);
            if (outfile.is_open()) {
                outfile << output;
                outfile.close();
            } else {
                std::cerr << "Error: Cannot write to output file: " << output_file << std::endl;
                return 1;
            }
        } else {
            std::cout << output;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}