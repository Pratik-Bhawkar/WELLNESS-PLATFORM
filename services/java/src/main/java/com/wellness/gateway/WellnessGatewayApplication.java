package com.wellness.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Map;
import java.util.HashMap;
import java.util.Arrays;

/**
 * Mental Wellness Platform - API Gateway
 * Central orchestrator for all microservices
 */
@SpringBootApplication
@RestController
@RequestMapping("/api")
public class WellnessGatewayApplication {

    @Value("${intent.service.url:http://localhost:8001}")
    private String intentServiceUrl;

    @Value("${llm.service.url:http://localhost:8002}")  
    private String llmServiceUrl;

    @Value("${voice.service.url:http://localhost:8003}")
    private String voiceServiceUrl;

    @Value("${openai.service.url:http://localhost:8004}")
    private String openaiServiceUrl;

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    public static void main(String[] args) {
        SpringApplication.run(WellnessGatewayApplication.class, args);
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("service", "api-gateway");
        health.put("timestamp", System.currentTimeMillis());
        
        // Check downstream services
        Map<String, String> services = new HashMap<>();
        services.put("intent-service", checkServiceHealth(intentServiceUrl + "/health"));
        services.put("llm-service", checkServiceHealth(llmServiceUrl + "/health"));
        services.put("voice-service", checkServiceHealth(voiceServiceUrl + "/health"));
        services.put("openai-service", checkServiceHealth(openaiServiceUrl + "/health"));
        
        health.put("downstream_services", services);
        return ResponseEntity.ok(health);
    }

    /**
     * Chat endpoint - routes to appropriate service based on intent
     */
    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@RequestBody Map<String, Object> request) {
        try {
            String message = (String) request.get("message");
            Integer userId = (Integer) request.get("user_id");
            
            if (message == null || userId == null) {
                Map<String, Object> error = new HashMap<>();
                error.put("error", "Missing required fields: message, user_id");
                return ResponseEntity.badRequest().body(error);
            }
            
            // Step 1: Classify intent
            Map<String, Object> intentRequest = new HashMap<>();
            intentRequest.put("message", message);
            intentRequest.put("user_id", userId);
            
            RestTemplate restTemplate = restTemplate();
            
            try {
                ResponseEntity<Map> intentResponse = restTemplate.postForEntity(
                    intentServiceUrl + "/classify", intentRequest, Map.class);
                
                Map<String, Object> intent = intentResponse.getBody();
                String intentType = (String) intent.get("intent");
                String suggestedService = (String) intent.get("suggested_service");
                
                // Step 2: Route to appropriate service based on intent
                Map<String, Object> chatRequest = new HashMap<>();
                chatRequest.put("message", message);
                chatRequest.put("user_id", userId);
                chatRequest.put("context", intentType);
                
                String targetUrl;
                if ("crisis".equals(intentType)) {
                    // Crisis situations go to OpenAI service for professional responses
                    targetUrl = openaiServiceUrl + "/chat";
                } else if ("navigation".equals(intentType)) {
                    // Navigation goes to local LLM
                    targetUrl = llmServiceUrl + "/chat";
                } else {
                    // Other therapy types go to OpenAI
                    targetUrl = openaiServiceUrl + "/chat";
                }
                
                ResponseEntity<Map> chatResponse = restTemplate.postForEntity(
                    targetUrl, chatRequest, Map.class);
                
                Map<String, Object> response = new HashMap<>();
                response.put("message", chatResponse.getBody().get("response"));
                response.put("intent", intent);
                response.put("service_used", targetUrl);
                response.put("confidence", intent.get("confidence"));
                
                return ResponseEntity.ok(response);
                
            } catch (Exception e) {
                // Fallback to local LLM if services are down
                Map<String, Object> fallbackRequest = new HashMap<>();
                fallbackRequest.put("message", message);
                fallbackRequest.put("user_id", userId);
                
                try {
                    ResponseEntity<Map> fallbackResponse = restTemplate.postForEntity(
                        llmServiceUrl + "/chat", fallbackRequest, Map.class);
                    
                    Map<String, Object> response = new HashMap<>();
                    response.put("message", fallbackResponse.getBody().get("response"));
                    response.put("service_used", "fallback-llm");
                    response.put("note", "Primary services unavailable, using fallback");
                    
                    return ResponseEntity.ok(response);
                } catch (Exception fallbackError) {
                    Map<String, Object> error = new HashMap<>();
                    error.put("error", "All services unavailable");
                    error.put("message", "I'm temporarily unavailable. Please try again later.");
                    return ResponseEntity.ok(error);
                }
            }
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Get available services and their status
     */
    @GetMapping("/services")
    public ResponseEntity<Map<String, Object>> getServices() {
        Map<String, Object> services = new HashMap<>();
        
        Map<String, String> serviceStatus = new HashMap<>();
        serviceStatus.put("intent-classification", checkServiceHealth(intentServiceUrl + "/health"));
        serviceStatus.put("local-llm", checkServiceHealth(llmServiceUrl + "/health"));
        serviceStatus.put("voice-processing", checkServiceHealth(voiceServiceUrl + "/health"));
        serviceStatus.put("openai-integration", checkServiceHealth(openaiServiceUrl + "/health"));
        
        services.put("services", serviceStatus);
        services.put("gateway_status", "operational");
        
        return ResponseEntity.ok(services);
    }

    private String checkServiceHealth(String healthUrl) {
        try {
            RestTemplate restTemplate = restTemplate();
            ResponseEntity<String> response = restTemplate.getForEntity(healthUrl, String.class);
            return response.getStatusCode().is2xxSuccessful() ? "healthy" : "unhealthy";
        } catch (Exception e) {
            return "unavailable";
        }
    }
}