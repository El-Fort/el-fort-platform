package com.elfort.efn.utility;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.HashMap;

@SpringBootApplication
@RestController
@RequestMapping("/efn/v1/utility")
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @PostMapping("/validate")
    public Map<String, Object> validate(@RequestBody Map<String, Object> req) {
        Map<String, Object> res = new HashMap<>();
        res.put("is_valid", true);
        res.put("customer_name", "John Doe");
        return res;
    }

    @PostMapping("/dispense")
    public Map<String, Object> dispense(@RequestBody Map<String, Object> req) {
        Map<String, Object> res = new HashMap<>();
        res.put("status", "success");
        res.put("value_token", "1234-5678");
        return res;
    }
}
