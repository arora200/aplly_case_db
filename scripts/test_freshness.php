<?php
define('DB_HOST', 'srv818.hstgr.io');
define('DB_NAME', 'u349538621_aplly');
define('DB_USER', 'u349538621_plato');
define('DB_PASS', 'Praxis2138');
define('DB_CHARSET', 'utf8mb4');

try {
    $pdo = new PDO('mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=' . DB_CHARSET, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);

    echo "=== CASE STUDY DATA FRESHNESS ANALYSIS ===\n\n";

    // 1. Relevance status distribution
    echo "--- 1. Distribution by relevance_status ---\n";
    $q = $pdo->query("SELECT relevance_status, COUNT(*) AS count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM case_studies), 1) AS pct FROM case_studies GROUP BY relevance_status ORDER BY count DESC");
    foreach ($q as $r) echo "  {$r['relevance_status']}: {$r['count']} ({$r['pct']}%)\n";

    // 2. Status distribution
    echo "\n--- 2. Distribution by status ---\n";
    $q = $pdo->query("SELECT status, COUNT(*) AS count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM case_studies), 1) AS pct FROM case_studies GROUP BY status ORDER BY count DESC");
    foreach ($q as $r) echo "  {$r['status']}: {$r['count']} ({$r['pct']}%)\n";

    // 3. Published cases by year
    echo "\n--- 3. Published case studies by year ---\n";
    $q = $pdo->query("SELECT YEAR(published_at) AS yr, COUNT(*) AS count FROM case_studies WHERE published_at IS NOT NULL GROUP BY yr ORDER BY yr DESC");
    foreach ($q as $r) echo "  {$r['yr']}: {$r['count']} cases\n";

    // 4. Published cases by month within 2026
    echo "\n--- 4. Published cases by month (2026) ---\n";
    $q = $pdo->query("SELECT MONTH(published_at) AS mo, COUNT(*) AS count FROM case_studies WHERE published_at IS NOT NULL AND YEAR(published_at) = 2026 GROUP BY mo ORDER BY mo");
    $months = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    foreach ($q as $r) echo "  {$months[$r['mo']]}: {$r['count']} cases\n";

    // 5. NULL date fields
    echo "\n--- 5. Cases with NULL dates ---\n";
    $q = $pdo->query("SELECT SUM(CASE WHEN published_at IS NULL THEN 1 ELSE 0 END) AS no_publish_date, SUM(CASE WHEN created_at IS NULL THEN 1 ELSE 0 END) AS no_created_date, SUM(CASE WHEN updated_at IS NULL THEN 1 ELSE 0 END) AS no_updated_date, SUM(CASE WHEN submission_deadline IS NULL THEN 1 ELSE 0 END) AS no_deadline, COUNT(*) AS total FROM case_studies");
    $r = $q->fetch();
    foreach ($r as $k => $v) echo "  {$k}: {$v}\n";

    // 6. Recency windows
    echo "\n--- 6. Cases published in recency windows ---\n";
    $windows = ['Last 30 days' => 30, 'Last 90 days' => 90, 'Last 180 days' => 180, 'Last 365 days' => 365];
    foreach ($windows as $label => $days) {
        $q = $pdo->query("SELECT COUNT(*) AS count FROM case_studies WHERE published_at IS NOT NULL AND published_at >= DATE_SUB(NOW(), INTERVAL $days DAY)");
        echo "  {$label}: {$q->fetch()['count']} cases\n";
    }
    $q = $pdo->query("SELECT COUNT(*) AS count FROM case_studies WHERE published_at IS NOT NULL AND published_at < DATE_SUB(NOW(), INTERVAL 365 DAY)");
    echo "  Older than 365 days: {$q->fetch()['count']} cases\n";

    // 7. Most recently published
    echo "\n--- 7. Most recently published ---\n";
    $q = $pdo->query("SELECT id, title, published_at, relevance_status, status FROM case_studies WHERE published_at IS NOT NULL ORDER BY published_at DESC LIMIT 5");
    foreach ($q as $r) echo "  #{$r['id']} {$r['title']} | Published: {$r['published_at']} | {$r['relevance_status']} | {$r['status']}\n";

    // 8. Oldest published
    echo "\n--- 8. Oldest published ---\n";
    $q = $pdo->query("SELECT id, title, published_at, relevance_status, status FROM case_studies WHERE published_at IS NOT NULL ORDER BY published_at ASC LIMIT 5");
    foreach ($q as $r) echo "  #{$r['id']} {$r['title']} | Published: {$r['published_at']} | {$r['relevance_status']} | {$r['status']}\n";

    // 9. Cases never published
    echo "\n--- 9. Cases never published ---\n";
    $q = $pdo->query("SELECT id, title, status, created_at, relevance_status FROM case_studies WHERE published_at IS NULL ORDER BY created_at DESC LIMIT 10");
    foreach ($q as $r) echo "  #{$r['id']} {$r['title']} | Status: {$r['status']} | Relevance: {$r['relevance_status']} | Created: {$r['created_at']}\n";

    // 10. Difficulty distribution
    echo "\n--- 10. Difficulty level distribution ---\n";
    $q = $pdo->query("SELECT difficulty_level, COUNT(*) AS count FROM case_studies GROUP BY difficulty_level ORDER BY FIELD(difficulty_level, 'Beginner','Intermediate','Advanced','Expert')");
    foreach ($q as $r) echo "  {$r['difficulty_level']}: {$r['count']}\n";

    // 11. Duration buckets
    echo "\n--- 11. Case duration (estimated_time_minutes) ---\n";
    $q = $pdo->query("SELECT CASE WHEN estimated_time_minutes <= 30 THEN '<=30 min' WHEN estimated_time_minutes <= 60 THEN '31-60 min' WHEN estimated_time_minutes <= 120 THEN '61-120 min' WHEN estimated_time_minutes <= 180 THEN '121-180 min' ELSE '181+ min' END AS bucket, COUNT(*) AS count FROM case_studies GROUP BY bucket ORDER BY FIELD(bucket, '<=30 min','31-60 min','61-120 min','121-180 min','181+ min')");
    foreach ($q as $r) echo "  {$r['bucket']}: {$r['count']}\n";

    // 12. Stale/Outdated cases
    echo "\n--- 12. Stale/Outdated cases ---\n";
    $q = $pdo->query("SELECT id, title, relevance_status, published_at, status FROM case_studies WHERE relevance_status IN ('Stale','Outdated') ORDER BY published_at ASC LIMIT 10");
    foreach ($q as $r) echo "  #{$r['id']} {$r['title']} | {$r['relevance_status']} | Published: {$r['published_at']} | {$r['status']}\n";

    // 13. Data completeness
    echo "\n--- 13. Data completeness (missing fields) ---\n";
    $q = $pdo->query("SELECT SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END) AS missing_description, SUM(CASE WHEN full_content IS NULL OR full_content = '' THEN 1 ELSE 0 END) AS missing_full_content, SUM(CASE WHEN solution_frameworks IS NULL OR solution_frameworks = '' THEN 1 ELSE 0 END) AS missing_solution_frameworks, SUM(CASE WHEN solver_guidance IS NULL OR solver_guidance = '' THEN 1 ELSE 0 END) AS missing_solver_guidance, SUM(CASE WHEN data_sources IS NULL OR data_sources = '' THEN 1 ELSE 0 END) AS missing_data_sources, SUM(CASE WHEN current_affairs_tags IS NULL OR current_affairs_tags = '' THEN 1 ELSE 0 END) AS missing_current_affairs_tags, SUM(CASE WHEN case_type_id IS NULL THEN 1 ELSE 0 END) AS missing_case_type_id, SUM(CASE WHEN author_id IS NULL THEN 1 ELSE 0 END) AS missing_author_id, SUM(CASE WHEN difficulty_level IS NULL THEN 1 ELSE 0 END) AS missing_difficulty_level, COUNT(*) AS total FROM case_studies");
    $r = $q->fetch();
    foreach ($r as $k => $v) echo "  {$k}: {$v}\n";

    // 14. Registrations by month
    echo "\n--- 14. Case Registrations by month ---\n";
    $q = $pdo->query("SELECT DATE_FORMAT(registered_at, '%Y-%m') AS mo, COUNT(*) AS registrations, COUNT(DISTINCT user_id) AS unique_users, COUNT(DISTINCT case_study_id) AS unique_cases FROM case_registrations GROUP BY mo ORDER BY mo DESC");
    foreach ($q as $r) echo "  {$r['mo']}: {$r['registrations']} regs, {$r['unique_users']} users, {$r['unique_cases']} cases\n";

    // 15. View count stats
    echo "\n--- 15. View count statistics ---\n";
    $q = $pdo->query("SELECT MIN(view_count) AS min_views, MAX(view_count) AS max_views, ROUND(AVG(view_count),1) AS avg_views, SUM(CASE WHEN view_count = 0 THEN 1 ELSE 0 END) AS zero_views, SUM(CASE WHEN view_count > 0 AND view_count <= 10 THEN 1 ELSE 0 END) AS low_views, SUM(CASE WHEN view_count > 10 AND view_count <= 100 THEN 1 ELSE 0 END) AS medium_views, SUM(CASE WHEN view_count > 100 THEN 1 ELSE 0 END) AS high_views FROM case_studies");
    $r = $q->fetch();
    foreach ($r as $k => $v) echo "  {$k}: {$v}\n";

    // 16. Top 5 most viewed
    echo "\n--- 16. Top 5 most viewed ---\n";
    $q = $pdo->query("SELECT id, title, view_count, relevance_status, published_at FROM case_studies ORDER BY view_count DESC LIMIT 5");
    foreach ($q as $r) echo "  #{$r['id']} ({$r['view_count']} views) {$r['title']} | {$r['relevance_status']} | {$r['published_at']}\n";

    // 17. Case types with zero published cases
    echo "\n--- 17. Case types with zero published cases ---\n";
    $q = $pdo->query("SELECT ct.id, ct.name, ct.category FROM case_types ct LEFT JOIN case_studies cs ON ct.id = cs.case_type_id AND cs.status = 'Published' GROUP BY ct.id, ct.name, ct.category HAVING COUNT(cs.id) = 0 ORDER BY ct.category, ct.name");
    foreach ($q as $r) echo "  #{$r['id']} {$r['name']} [{$r['category']}]\n";

    // 18. Premium vs Free
    echo "\n--- 18. Premium vs Free ---\n";
    $q = $pdo->query("SELECT is_premium, COUNT(*) AS count FROM case_studies GROUP BY is_premium");
    foreach ($q as $r) echo "  " . ($r['is_premium'] ? 'Premium' : 'Free') . ": {$r['count']}\n";

    // 19. Freshness cross-tab: relevance_status vs recency
    echo "\n--- 19. Relevance status vs publication recency ---\n";
    $q = $pdo->query("SELECT relevance_status, CASE WHEN published_at >= DATE_SUB(NOW(), INTERVAL 90 DAY) THEN 'Last 90 days' WHEN published_at >= DATE_SUB(NOW(), INTERVAL 180 DAY) THEN '91-180 days' WHEN published_at >= DATE_SUB(NOW(), INTERVAL 365 DAY) THEN '181-365 days' ELSE 'Over 1 year' END AS recency, COUNT(*) AS count FROM case_studies WHERE published_at IS NOT NULL GROUP BY relevance_status, recency ORDER BY relevance_status, recency");
    foreach ($q as $r) echo "  {$r['relevance_status']} / {$r['recency']}: {$r['count']}\n";

    // 20. Author distribution
    echo "\n--- 20. Cases per author ---\n";
    $q = $pdo->query("SELECT COALESCE(u.full_name, 'Unknown') AS author, COUNT(cs.id) AS count FROM case_studies cs LEFT JOIN users u ON cs.author_id = u.id GROUP BY author ORDER BY count DESC LIMIT 10");
    foreach ($q as $r) echo "  {$r['author']}: {$r['count']} cases\n";

} catch (PDOException $e) {
    echo "ERROR: " . $e->getMessage() . "\n";
}
