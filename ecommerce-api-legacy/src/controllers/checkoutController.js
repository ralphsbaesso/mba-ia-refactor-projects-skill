const checkoutService = require('../services/checkoutService');
const { ApiError } = require('../middlewares/errorHandler');

async function checkout(req, res, next) {
    try {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;
        if (!name || !email || !courseId || !card) throw new ApiError('Bad Request', 400);

        const result = await checkoutService.checkout(req.app.locals.db, {
            name, email, password, courseId, card
        });
        res.status(200).json(result);
    } catch (err) {
        next(err);
    }
}

module.exports = { checkout };
