// Uma única query com JOINs substitui o padrão N+1
// (1 query de cursos + 1 por curso + 2 por matrícula do código legado).
function financialRows(db) {
    return db.all(`
        SELECT c.id          AS course_id,
               c.title       AS course_title,
               e.id          AS enrollment_id,
               u.name        AS student_name,
               p.amount      AS amount,
               p.status      AS status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id, e.id
    `);
}

module.exports = { financialRows };
