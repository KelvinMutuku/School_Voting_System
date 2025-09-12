<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST");
header("Access-Control-Allow-Headers: Content-Type");

$host = "localhost";
$dbname = "algocracy_elections";
$username = "root"; // Replace with your MySQL username
$password = ""; // Replace with your MySQL password

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(["success" => false, "message" => "Database connection failed: " . $e->getMessage()]);
    exit;
}

$action = isset($_GET['action']) ? $_GET['action'] : '';

function validateId($id) {
    return preg_match('/^KJS[0-9]{3}$/', $id);
}

function validateTeacherUsername($username) {
    return preg_match('/^teacher[7-9][a-zA-Z]+$/', $username);
}

switch ($action) {
    case 'get_student':
        $id = isset($_GET['id']) ? $_GET['id'] : '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT name, grade, class, gender FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode(["success" => $student !== false, "student" => $student ?: null]);
        break;

    case 'register_student':
        $data = json_decode(file_get_contents("php://input"), true);
        $id = $data['id'] ?? '';
        $password = $data['password'] ?? '';
        $question = $data['security_question'] ?? '';
        $answer = $data['security_answer'] ?? '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        if (strlen($password) < 6) {
            echo json_encode(["success" => false, "message" => "Password must be at least 6 characters."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT id FROM students WHERE id = ?");
        $stmt->execute([$id]);
        if ($stmt->fetch()) {
            $stmt = $pdo->prepare("SELECT id FROM students WHERE id = ? AND password IS NOT NULL AND password != ''");
            $stmt->execute([$id]);
            if ($stmt->fetch()) {
                echo json_encode(["success" => false, "message" => "Student already registered."]);
                exit;
            }
            $hashedPassword = password_hash($password, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("UPDATE students SET password = ?, security_question = ?, security_answer = ? WHERE id = ?");
            $stmt->execute([$hashedPassword, $question, $answer, $id]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Student ID not found."]);
        }
        break;

    case 'change_student_password':
        $data = json_decode(file_get_contents("php://input"), true);
        $id = $data['id'] ?? '';
        $oldPassword = $data['old_password'] ?? '';
        $newPassword = $data['new_password'] ?? '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        if (strlen($newPassword) < 6) {
            echo json_encode(["success" => false, "message" => "New password must be at least 6 characters."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT password FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($student && password_verify($oldPassword, $student['password'])) {
            $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("UPDATE students SET password = ? WHERE id = ?");
            $stmt->execute([$hashedPassword, $id]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid Student ID or old password."]);
        }
        break;

    case 'get_security_question':
        $id = isset($_GET['id']) ? $_GET['id'] : '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT security_question FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode(["success" => $result !== false, "security_question" => $result['security_question'] ?? null]);
        break;

    case 'reset_student_password':
        $data = json_decode(file_get_contents("php://input"), true);
        $id = $data['id'] ?? '';
        $answer = $data['security_answer'] ?? '';
        $newPassword = $data['new_password'] ?? '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        if (strlen($newPassword) < 6) {
            echo json_encode(["success" => false, "message" => "New password must be at least 6 characters."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT security_answer FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($student && $student['security_answer'] === $answer) {
            $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("UPDATE students SET password = ? WHERE id = ?");
            $stmt->execute([$hashedPassword, $id]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid Student ID or security answer."]);
        }
        break;

    case 'validate_voter':
        $data = json_decode(file_get_contents("php://input"), true);
        $id = $data['id'] ?? '';
        $password = $data['password'] ?? '';
        if (!validateId($id)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT * FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($student && password_verify($password, $student['password'])) {
            $stmt = $pdo->prepare("SELECT voting_open FROM admin WHERE id = 1");
            $stmt->execute();
            $admin = $stmt->fetch(PDO::FETCH_ASSOC);
            if (!$admin['voting_open']) {
                echo json_encode(["success" => false, "message" => "Voting is closed."]);
                exit;
            }
            echo json_encode(["success" => true, "student" => [
                "id" => $student['id'],
                "name" => $student['name'],
                "grade" => $student['grade'],
                "class" => $student['class']
            ]]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid Student ID or password."]);
        }
        break;

    case 'get_positions':
        $grade = isset($_GET['grade']) ? (int)$_GET['grade'] : 0;
        $class = isset($_GET['class']) ? $_GET['class'] : '';
        $positions = [];
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $allPositions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($allPositions as $p) {
            $scope = $p['scope'];
            $include = false;
            if ($scope === 'school') {
                $include = true;
            } elseif (preg_match('/grade_(\d+)/', $scope, $matches) && (int)$matches[1] === $grade) {
                $include = true;
            } elseif (preg_match('/grade_(\d+)_class_(.+)/', $scope, $matches) && (int)$matches[1] === $grade && $matches[2] === strtolower($class)) {
                $include = true;
            }
            if ($include) {
                $stmt = $pdo->prepare("SELECT student_name FROM candidates WHERE position_id = ?");
                $stmt->execute([$p['id']]);
                $candidates = $stmt->fetchAll(PDO::FETCH_COLUMN);
                $positions[] = [
                    "id" => $p['id'],
                    "name" => $p['name'],
                    "scope" => $p['scope'],
                    "candidates" => $candidates
                ];
            }
        }
        echo json_encode($positions);
        break;

    case 'submit_votes':
        $data = json_decode(file_get_contents("php://input"), true);
        $votes = $data['votes'] ?? [];
        $stmt = $pdo->prepare("SELECT voting_open FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$admin['voting_open']) {
            echo json_encode(["success" => false, "message" => "Voting is closed."]);
            exit;
        }
        $pdo->beginTransaction();
        try {
            $stmt = $pdo->prepare("SELECT voter_hash, position_id FROM votes WHERE voter_hash = ? AND position_id = ?");
            $insertStmt = $pdo->prepare("INSERT INTO votes (position_id, voter_hash, candidate_name, timestamp) VALUES (?, ?, ?, NOW())");
            foreach ($votes as $vote) {
                $positionId = $vote['position_id'];
                $voterHash = $vote['voter_hash'];
                $candidate = $vote['candidate'];
                $stmt->execute([$voterHash, $positionId]);
                if ($stmt->fetch()) {
                    $pdo->rollBack();
                    echo json_encode(["success" => false, "message" => "You have already voted for one or more positions."]);
                    exit;
                }
                $stmtCand = $pdo->prepare("SELECT id FROM candidates WHERE position_id = ? AND student_name = ?");
                $stmtCand->execute([$positionId, $candidate]);
                if (!$stmtCand->fetch()) {
                    $pdo->rollBack();
                    echo json_encode(["success" => false, "message" => "Invalid candidate for position."]);
                    exit;
                }
                $insertStmt->execute([$positionId, $voterHash, $candidate]);
            }
            $pdo->commit();
            echo json_encode(["success" => true]);
        } catch (Exception $e) {
            $pdo->rollBack();
            echo json_encode(["success" => false, "message" => "Error submitting votes: " . $e->getMessage()]);
        }
        break;

    case 'get_tally':
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $positions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $tally = [];
        foreach ($positions as $p) {
            $stmt = $pdo->prepare("SELECT candidate_name, COUNT(*) as count FROM votes WHERE position_id = ? GROUP BY candidate_name");
            $stmt->execute([$p['id']]);
            $votes = $stmt->fetchAll(PDO::FETCH_ASSOC);
            $tally[] = [
                "position" => $p['name'],
                "votes" => $votes
            ];
        }
        echo json_encode($tally);
        break;

    case 'get_results':
        $stmt = $pdo->prepare("SELECT * FROM weights WHERE id = 1");
        $stmt->execute();
        $weights = $stmt->fetch(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $positions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $results = [];
        foreach ($positions as $p) {
            $stmt = $pdo->prepare("SELECT student_name FROM candidates WHERE position_id = ?");
            $stmt->execute([$p['id']]);
            $candidates = $stmt->fetchAll(PDO::FETCH_COLUMN);
            $stmt = $pdo->prepare("SELECT candidate_name, COUNT(*) as count FROM votes WHERE position_id = ? GROUP BY candidate_name");
            $stmt->execute([$p['id']]);
            $votes = $stmt->fetchAll(PDO::FETCH_ASSOC);
            $totalVotes = array_sum(array_column($votes, 'count'));
            $votePercentages = [];
            foreach ($votes as $v) {
                $votePercentages[$v['candidate_name']] = $totalVotes ? ($v['count'] / $totalVotes) * 100 : 0;
            }
            $positionResults = [];
            foreach ($candidates as $c) {
                $stmt = $pdo->prepare("SELECT * FROM metrics WHERE student_name = ?");
                $stmt->execute([$c]);
                $m = $stmt->fetch(PDO::FETCH_ASSOC);
                $score = ($votePercentages[$c] ?? 0) * ($weights['student_votes'] / 100);
                if ($m) {
                    $score += ($m['academics'] ?? 0) * ($weights['academics'] / 100);
                    $score += ($m['discipline'] ?? 0) * ($weights['discipline'] / 100);
                    $score += ($m['clubs'] ?? 0) * ($weights['clubs'] / 100);
                    $score += ($m['community_service'] ?? 0) * ($weights['community_service'] / 100);
                    $score += ($m['teacher'] ?? 0) * ($weights['teacher'] / 100);
                    $score += ($m['leadership'] ?? 0) * ($weights['leadership'] / 100);
                    $score += ($m['public_speaking'] ?? 0) * ($weights['public_speaking'] / 100);
                }
                $positionResults[] = [
                    "candidate" => $c,
                    "student_votes" => sprintf("%.2f%%", $votePercentages[$c] ?? 0),
                    "academics" => $m['academics'] ?? "-",
                    "discipline" => $m['discipline'] ?? "-",
                    "clubs" => $m['clubs'] ?? "-",
                    "community_service" => $m['community_service'] ?? "-",
                    "teacher" => $m['teacher'] ?? "-",
                    "leadership" => $m['leadership'] ?? "-",
                    "public_speaking" => $m['public_speaking'] ?? "-",
                    "final_score" => sprintf("%.2f", $score)
                ];
            }
            usort($positionResults, fn($a, $b) => $b['final_score'] <=> $a['final_score']);
            $results[] = [
                "position" => $p['name'],
                "results" => $positionResults
            ];
        }
        echo json_encode($results);
        break;

    case 'login_teacher':
        $data = json_decode(file_get_contents("php://input"), true);
        $username = $data['username'] ?? '';
        $password = $data['password'] ?? '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT * FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($teacher && password_verify($password, $teacher['password'])) {
            echo json_encode(["success" => true, "teacher" => [
                "username" => $teacher['username'],
                "grade" => $teacher['grade'],
                "class" => $teacher['class']
            ]]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid username or password."]);
        }
        break;

    case 'get_class_students':
        $grade = isset($_GET['grade']) ? (int)$_GET['grade'] : 0;
        $class = isset($_GET['class']) ? $_GET['class'] : '';
        $stmt = $pdo->prepare("SELECT s.id, s.name, m.* FROM students s LEFT JOIN metrics m ON s.name = m.student_name WHERE s.grade = ? AND s.class = ?");
        $stmt->execute([$grade, $class]);
        $students = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($students);
        break;

    case 'save_metrics':
        $data = json_decode(file_get_contents("php://input"), true);
        $metrics = $data['metrics'] ?? [];
        $pdo->beginTransaction();
        try {
            $stmt = $pdo->prepare("
                INSERT INTO metrics (student_name, academics, discipline, clubs, community_service, teacher, leadership, public_speaking)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    academics = VALUES(academics),
                    discipline = VALUES(discipline),
                    clubs = VALUES(clubs),
                    community_service = VALUES(community_service),
                    teacher = VALUES(teacher),
                    leadership = VALUES(leadership),
                    public_speaking = VALUES(public_speaking)
            ");
            foreach ($metrics as $m) {
                $stmt->execute([
                    $m['student_name'],
                    $m['academics'],
                    $m['discipline'],
                    $m['clubs'],
                    $m['community_service'],
                    $m['teacher'],
                    $m['leadership'],
                    $m['public_speaking']
                ]);
            }
            $pdo->commit();
            echo json_encode(["success" => true]);
        } catch (Exception $e) {
            $pdo->rollBack();
            echo json_encode(["success" => false, "message" => "Error saving metrics: " . $e->getMessage()]);
        }
        break;

    case 'change_teacher_password':
        $data = json_decode(file_get_contents("php://input"), true);
        $username = $data['username'] ?? '';
        $oldPassword = $data['old_password'] ?? '';
        $newPassword = $data['new_password'] ?? '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        if (strlen($newPassword) < 6) {
            echo json_encode(["success" => false, "message" => "New password must be at least 6 characters."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT password FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($teacher && password_verify($oldPassword, $teacher['password'])) {
            $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("UPDATE teachers SET password = ? WHERE username = ?");
            $stmt->execute([$hashedPassword, $username]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid username or old password."]);
        }
        break;

    case 'get_teacher_security_question':
        $username = isset($_GET['username']) ? $_GET['username'] : '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT security_question FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode(["success" => $result !== false, "security_question" => $result['security_question'] ?? null]);
        break;

    case 'reset_teacher_password':
        $data = json_decode(file_get_contents("php://input"), true);
        $username = $data['username'] ?? '';
        $answer = $data['security_answer'] ?? '';
        $newPassword = $data['new_password'] ?? '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        if (strlen($newPassword) < 6) {
            echo json_encode(["success" => false, "message" => "New password must be at least 6 characters."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT security_answer FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($teacher && $teacher['security_answer'] === $answer) {
            $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("UPDATE teachers SET password = ? WHERE username = ?");
            $stmt->execute([$hashedPassword, $username]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid username or security answer."]);
        }
        break;

    case 'add_student_to_class':
        $data = json_decode(file_get_contents("php://input"), true);
        $teacherUsername = $data['teacher_username'] ?? '';
        $studentId = $data['student_id'] ?? '';
        $studentName = $data['student_name'] ?? '';
        if (!validateTeacherUsername($teacherUsername) || !validateId($studentId)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username or student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT grade, class FROM teachers WHERE username = ?");
        $stmt->execute([$teacherUsername]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$teacher) {
            echo json_encode(["success" => false, "message" => "Teacher not found."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT id FROM students WHERE id = ?");
        $stmt->execute([$studentId]);
        if ($stmt->fetch()) {
            echo json_encode(["success" => false, "message" => "Student ID already exists."]);
            exit;
        }
        $stmt = $pdo->prepare("INSERT INTO students (id, name, password, grade, class, gender) VALUES (?, ?, '', ?, ?, 'U')");
        $stmt->execute([$studentId, $studentName, $teacher['grade'], $teacher['class']]);
        echo json_encode(["success" => true]);
        break;

    case 'remove_student_from_class':
        $data = json_decode(file_get_contents("php://input"), true);
        $teacherUsername = $data['teacher_username'] ?? '';
        $studentId = $data['student_id'] ?? '';
        if (!validateTeacherUsername($teacherUsername) || !validateId($studentId)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username or student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT grade, class FROM teachers WHERE username = ?");
        $stmt->execute([$teacherUsername]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$teacher) {
            echo json_encode(["success" => false, "message" => "Teacher not found."]);
            exit;
        }
        $stmt = $pdo->prepare("DELETE FROM students WHERE id = ? AND grade = ? AND class = ?");
        $stmt->execute([$studentId, $teacher['grade'], $teacher['class']]);
        if ($stmt->rowCount() > 0) {
            $stmt = $pdo->prepare("DELETE FROM metrics WHERE student_name IN (SELECT name FROM students WHERE id = ?)");
            $stmt->execute([$studentId]);
            $stmt = $pdo->prepare("DELETE FROM candidates WHERE student_name IN (SELECT name FROM students WHERE id = ?)");
            $stmt->execute([$studentId]);
            $stmt = $pdo->prepare("DELETE FROM votes WHERE candidate_name IN (SELECT name FROM students WHERE id = ?)");
            $stmt->execute([$studentId]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Student not found in your class."]);
        }
        break;

    case 'clear_all_students':
        $data = json_decode(file_get_contents("php://input"), true);
        $pdo->beginTransaction();
        try {
            $pdo->exec("DELETE FROM votes");
            $pdo->exec("DELETE FROM candidates");
            $pdo->exec("DELETE FROM metrics");
            $pdo->exec("DELETE FROM students");
            $pdo->commit();
            echo json_encode(["success" => true]);
        } catch (Exception $e) {
            $pdo->rollBack();
            echo json_encode(["success" => false, "message" => "Error clearing students: " . $e->getMessage()]);
        }
        break;

    case 'unlock_admin':
        $data = json_decode(file_get_contents("php://input"), true);
        $pin = $data['pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin, voting_open FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $pin === $admin['pin']) {
            echo json_encode(["success" => true, "voting_open" => $admin['voting_open']]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid PIN."]);
        }
        break;

    case 'get_all_positions':
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $positions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($positions);
        break;

    case 'add_position':
        $data = json_decode(file_get_contents("php://input"), true);
        $name = $data['name'] ?? '';
        $scope = $data['scope'] ?? 'school';
        if (!$name) {
            echo json_encode(["success" => false, "message" => "Position name is required."]);
            exit;
        }
        $stmt = $pdo->prepare("INSERT INTO positions (name, scope) VALUES (?, ?)");
        $stmt->execute([$name, $scope]);
        echo json_encode(["success" => true]);
        break;

    case 'remove_position':
        $data = json_decode(file_get_contents("php://input"), true);
        $positionId = $data['position_id'] ?? 0;
        $pdo->beginTransaction();
        try {
            $stmt = $pdo->prepare("DELETE FROM votes WHERE position_id = ?");
            $stmt->execute([$positionId]);
            $stmt = $pdo->prepare("DELETE FROM candidates WHERE position_id = ?");
            $stmt->execute([$positionId]);
            $stmt = $pdo->prepare("DELETE FROM positions WHERE id = ?");
            $stmt->execute([$positionId]);
            $pdo->commit();
            echo json_encode(["success" => true]);
        } catch (Exception $e) {
            $pdo->rollBack();
            echo json_encode(["success" => false, "message" => "Error removing position: " . $e->getMessage()]);
        }
        break;

    case 'get_all_teachers':
        $stmt = $pdo->prepare("SELECT username, grade, class FROM teachers");
        $stmt->execute();
        $teachers = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($teachers);
        break;

    case 'add_teacher':
        $data = json_decode(file_get_contents("php://input"), true);
        $username = $data['username'] ?? '';
        $grade = $data['grade'] ?? 0;
        $class = $data['class'] ?? '';
        $password = $data['password'] ?? '';
        if (!validateTeacherUsername($username) || !in_array($grade, [7, 8, 9]) || !$class || strlen($password) < 4) {
            echo json_encode(["success" => false, "message" => "Invalid teacher details."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT username FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        if ($stmt->fetch()) {
            echo json_encode(["success" => false, "message" => "Teacher username already exists."]);
            exit;
        }
        $hashedPassword = password_hash($password, PASSWORD_BCRYPT);
        $stmt = $pdo->prepare("INSERT INTO teachers (username, password, grade, class) VALUES (?, ?, ?, ?)");
        $stmt->execute([$username, $hashedPassword, $grade, $class]);
        echo json_encode(["success" => true]);
        break;

    case 'remove_teacher':
        $data = json_decode(file_get_contents("php://input"), true);
        $username = $data['username'] ?? '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        $stmt = $pdo->prepare("DELETE FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        if ($stmt->rowCount() > 0) {
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Teacher not found."]);
        }
        break;

    case 'get_weights':
        $stmt = $pdo->prepare("SELECT * FROM weights WHERE id = 1");
        $stmt->execute();
        $weights = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode($weights);
        break;

    case 'save_weights':
        $data = json_decode(file_get_contents("php://input"), true);
        $weights = [
            'student_votes' => (int)($data['student_votes'] ?? 30),
            'academics' => (int)($data['academics'] ?? 15),
            'discipline' => (int)($data['discipline'] ?? 10),
            'clubs' => (int)($data['clubs'] ?? 10),
            'community_service' => (int)($data['community_service'] ?? 5),
            'teacher' => (int)($data['teacher'] ?? 10),
            'leadership' => (int)($data['leadership'] ?? 10),
            'public_speaking' => (int)($data['public_speaking'] ?? 10)
        ];
        $total = array_sum($weights);
        if ($total !== 100) {
            echo json_encode(["success" => false, "message" => "Weights must total 100%."]);
            exit;
        }
        $stmt = $pdo->prepare("
            UPDATE weights SET
                student_votes = ?,
                academics = ?,
                discipline = ?,
                clubs = ?,
                community_service = ?,
                teacher = ?,
                leadership = ?,
                public_speaking = ?
            WHERE id = 1
        ");
        $stmt->execute(array_values($weights));
        echo json_encode(["success" => true]);
        break;

    case 'toggle_voting':
        $data = json_decode(file_get_contents("php://input"), true);
        $pin = $data['pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $pin === $admin['pin']) {
            $stmt = $pdo->prepare("UPDATE admin SET voting_open = NOT voting_open WHERE id = 1");
            $stmt->execute();
            $stmt = $pdo->prepare("SELECT voting_open FROM admin WHERE id = 1");
            $stmt->execute();
            $newStatus = $stmt->fetch(PDO::FETCH_ASSOC);
            echo json_encode(["success" => true, "voting_open" => $newStatus['voting_open']]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid PIN."]);
        }
        break;

    case 'update_pin':
        $data = json_decode(file_get_contents("php://input"), true);
        $oldPin = $data['old_pin'] ?? '';
        $newPin = $data['new_pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $oldPin === $admin['pin']) {
            $stmt = $pdo->prepare("UPDATE admin SET pin = ? WHERE id = 1");
            $stmt->execute([$newPin]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid current PIN."]);
        }
        break;

    case 'factory_reset':
        $data = json_decode(file_get_contents("php://input"), true);
        $pin = $data['pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $pin === $admin['pin']) {
            $pdo->beginTransaction();
            try {
                $pdo->exec("DELETE FROM votes");
                $pdo->exec("DELETE FROM candidates");
                $pdo->exec("DELETE FROM positions");
                $pdo->exec("DELETE FROM metrics");
                $pdo->exec("DELETE FROM students");
                $pdo->exec("DELETE FROM teachers");
                $pdo->exec("UPDATE weights SET student_votes = 30, academics = 15, discipline = 10, clubs = 10, community_service = 5, teacher = 10, leadership = 10, public_speaking = 10 WHERE id = 1");
                $pdo->exec("UPDATE admin SET pin = '1234', voting_open = TRUE WHERE id = 1");
                $pdo->commit();
                echo json_encode(["success" => true]);
            } catch (Exception $e) {
                $pdo->rollBack();
                echo json_encode(["success" => false, "message" => "Error performing factory reset: " . $e->getMessage()]);
            }
        } else {
            echo json_encode(["success" => false, "message" => "Invalid PIN."]);
        }
        break;

    case 'export_votes':
        $stmt = $pdo->prepare("
            SELECT v.position_id, p.name as position_name, v.voter_hash, v.candidate_name, v.timestamp
            FROM votes v
            JOIN positions p ON v.position_id = p.id
        ");
        $stmt->execute();
        $votes = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode(["success" => true, "votes" => $votes]);
        break;

    case 'export_results':
        $stmt = $pdo->prepare("SELECT * FROM weights WHERE id = 1");
        $stmt->execute();
        $weights = $stmt->fetch(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $positions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $results = [];
        foreach ($positions as $p) {
            $stmt = $pdo->prepare("SELECT student_name FROM candidates WHERE position_id = ?");
            $stmt->execute([$p['id']]);
            $candidates = $stmt->fetchAll(PDO::FETCH_COLUMN);
            $stmt = $pdo->prepare("SELECT candidate_name, COUNT(*) as count FROM votes WHERE position_id = ? GROUP BY candidate_name");
            $stmt->execute([$p['id']]);
            $votes = $stmt->fetchAll(PDO::FETCH_ASSOC);
            $totalVotes = array_sum(array_column($votes, 'count'));
            $votePercentages = [];
            foreach ($votes as $v) {
                $votePercentages[$v['candidate_name']] = $totalVotes ? ($v['count'] / $totalVotes) * 100 : 0;
            }
            $positionResults = [];
            foreach ($candidates as $c) {
                $stmt = $pdo->prepare("SELECT * FROM metrics WHERE student_name = ?");
                $stmt->execute([$c]);
                $m = $stmt->fetch(PDO::FETCH_ASSOC);
                $score = ($votePercentages[$c] ?? 0) * ($weights['student_votes'] / 100);
                if ($m) {
                    $score += ($m['academics'] ?? 0) * ($weights['academics'] / 100);
                    $score += ($m['discipline'] ?? 0) * ($weights['discipline'] / 100);
                    $score += ($m['clubs'] ?? 0) * ($weights['clubs'] / 100);
                    $score += ($m['community_service'] ?? 0) * ($weights['community_service'] / 100);
                    $score += ($m['teacher'] ?? 0) * ($weights['teacher'] / 100);
                    $score += ($m['leadership'] ?? 0) * ($weights['leadership'] / 100);
                    $score += ($m['public_speaking'] ?? 0) * ($weights['public_speaking'] / 100);
                }
                $positionResults[] = [
                    "Candidate" => $c,
                    "Student Votes (%)" => sprintf("%.2f", $votePercentages[$c] ?? 0),
                    "Academics" => $m['academics'] ?? "-",
                    "Discipline" => $m['discipline'] ?? "-",
                    "Clubs" => $m['clubs'] ?? "-",
                    "Community Service" => $m['community_service'] ?? "-",
                    "Teacher" => $m['teacher'] ?? "-",
                    "Leadership" => $m['leadership'] ?? "-",
                    "Public Speaking" => $m['public_speaking'] ?? "-",
                    "Final Score" => sprintf("%.2f", $score)
                ];
            }
            usort($positionResults, fn($a, $b) => $b['Final Score'] <=> $a['Final Score']);
            $results[$p['name']] = $positionResults;
        }
        echo json_encode(["success" => true, "results" => $results]);
        break;

    case 'download_backup':
        $backup = [];
        $stmt = $pdo->prepare("SELECT * FROM students");
        $stmt->execute();
        $backup['students'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM teachers");
        $stmt->execute();
        $backup['teachers'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM positions");
        $stmt->execute();
        $backup['positions'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM candidates");
        $stmt->execute();
        $backup['candidates'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM votes");
        $stmt->execute();
        $backup['votes'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM metrics");
        $stmt->execute();
        $backup['metrics'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT * FROM weights");
        $stmt->execute();
        $backup['weights'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $stmt = $pdo->prepare("SELECT pin, voting_open FROM admin");
        $stmt->execute();
        $backup['admin'] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode(["success" => true, "backup" => $backup]);
        break;

    case 'import_backup':
        $data = json_decode(file_get_contents("php://input"), true);
        $backup = $data['backup'] ?? [];
        $pin = $data['pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $pin === $admin['pin']) {
            $pdo->beginTransaction();
            try {
                $pdo->exec("DELETE FROM votes");
                $pdo->exec("DELETE FROM candidates");
                $pdo->exec("DELETE FROM positions");
                $pdo->exec("DELETE FROM metrics");
                $pdo->exec("DELETE FROM students");
                $pdo->exec("DELETE FROM teachers");
                $stmt = $pdo->prepare("INSERT INTO students (id, name, password, grade, class, gender, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
                foreach ($backup['students'] as $s) {
                    $stmt->execute([$s['id'], $s['name'], $s['password'], $s['grade'], $s['class'], $s['gender'], $s['security_question'], $s['security_answer']]);
                }
                $stmt = $pdo->prepare("INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)");
                foreach ($backup['teachers'] as $t) {
                    $stmt->execute([$t['username'], $t['password'], $t['grade'], $t['class'], $t['security_question'], $t['security_answer']]);
                }
                $stmt = $pdo->prepare("INSERT INTO positions (id, name, scope) VALUES (?, ?, ?)");
                foreach ($backup['positions'] as $p) {
                    $stmt->execute([$p['id'], $p['name'], $p['scope']]);
                }
                $stmt = $pdo->prepare("INSERT INTO candidates (id, position_id, student_name) VALUES (?, ?, ?)");
                foreach ($backup['candidates'] as $c) {
                    $stmt->execute([$c['id'], $c['position_id'], $c['student_name']]);
                }
                $stmt = $pdo->prepare("INSERT INTO votes (id, position_id, voter_hash, candidate_name, timestamp) VALUES (?, ?, ?, ?, ?)");
                foreach ($backup['votes'] as $v) {
                    $stmt->execute([$v['id'], $v['position_id'], $v['voter_hash'], $v['candidate_name'], $v['timestamp']]);
                }
                $stmt = $pdo->prepare("INSERT INTO metrics (id, student_name, academics, discipline, clubs, community_service, teacher, leadership, public_speaking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
                foreach ($backup['metrics'] as $m) {
                    $stmt->execute([$m['id'], $m['student_name'], $m['academics'], $m['discipline'], $m['clubs'], $m['community_service'], $m['teacher'], $m['leadership'], $m['public_speaking']]);
                }
                $stmt = $pdo->prepare("UPDATE weights SET student_votes = ?, academics = ?, discipline = ?, clubs = ?, community_service = ?, teacher = ?, leadership = ?, public_speaking = ? WHERE id = 1");
                $w = $backup['weights'][0];
                $stmt->execute([$w['student_votes'], $w['academics'], $w['discipline'], $w['clubs'], $w['community_service'], $w['teacher'], $w['leadership'], $w['public_speaking']]);
                $pdo->commit();
                echo json_encode(["success" => true]);
            } catch (Exception $e) {
                $pdo->rollBack();
                echo json_encode(["success" => false, "message" => "Error importing backup: " . $e->getMessage()]);
            }
        } else {
            echo json_encode(["success" => false, "message" => "Invalid PIN."]);
        }
        break;

    case 'get_candidates':
        $positionId = isset($_GET['position_id']) ? (int)$_GET['position_id'] : 0;
        $stmt = $pdo->prepare("SELECT student_name FROM candidates WHERE position_id = ?");
        $stmt->execute([$positionId]);
        $candidates = $stmt->fetchAll(PDO::FETCH_COLUMN);
        echo json_encode(["success" => true, "candidates" => $candidates]);
        break;

    case 'add_candidate':
        $data = json_decode(file_get_contents("php://input"), true);
        $positionId = $data['position_id'] ?? 0;
        $studentId = $data['student_id'] ?? '';
        if (!validateId($studentId)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT name FROM students WHERE id = ?");
        $stmt->execute([$studentId]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$student) {
            echo json_encode(["success" => false, "message" => "Student not found."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT id FROM positions WHERE id = ?");
        $stmt->execute([$positionId]);
        if (!$stmt->fetch()) {
            echo json_encode(["success" => false, "message" => "Position not found."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT id FROM candidates WHERE position_id = ? AND student_name = ?");
        $stmt->execute([$positionId, $student['name']]);
        if ($stmt->fetch()) {
            echo json_encode(["success" => false, "message" => "Student is already a candidate for this position."]);
            exit;
        }
        $stmt = $pdo->prepare("INSERT INTO candidates (position_id, student_name) VALUES (?, ?)");
        $stmt->execute([$positionId, $student['name']]);
        echo json_encode(["success" => true]);
        break;

    case 'remove_candidate':
        $data = json_decode(file_get_contents("php://input"), true);
        $positionId = $data['position_id'] ?? 0;
        $studentId = $data['student_id'] ?? '';
        if (!validateId($studentId)) {
            echo json_encode(["success" => false, "message" => "Invalid Student ID format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT name FROM students WHERE id = ?");
        $stmt->execute([$studentId]);
        $student = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$student) {
            echo json_encode(["success" => false, "message" => "Student not found."]);
            exit;
        }
        $stmt = $pdo->prepare("DELETE FROM candidates WHERE position_id = ? AND student_name = ?");
        $stmt->execute([$positionId, $student['name']]);
        if ($stmt->rowCount() > 0) {
            $stmt = $pdo->prepare("DELETE FROM votes WHERE position_id = ? AND candidate_name = ?");
            $stmt->execute([$positionId, $student['name']]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Candidate not found for this position."]);
        }
        break;

    case 'clear_all_candidates':
        $data = json_decode(file_get_contents("php://input"), true);
        $pin = $data['pin'] ?? '';
        $stmt = $pdo->prepare("SELECT pin FROM admin WHERE id = 1");
        $stmt->execute();
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($admin && $pin === $admin['pin']) {
            $pdo->beginTransaction();
            try {
                $pdo->exec("DELETE FROM votes");
                $pdo->exec("DELETE FROM candidates");
                $pdo->commit();
                echo json_encode(["success" => true]);
            } catch (Exception $e) {
                $pdo->rollBack();
                echo json_encode(["success" => false, "message" => "Error clearing candidates: " . $e->getMessage()]);
            }
        } else {
            echo json_encode(["success" => false, "message" => "Invalid PIN."]);
        }
        break;

    case 'get_teacher':
        $username = isset($_GET['username']) ? $_GET['username'] : '';
        if (!validateTeacherUsername($username)) {
            echo json_encode(["success" => false, "message" => "Invalid teacher username format."]);
            exit;
        }
        $stmt = $pdo->prepare("SELECT username, grade, class FROM teachers WHERE username = ?");
        $stmt->execute([$username]);
        $teacher = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($teacher) {
            echo json_encode(["success" => true, "teacher" => $teacher]);
        } else {
            echo json_encode(["success" => false, "message" => "Teacher not found."]);
        }
        break;

    default:
        echo json_encode(["success" => false, "message" => "Invalid action."]);
        break;
}
?>