# EFN Utility Adapter - Java SDK

A Spring Boot 3 implementation of the EFN Utility Provider Adapter.

## Quickstart
1. Set your secret: `export EFN_API_SECRET="your_secret"`
2. Run the server: `./mvnw spring-boot:run`

## Customization
Open `src/main/java/com/elfort/efn/utility/Application.java` and implement the `@PostMapping` endpoints with your business logic.
