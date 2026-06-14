use axum::{
    routing::{get, post},
    Router, Json, http::{Request, StatusCode}, middleware::{self, Next}, response::IntoResponse
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct ValidateReq { customer_ref: String }
#[derive(Serialize)]
struct ValidateRes { is_valid: bool, customer_name: String }

async fn validate(Json(payload): Json<ValidateReq>) -> Json<ValidateRes> {
    // TODO: Implement logic
    Json(ValidateRes { is_valid: true, customer_name: "John Doe".to_string() })
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/efn/v1/utility/validate", post(validate));
        // TODO: add dispense and status

    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
