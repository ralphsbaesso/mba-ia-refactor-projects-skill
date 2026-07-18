const reportModel = require('../models/reportModel');
const { PAYMENT_STATUS } = require('./checkoutService');

// Agrega as linhas do JOIN no mesmo formato de resposta do relatório legado:
// [{ course, revenue, students: [{ student, paid }] }]
async function financialReport(db) {
    const rows = await reportModel.financialRows(db);
    const byCourse = new Map();

    for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
        }
        if (row.enrollment_id === null) continue;

        const courseData = byCourse.get(row.course_id);
        if (row.status === PAYMENT_STATUS.PAID) {
            courseData.revenue += row.amount;
        }
        courseData.students.push({
            student: row.student_name || 'Unknown',
            paid: row.amount != null ? row.amount : 0
        });
    }

    return [...byCourse.values()];
}

module.exports = { financialReport };
