package com.elfort.efn.utility.example;

import com.elfort.efn.utility.EFNUtilityAutoConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

/**
 * Example Spring Boot application bootstrapping the EFN Utility Adapter.
 *
 * <h2>Running</h2>
 * <pre>{@code
 * export EFN_API_SECRET=your_secret_from_efn
 * mvn spring-boot:run
 * }</pre>
 *
 * <p>The adapter will start on port 8080 and expose:
 * <ul>
 *   <li>{@code POST http://localhost:8080/efn/v1/utility/validate}</li>
 *   <li>{@code POST http://localhost:8080/efn/v1/utility/dispense}</li>
 *   <li>{@code GET  http://localhost:8080/efn/v1/utility/transaction/{ref}/status}</li>
 * </ul>
 */
@SpringBootApplication
@Import(EFNUtilityAutoConfiguration.class)
public class ExampleApplication {

    public static void main(String[] args) {
        SpringApplication.run(ExampleApplication.class, args);
    }
}
