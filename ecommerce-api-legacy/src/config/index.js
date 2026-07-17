const config = {
    port: parseInt(process.env.PORT || '3000', 10),
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev_only',
    smtpUser: process.env.SMTP_USER || ''
};

module.exports = config;
