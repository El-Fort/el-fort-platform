package com.elfort.efn.utility;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Auto-configuration for the EFN Utility Adapter SDK.
 *
 * <p>Include this configuration class (or import it) in your Spring Boot application.
 * The SDK expects:
 * <ol>
 *   <li>An {@link EFNUtilityAdapter} bean registered in the application context</li>
 *   <li>Environment variable {@code EFN_API_SECRET} set to your shared EFN secret</li>
 * </ol>
 *
 * <h2>Minimal Setup</h2>
 * <pre>{@code
 * @SpringBootApplication
 * @Import(EFNUtilityAutoConfiguration.class)
 * public class Application {
 *     public static void main(String[] args) { SpringApplication.run(Application.class, args); }
 *
 *     @Bean
 *     public EFNUtilityAdapter myAdapter() { return new MyUtilityAdapter(); }
 * }
 * }</pre>
 */
@Configuration
public class EFNUtilityAutoConfiguration {

    @Value("${EFN_API_SECRET:}")
    private String apiSecret;

    /**
     * Register the HMAC signature filter for all {@code /efn/v1/utility/**} paths.
     */
    @Bean
    public FilterRegistrationBean<EFNSignatureFilter> efnSignatureFilter() {
        if (apiSecret == null || apiSecret.isBlank()) {
            throw new IllegalStateException(
                "EFN_API_SECRET environment variable is not set. " +
                "Set it to your shared secret provided by EFN."
            );
        }
        FilterRegistrationBean<EFNSignatureFilter> bean = new FilterRegistrationBean<>();
        bean.setFilter(new EFNSignatureFilter(apiSecret));
        bean.addUrlPatterns("/efn/v1/utility/*");
        bean.setOrder(1);
        return bean;
    }

    /**
     * Register the EFN REST controller (requires an EFNUtilityAdapter bean).
     */
    @Bean
    public EFNUtilityController efnUtilityController(EFNUtilityAdapter adapter) {
        return new EFNUtilityController(adapter);
    }
}
