# EFN Utility Adapter - Node.js SDK

An Express.js implementation of the EFN Utility Provider Adapter.

## Quickstart
1. Install dependencies: `npm install`
2. Set your secret: `export EFN_API_SECRET="your_secret"`
3. Run the server: `node index.js`

## Customization
Open `index.js` and implement your actual provider logic inside the `app.post('/efn/v1/utility/...')` route handlers.
