const express = require('express');
const crypto = require('crypto');
const app = express();

const API_SECRET = process.env.EFN_API_SECRET || "test_secret_key_efn";

app.use(express.json({
    verify: (req, res, buf) => { req.rawBody = buf; }
}));

function verifySignature(req, res, next) {
    if (!req.path.startsWith('/efn/v1/utility')) return next();
    
    const ts = req.headers['x-efn-timestamp'];
    const sig = req.headers['x-efn-signature']?.replace('v1=', '');
    
    if (Math.abs(Math.floor(Date.now() / 1000) - parseInt(ts)) > 300) {
        return res.status(401).json({ error: "Expired request" });
    }
    
    const hmac = crypto.createHmac('sha256', API_SECRET);
    hmac.update(ts + ".");
    hmac.update(req.rawBody);
    const expected = hmac.digest('hex');
    
    if (expected !== sig) {
        return res.status(401).json({ error: "Invalid signature" });
    }
    next();
}

app.use(verifySignature);

app.post('/efn/v1/utility/validate', (req, res) => {
    // TODO: Implement DB lookup
    if (req.body.customer_ref === "12345678901") {
        res.json({ is_valid: true, customer_name: "John Doe", minimum_amount: 1000 });
    } else {
        res.json({ is_valid: false });
    }
});

app.post('/efn/v1/utility/dispense', (req, res) => {
    // TODO: Implement dispensation
    res.json({
        status: "success",
        dispense_ref: "UTL-998877",
        value_token: "4455-6677-8899-0011-2233",
        receipt_details: { units: (req.body.amount / 100) + " units" }
    });
});

app.get('/efn/v1/utility/transaction/:ref/status', (req, res) => {
    res.json({ status: "success", value_token: "4455-6677-8899-0011-2233" });
});

app.listen(3000, () => console.log('Utility adapter running on 3000'));
