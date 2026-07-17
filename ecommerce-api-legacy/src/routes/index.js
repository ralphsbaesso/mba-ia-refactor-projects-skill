const { Router } = require('express');
const checkoutController = require('../controllers/checkoutController');
const reportController = require('../controllers/reportController');
const userController = require('../controllers/userController');

const router = Router();

router.post('/api/checkout', checkoutController.checkout);
router.get('/api/admin/financial-report', reportController.financialReport);
router.delete('/api/users/:id', userController.deleteUser);

module.exports = router;
