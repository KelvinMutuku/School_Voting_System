const VOTE_ENDPOINT = "";
const classes = {
  7: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta"],
  8: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta"],
  9: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"]
};

let teachers = JSON.parse(localStorage.getItem("teachers")) || [
  { username: "teacher7blue", password: "1234", grade: 7, class: "Blue", securityQuestion: "", securityAnswer: "" },
  { username: "teacher7red", password: "1234", grade: 7, class: "Red", securityQuestion: "", securityAnswer: "" },
  { username: "teacher7green", password: "1234", grade: 7, class: "Green", securityQuestion: "", securityAnswer: "" },
  { username: "teacher7yellow", password: "1234", grade: 7, class: "Yellow", securityQuestion: "", securityAnswer: "" },
  { username: "teacher7pink", password: "1234", grade: 7, class: "Pink", securityQuestion: "", securityAnswer: "" },
  { username: "teacher7magenta", password: "1234", grade: 7, class: "Magenta", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8blue", password: "1234", grade: 8, class: "Blue", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8red", password: "1234", grade: 8, class: "Red", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8green", password: "1234", grade: 8, class: "Green", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8yellow", password: "1234", grade: 8, class: "Yellow", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8pink", password: "1234", grade: 8, class: "Pink", securityQuestion: "", securityAnswer: "" },
  { username: "teacher8magenta", password: "1234", grade: 8, class: "Magenta", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9blue", password: "1234", grade: 9, class: "Blue", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9red", password: "1234", grade: 9, class: "Red", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9green", password: "1234", grade: 9, class: "Green", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9yellow", password: "1234", grade: 9, class: "Yellow", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9pink", password: "1234", grade: 9, class: "Pink", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9magenta", password: "1234", grade: 9, class: "Magenta", securityQuestion: "", securityAnswer: "" },
  { username: "teacher9purple", password: "1234", grade: 9, class: "Purple", securityQuestion: "", securityAnswer: "" }
];

let students = JSON.parse(localStorage.getItem("students")) || generateStudents();

function generateStudents() {
  const students = [];
  let studentCounter = 1;
  Object.entries(classes).forEach(([grade, classList]) => {
    classList.forEach(cls => {
      for (let i = 1; i <= 3; i++) {
        const name = `${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}${i}`;
        const id = `KJS${String(studentCounter).padStart(3, "0")}`;
        const gender = i % 2 === 0 ? "M" : "F";
        students.push({
          name: name,
          id: id,
          password: "1234",
          grade: parseInt(grade),
          class: cls,
          gender: gender,
          securityQuestion: "",
          securityAnswer: ""
        });
        studentCounter++;
      }
    });
  });
  return students;
}

let positions = JSON.parse(localStorage.getItem("positions")) || generatePositionsWithCandidates();

function generatePositionsWithCandidates() {
  const positions = [
    { name: "School President", scope: "school", candidates: ["sevenblue1", "eightred1", "ninegreen1"] },
    { name: "Governor_Grade_7", scope: "grade_7", candidates: ["sevenblue1", "sevenred1", "sevengreen1"] },
    { name: "Senator_Grade_7", scope: "grade_7", candidates: ["sevenyellow1", "sevenpink1", "sevenmagenta1"] },
    { name: "Girl_Representative_Grade_7", scope: "grade_7", candidates: ["sevenblue3", "sevenred3", "sevengreen3"] },
    { name: "Governor_Grade_8", scope: "grade_8", candidates: ["eightblue1", "eightred1", "eightgreen1"] },
    { name: "Senator_Grade_8", scope: "grade_8", candidates: ["eightyellow1", "eightpink1", "eightmagenta1"] },
    { name: "Girl_Representative_Grade_8", scope: "grade_8", candidates: ["eightblue3", "eightred3", "eightgreen3"] },
    { name: "Governor_Grade_9", scope: "grade_9", candidates: ["nineblue1", "ninered1", "ninegreen1"] },
    { name: "Senator_Grade_9", scope: "grade_9", candidates: ["nineyellow1", "ninepink1", "ninemagenta1"] },
    { name: "Girl_Representative_Grade_9", scope: "grade_9", candidates: ["nineblue3", "ninered3", "ninegreen3"] },
    ...Object.entries(classes).flatMap(([grade, classList]) => 
      classList.flatMap(cls => [
        {
          name: `MCA_Grade_${grade}_${cls}`, 
          scope: `grade_${grade}_class_${cls.toLowerCase()}`, 
          candidates: [`${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}1`, 
                       `${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}2`, 
                       `${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}3`]
        },
        {
          name: `${grade} ${cls} MP`, 
          scope: `grade_${grade}_class_${cls.toLowerCase()}`, 
          candidates: [`${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}1`, 
                       `${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}2`, 
                       `${grade === "7" ? "seven" : grade === "8" ? "eight" : "nine"}${cls.toLowerCase()}3`]
        }
      ])
    )
  ].filter((p, i, arr) => arr.findIndex(p2 => p2.name === p.name) === i);
  return positions;
}

let votes = JSON.parse(localStorage.getItem("votes")) || {};
let metrics = JSON.parse(localStorage.getItem("metrics")) || {};
let weights = JSON.parse(localStorage.getItem("weights")) || {
  studentVotes: 30,
  academics: 15,
  discipline: 10,
  clubs: 10,
  communityService: 5,
  teacher: 10,
  leadership: 10,
  publicSpeaking: 10
};
let pin = localStorage.getItem("pin") || "1234";
let votingOpen = JSON.parse(localStorage.getItem("votingOpen")) !== false;

function showTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(tab => tab.classList.add("hidden"));
  document.getElementById(tabId).classList.remove("hidden");
  document.querySelectorAll(".tab-link").forEach(link => link.classList.remove("font-bold"));
  document.querySelector(`[data-tab="${tabId}"]`).classList.add("font-bold");
  if (tabId === "admin") updateAdminForm();
  if (tabId === "results") computeResults();
  updateTallyDisplay();
}

document.querySelectorAll(".tab-link").forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    showTab(e.target.dataset.tab);
  });
});

function showStudentName() {
  const id = document.getElementById("registerId").value.trim().toUpperCase();
  const student = students.find(s => s.id === id);
  const registerName = document.getElementById("registerName");
  if (student) {
    registerName.value = student.name;
  } else {
    registerName.value = "";
  }
}

function registerStudent() {
  const id = document.getElementById("registerId").value.trim().toUpperCase();
  const password = document.getElementById("registerPassword").value;
  const question = document.getElementById("securityQuestion").value;
  const answer = document.getElementById("securityAnswer").value;
  const registerError = document.getElementById("registerError");
  const registerSuccess = document.getElementById("registerSuccess");

  if (!id.match(/^KJS[0-4][0-9]{2}$|^KJS057$/)) {
    registerError.textContent = "Invalid ID format. Use KJS001 to KJS057.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
    return;
  }

  const student = students.find(s => s.id === id);
  if (!student) {
    registerError.textContent = "Student ID not found.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
    return;
  }

  if (student.password !== "1234") {
    registerError.textContent = "This ID is already registered.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
    return;
  }

  if (password.length < 6) {
    registerError.textContent = "Password must be at least 6 characters.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
    return;
  }

  if (!question || !answer) {
    registerError.textContent = "Security question and answer are required.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
    return;
  }

  student.password = password;
  student.securityQuestion = question;
  student.securityAnswer = answer;
  localStorage.setItem("students", JSON.stringify(students));
  document.getElementById("registerId").value = "";
  document.getElementById("registerPassword").value = "";
  document.getElementById("registerName").value = "";
  document.getElementById("securityQuestion").value = "";
  document.getElementById("securityAnswer").value = "";
  registerError.classList.add("hidden");
  registerSuccess.classList.remove("hidden");
  setTimeout(() => registerSuccess.classList.add("hidden"), 2000);
}

function changePassword() {
  const id = document.getElementById("changeId").value.trim().toUpperCase();
  const oldPassword = document.getElementById("oldPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const changeError = document.getElementById("changeError");
  const changeSuccess = document.getElementById("changeSuccess");

  const student = students.find(s => s.id === id);
  if (!student) {
    changeError.textContent = "Student ID not found.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  if (student.password !== oldPassword) {
    changeError.textContent = "Incorrect old password.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  if (newPassword.length < 6) {
    changeError.textContent = "New password must be at least 6 characters.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  student.password = newPassword;
  localStorage.setItem("students", JSON.stringify(students));
  document.getElementById("changeId").value = "";
  document.getElementById("oldPassword").value = "";
  document.getElementById("newPassword").value = "";
  changeError.classList.add("hidden");
  changeSuccess.classList.remove("hidden");
  setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
}

function showSecurityQuestion() {
  const id = document.getElementById("resetId").value.trim().toUpperCase();
  const student = students.find(s => s.id === id);
  const resetQuestion = document.getElementById("resetQuestion");
  if (student && student.securityQuestion) {
    resetQuestion.value = student.securityQuestion;
  } else {
    resetQuestion.value = "";
  }
}

function resetPassword() {
  const id = document.getElementById("resetId").value.trim().toUpperCase();
  const answer = document.getElementById("resetAnswer").value;
  const newPassword = document.getElementById("resetNewPassword").value;
  const resetError = document.getElementById("resetError");
  const resetSuccess = document.getElementById("resetSuccess");

  const student = students.find(s => s.id === id);
  if (!student) {
    resetError.textContent = "Student ID not found.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  if (student.securityAnswer !== answer) {
    resetError.textContent = "Incorrect security answer.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  if (newPassword.length < 6) {
    resetError.textContent = "New password must be at least 6 characters.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  student.password = newPassword;
  localStorage.setItem("students", JSON.stringify(students));
  document.getElementById("resetId").value = "";
  document.getElementById("resetAnswer").value = "";
  document.getElementById("resetNewPassword").value = "";
  document.getElementById("resetQuestion").value = "";
  resetError.classList.add("hidden");
  resetSuccess.classList.remove("hidden");
  setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
}

function validateVoter() {
  const voterId = document.getElementById("voterId").value.trim().toUpperCase();
  const voterPassword = document.getElementById("voterPassword").value;
  const voterName = document.getElementById("voterName");
  const voterGrade = document.getElementById("voterGrade");
  const voterClass = document.getElementById("voterClass");
  const votePositions = document.getElementById("votePositions");
  const voteError = document.getElementById("voteError");

  votePositions.innerHTML = "";
  voterName.value = "";
  voterGrade.value = "";
  voterClass.value = "";

  const voter = students.find(s => s.id === voterId && s.password === voterPassword);
  if (voter) {
    voterName.value = voter.name;
    voterGrade.value = voter.grade;
    voterClass.value = voter.class;
    voteError.classList.add("hidden");
    updatePositionDropdown(voter);
  } else {
    voteError.textContent = "Invalid Student ID or Password.";
    voteError.classList.remove("hidden");
  }
}

function updatePositionDropdown(voter) {
  const grade = voter.grade;
  const cls = voter.class.toLowerCase();
  const votePositions = document.getElementById("votePositions");
  const relevantPositions = positions.filter(p => 
    p.scope === "school" || 
    p.scope === `grade_${grade}` || 
    p.scope === `grade_${grade}_class_${cls}`
  );
  votePositions.innerHTML = relevantPositions.map(p => `
    <div class="mb-4 flex items-center">
      <label class="w-1/3 text-gray-700 font-semibold">${p.name.replace(/_/g, ' ')}</label>
      <select id="voteCandidate_${p.name}" class="w-2/3 p-2 border rounded">
        <option value="">Select a candidate</option>
        ${p.candidates.filter(c => c !== voter.name).map(c => `<option value="${c}">${c}</option>`).join("")}
      </select>
    </div>
  `).join("");
}

function submitVote() {
  const voterId = document.getElementById("voterId").value.trim().toUpperCase();
  const voterPassword = document.getElementById("voterPassword").value;
  const voteError = document.getElementById("voteError");

  if (!votingOpen) {
    voteError.textContent = "Voting is closed.";
    voteError.classList.remove("hidden");
    return;
  }

  const voter = students.find(s => s.id === voterId && s.password === voterPassword);
  if (!voter) {
    voteError.textContent = "Invalid Student ID or Password.";
    voteError.classList.remove("hidden");
    return;
  }

  const grade = voter.grade;
  const cls = voter.class.toLowerCase();
  const relevantPositions = positions.filter(p => 
    p.scope === "school" || 
    p.scope === `grade_${grade}` || 
    p.scope === `grade_${grade}_class_${cls}`
  );

  const hash = btoa(voterId);
  let hasError = false;
  let votesSubmitted = 0;

  relevantPositions.forEach(p => {
    const candidate = document.getElementById(`voteCandidate_${p.name}`).value;
    if (candidate) {
      if (p.name.includes("Girl_Representative") && students.find(s => s.name === candidate)?.gender !== "F") {
        voteError.textContent = `Only female candidates can be selected for ${p.name.replace(/_/g, ' ')}.`;
        voteError.classList.remove("hidden");
        hasError = true;
        return;
      }

      if (localStorage.getItem(`vote_${hash}_${p.name}`)) {
        voteError.textContent = `You have already voted for ${p.name.replace(/_/g, ' ')}.`;
        voteError.classList.remove("hidden");
        hasError = true;
        return;
      }

      localStorage.setItem(`vote_${hash}_${p.name}`, candidate);
      if (!votes[p.name]) votes[p.name] = {};
      votes[p.name][candidate] = (votes[p.name][candidate] || 0) + 1;
      votesSubmitted++;
    }
  });

  if (hasError) {
    return;
  }

  if (votesSubmitted === 0) {
    voteError.textContent = "Please select at least one candidate.";
    voteError.classList.remove("hidden");
    return;
  }

  localStorage.setItem("votes", JSON.stringify(votes));

  if (VOTE_ENDPOINT) {
    relevantPositions.forEach(p => {
      const candidate = document.getElementById(`voteCandidate_${p.name}`).value;
      if (candidate) {
        fetch(VOTE_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ position: p.name, candidate, voterId: hash })
        }).catch(error => console.error("Error sending vote to endpoint:", error));
      }
    });
  }

  alert("Votes submitted successfully!");
  voteError.classList.add("hidden");
  document.getElementById("voterId").value = "";
  document.getElementById("voterPassword").value = "";
  document.getElementById("voterName").value = "";
  document.getElementById("voterGrade").value = "";
  document.getElementById("voterClass").value = "";
  document.getElementById("votePositions").innerHTML = "";
  updateTallyDisplay();
}

function loginTeacher() {
  const username = document.getElementById("teacherUsername").value.trim();
  const password = document.getElementById("teacherPassword").value;
  const teacherLoginError = document.getElementById("teacherLoginError");

  const teacher = teachers.find(t => t.username === username && t.password === password);
  if (teacher) {
    document.getElementById("teacherForm").classList.remove("hidden");
    document.getElementById("teacherChangePassword").classList.remove("hidden");
    document.getElementById("teacherResetPassword").classList.remove("hidden");
    document.getElementById("teacherStudentManagement").classList.remove("hidden");
    updateTeacherMetricsTable(teacher);
    teacherLoginError.classList.add("hidden");
  } else {
    teacherLoginError.textContent = "Invalid username or password.";
    teacherLoginError.classList.remove("hidden");
  }
}

function updateTeacherMetricsTable(teacher) {
  const tableBody = document.getElementById("teacherMetricsTable");
  const classStudents = students.filter(s => s.grade === teacher.grade && s.class === teacher.class);
  tableBody.innerHTML = classStudents.map(s => {
    const m = metrics[s.name] || {};
    return `
      <tr>
        <td class="border p-2"><span title="ID: ${s.id}">${s.name}</span></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_academics" value="${m.academics || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_discipline" value="${m.discipline || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_clubs" value="${m.clubs || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_communityService" value="${m.communityService || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_teacher" value="${m.teacher || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_leadership" value="${m.leadership || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_publicSpeaking" value="${m.publicSpeaking || ''}"></td>
      </tr>
    `;
  }).join("");
}

function saveTeacherMetrics() {
  const tableBody = document.getElementById("teacherMetricsTable");
  const teacher = teachers.find(t => t.username === document.getElementById("teacherUsername").value.trim());
  const classStudents = students.filter(s => s.grade === teacher.grade && s.class === teacher.class);
  let hasInvalid = false;

  classStudents.forEach(s => {
    const academics = parseInt(document.getElementById(`metric_${s.name}_academics`).value);
    const discipline = parseInt(document.getElementById(`metric_${s.name}_discipline`).value);
    const clubs = parseInt(document.getElementById(`metric_${s.name}_clubs`).value);
    const communityService = parseInt(document.getElementById(`metric_${s.name}_communityService`).value);
    const teacherScore = parseInt(document.getElementById(`metric_${s.name}_teacher`).value);
    const leadership = parseInt(document.getElementById(`metric_${s.name}_leadership`).value);
    const publicSpeaking = parseInt(document.getElementById(`metric_${s.name}_publicSpeaking`).value);

    if (!isNaN(academics) || !isNaN(discipline) || !isNaN(clubs) || !isNaN(communityService) || !isNaN(teacherScore) || !isNaN(leadership) || !isNaN(publicSpeaking)) {
      if (isNaN(academics) || isNaN(discipline) || isNaN(clubs) || isNaN(communityService) || isNaN(teacherScore) || isNaN(leadership) || isNaN(publicSpeaking) ||
          academics < 0 || academics > 100 || discipline < 0 || discipline > 100 || clubs < 0 || clubs > 100 ||
          communityService < 0 || communityService > 100 || teacherScore < 0 || teacherScore > 100 || leadership < 0 || leadership > 100 ||
          publicSpeaking < 0 || publicSpeaking > 100) {
        hasInvalid = true;
        return;
      }
      metrics[s.name] = { academics, discipline, clubs, communityService, teacher: teacherScore, leadership, publicSpeaking };
    }
  });

  if (hasInvalid) {
    document.getElementById("teacherSaveError").classList.remove("hidden");
    return;
  }

  localStorage.setItem("metrics", JSON.stringify(metrics));
  document.getElementById("teacherSaveError").classList.add("hidden");
  document.getElementById("teacherSaveStatus").classList.remove("hidden");
  setTimeout(() => document.getElementById("teacherSaveStatus").classList.add("hidden"), 2000);
  computeResults();
}

function changeTeacherPassword() {
  const username = document.getElementById("teacherUsername").value.trim();
  const oldPassword = document.getElementById("teacherOldPassword").value;
  const newPassword = document.getElementById("teacherNewPassword").value;
  const changeError = document.getElementById("teacherChangeError");
  const changeSuccess = document.getElementById("teacherChangeSuccess");

  const teacher = teachers.find(t => t.username === username);
  if (!teacher) {
    changeError.textContent = "Teacher not found.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  if (teacher.password !== oldPassword) {
    changeError.textContent = "Incorrect old password.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  if (newPassword.length < 6) {
    changeError.textContent = "New password must be at least 6 characters.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
    return;
  }

  teacher.password = newPassword;
  localStorage.setItem("teachers", JSON.stringify(teachers));
  document.getElementById("teacherOldPassword").value = "";
  document.getElementById("teacherNewPassword").value = "";
  changeError.classList.add("hidden");
  changeSuccess.classList.remove("hidden");
  setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
}

function showTeacherSecurityQuestion() {
  const username = document.getElementById("teacherResetUsername").value.trim();
  const teacher = teachers.find(t => t.username === username);
  const resetQuestion = document.getElementById("teacherResetQuestion");
  if (teacher && teacher.securityQuestion) {
    resetQuestion.value = teacher.securityQuestion;
  } else {
    resetQuestion.value = "";
  }
}

function resetTeacherPassword() {
  const username = document.getElementById("teacherResetUsername").value.trim();
  const answer = document.getElementById("teacherResetAnswer").value;
  const newPassword = document.getElementById("teacherResetNewPassword").value;
  const resetError = document.getElementById("teacherResetError");
  const resetSuccess = document.getElementById("teacherResetSuccess");

  const teacher = teachers.find(t => t.username === username);
  if (!teacher) {
    resetError.textContent = "Teacher not found.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  if (teacher.securityAnswer !== answer) {
    resetError.textContent = "Incorrect security answer.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  if (newPassword.length < 6) {
    resetError.textContent = "New password must be at least 6 characters.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
    return;
  }

  teacher.password = newPassword;
  localStorage.setItem("teachers", JSON.stringify(teachers));
  document.getElementById("teacherResetUsername").value = "";
  document.getElementById("teacherResetAnswer").value = "";
  document.getElementById("teacherResetNewPassword").value = "";
  document.getElementById("teacherResetQuestion").value = "";
  resetError.classList.add("hidden");
  resetSuccess.classList.remove("hidden");
  setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
}

function addStudentToClass() {
  const teacherUsername = document.getElementById("teacherUsername").value.trim();
  const studentId = document.getElementById("studentIdManage").value.trim().toUpperCase();
  const studentName = document.getElementById("studentNameManage").value.trim();
  const studentManageError = document.getElementById("studentManageError");
  const studentManageSuccess = document.getElementById("studentManageSuccess");

  const teacher = teachers.find(t => t.username === teacherUsername);
  if (!teacher) {
    studentManageError.textContent = "Teacher not logged in.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  if (!studentId.match(/^KJS[0-4][0-9]{2}$|^KJS057$/)) {
    studentManageError.textContent = "Invalid ID format. Use KJS001 to KJS057.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  if (!studentName) {
    studentManageError.textContent = "Student name is required.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  const existingStudent = students.find(s => s.id === studentId || s.name === studentName);
  if (existingStudent) {
    studentManageError.textContent = "Student ID or name already exists.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  const newStudent = {
    name: studentName,
    id: studentId,
    password: "1234",
    grade: teacher.grade,
    class: teacher.class,
    gender: "U",
    securityQuestion: "",
    securityAnswer: ""
  };

  students.push(newStudent);
  localStorage.setItem("students", JSON.stringify(students));
  updateTeacherMetricsTable(teacher);
  document.getElementById("studentIdManage").value = "";
  document.getElementById("studentNameManage").value = "";
  studentManageError.classList.add("hidden");
  studentManageSuccess.textContent = "Student added successfully!";
  studentManageSuccess.classList.remove("hidden");
  setTimeout(() => studentManageSuccess.classList.add("hidden"), 2000);
}

function removeStudentFromClass() {
  const teacherUsername = document.getElementById("teacherUsername").value.trim();
  const studentId = document.getElementById("studentIdManage").value.trim().toUpperCase();
  const studentManageError = document.getElementById("studentManageError");
  const studentManageSuccess = document.getElementById("studentManageSuccess");

  const teacher = teachers.find(t => t.username === teacherUsername);
  if (!teacher) {
    studentManageError.textContent = "Teacher not logged in.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  if (!studentId.match(/^KJS[0-4][0-9]{2}$|^KJS057$/)) {
    studentManageError.textContent = "Invalid ID format. Use KJS001 to KJS057.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  const studentIndex = students.findIndex(s => s.id === studentId && s.grade === teacher.grade && s.class === teacher.class);
  if (studentIndex === -1) {
    studentManageError.textContent = "Student not found in this class.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
    return;
  }

  const student = students[studentIndex];
  positions.forEach(p => {
    p.candidates = p.candidates.filter(c => c !== student.name);
  });
  delete metrics[student.name];
  students.splice(studentIndex, 1);
  localStorage.setItem("students", JSON.stringify(students));
  localStorage.setItem("positions", JSON.stringify(positions));
  localStorage.setItem("metrics", JSON.stringify(metrics));
  updateTeacherMetricsTable(teacher);
  document.getElementById("studentIdManage").value = "";
  document.getElementById("studentNameManage").value = "";
  studentManageError.classList.add("hidden");
  studentManageSuccess.textContent = "Student removed successfully!";
  studentManageSuccess.classList.remove("hidden");
  setTimeout(() => studentManageSuccess.classList.add("hidden"), 2000);
  computeResults();
}

function clearAllStudents() {
  if (!confirm("Are you sure you want to clear all students? This will remove all student data and cannot be undone.")) {
    return;
  }

  students = generateStudents();
  metrics = {};
  positions = generatePositionsWithCandidates();
  votes = {};
  localStorage.setItem("students", JSON.stringify(students));
  localStorage.setItem("metrics", JSON.stringify(metrics));
  localStorage.setItem("positions", JSON.stringify(positions));
  localStorage.setItem("votes", JSON.stringify(votes));
  const teacher = teachers.find(t => t.username === document.getElementById("teacherUsername").value.trim());
  if (teacher) {
    updateTeacherMetricsTable(teacher);
  }
  document.getElementById("studentManageSuccess").textContent = "All students cleared and reset.";
  document.getElementById("studentManageSuccess").classList.remove("hidden");
  setTimeout(() => document.getElementById("studentManageSuccess").classList.add("hidden"), 2000);
  computeResults();
}

function unlockAdmin() {
  const enteredPin = document.getElementById("adminPin").value;
  if (enteredPin === pin) {
    document.getElementById("adminForm").classList.remove("hidden");
    document.getElementById("adminPinError").classList.add("hidden");
    document.getElementById("votingToggleBtn").textContent = votingOpen ? "Close Voting" : "Open Voting";
    document.getElementById("votingStatus").textContent = votingOpen ? "Voting is open." : "Voting is closed. Tallies are visible.";
    updateAdminForm();
  } else {
    document.getElementById("adminPinError").classList.remove("hidden");
  }
}

function updateAdminForm() {
  updatePositionListAdmin();
  updateTeacherListAdmin();
  updateCandidateList();
  document.getElementById("weightStudentVotes").value = weights.studentVotes;
  document.getElementById("weightAcademics").value = weights.academics;
  document.getElementById("weightDiscipline").value = weights.discipline;
  document.getElementById("weightClubs").value = weights.clubs;
  document.getElementById("weightCommunityService").value = weights.communityService;
  document.getElementById("weightTeacher").value = weights.teacher;
  document.getElementById("weightLeadership").value = weights.leadership;
  document.getElementById("weightPublicSpeaking").value = weights.publicSpeaking;
}

function addPosition() {
  const newPosition = document.getElementById("newPosition").value.trim();
  if (newPosition) {
    positions.push({ name: newPosition, scope: "school", candidates: [] });
    localStorage.setItem("positions", JSON.stringify(positions));
    document.getElementById("newPosition").value = "";
    updatePositionListAdmin();
    updateCandidateList();
    alert("Position added successfully!");
  } else {
    alert("Please enter a position name.");
  }
}

function updatePositionListAdmin() {
  const positionList = document.getElementById("positionList");
  positionList.innerHTML = positions.map(p => `
    <div class="flex justify-between items-center p-2 border-b">
      <span>${p.name.replace(/_/g, ' ')}</span>
      <button onclick="removePosition('${p.name}')" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Remove</button>
    </div>
  `).join("");
  const candidatePosition = document.getElementById("candidatePosition");
  candidatePosition.innerHTML = `<option value="">Select a position</option>` + 
    positions.map(p => `<option value="${p.name}">${p.name.replace(/_/g, ' ')}</option>`).join("");
}

function removePosition(positionName) {
  positions = positions.filter(p => p.name !== positionName);
  delete votes[positionName];
  localStorage.setItem("positions", JSON.stringify(positions));
  localStorage.setItem("votes", JSON.stringify(votes));
  updatePositionListAdmin();
  updateCandidateList();
  computeResults();
}

function addTeacher() {
  const input = document.getElementById("newTeacher").value.trim();
  const [username, grade, cls, password] = input.split(",");
  if (username && grade && cls && password) {
    const validGrade = Object.keys(classes).includes(grade);
    const validClass = classes[grade]?.includes(cls);
    if (!validGrade || !validClass) {
      alert("Invalid grade or class.");
      return;
    }
    if (teachers.find(t => t.username === username)) {
      alert("Teacher username already exists.");
      return;
    }
    teachers.push({ username, password, grade: parseInt(grade), class: cls, securityQuestion: "", securityAnswer: "" });
    localStorage.setItem("teachers", JSON.stringify(teachers));
    document.getElementById("newTeacher").value = "";
    updateTeacherListAdmin();
    alert("Teacher added successfully!");
  } else {
    alert("Please enter username, grade, class, and password (e.g., teacher7blue,7,Blue,1234).");
  }
}

function updateTeacherListAdmin() {
  const teacherList = document.getElementById("teacherList");
  teacherList.innerHTML = teachers.map(t => `
    <div class="flex justify-between items-center p-2 border-b">
      <span>${t.username} (Grade ${t.grade} ${t.class})</span>
      <button onclick="removeTeacher('${t.username}')" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Remove</button>
    </div>
  `).join("");
}

function removeTeacher(username) {
  teachers = teachers.filter(t => t.username !== username);
  localStorage.setItem("teachers", JSON.stringify(teachers));
  updateTeacherListAdmin();
}

function updateCandidateList() {
  const positionName = document.getElementById("candidatePosition").value;
  const candidateList = document.getElementById("candidateList");
  const position = positions.find(p => p.name === positionName);
  if (position) {
    candidateList.innerHTML = `
      <h4 class="text-lg font-semibold mb-2">Candidates for ${position.name.replace(/_/g, ' ')}</h4>
      ${position.candidates.length > 0 ? position.candidates.map(c => `
        <div class="flex justify-between items-center p-2 border-b">
          <span>${c} (${students.find(s => s.name === c)?.id})</span>
        </div>
      `).join("") : "<p>No candidates yet.</p>"}
    `;
  } else {
    candidateList.innerHTML = "<p>Select a position to view candidates.</p>";
  }
}

function addCandidate() {
  const positionName = document.getElementById("candidatePosition").value;
  const studentId = document.getElementById("candidateId").value.trim().toUpperCase();
  const candidateError = document.getElementById("candidateError");
  const candidateSuccess = document.getElementById("candidateSuccess");

  if (!positionName) {
    candidateError.textContent = "Please select a position.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (!studentId.match(/^KJS[0-4][0-9]{2}$|^KJS057$/)) {
    candidateError.textContent = "Invalid ID format. Use KJS001 to KJS057.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  const student = students.find(s => s.id === studentId);
  if (!student) {
    candidateError.textContent = "Student ID not found.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  const position = positions.find(p => p.name === positionName);
  if (!position) {
    candidateError.textContent = "Position not found.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (position.name.includes("Girl_Representative") && student.gender !== "F") {
    candidateError.textContent = "Only female students can be candidates for Girl Representative positions.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (position.scope !== "school" && !position.scope.includes(`grade_${student.grade}`)) {
    candidateError.textContent = `Student must be in grade ${position.scope.split('_')[1]} to be a candidate for this position.`;
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (position.scope.includes("class") && !position.scope.includes(`class_${student.class.toLowerCase()}`)) {
    candidateError.textContent = `Student must be in class ${position.scope.split('_')[3]} to be a candidate for this position.`;
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (position.candidates.includes(student.name)) {
    candidateError.textContent = "Student is already a candidate for this position.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  position.candidates.push(student.name);
  localStorage.setItem("positions", JSON.stringify(positions));
document.getElementById("candidateId").value = "";
  candidateError.classList.add("hidden");
  candidateSuccess.textContent = "Candidate added successfully!";
  candidateSuccess.classList.remove("hidden");
  setTimeout(() => candidateSuccess.classList.add("hidden"), 2000);
  updateCandidateList();
}

function removeCandidate() {
  const positionName = document.getElementById("candidatePosition").value;
  const studentId = document.getElementById("candidateId").value.trim().toUpperCase();
  const candidateError = document.getElementById("candidateError");
  const candidateSuccess = document.getElementById("candidateSuccess");

  if (!positionName) {
    candidateError.textContent = "Please select a position.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  if (!studentId.match(/^KJS[0-4][0-9]{2}$|^KJS057$/)) {
    candidateError.textContent = "Invalid ID format. Use KJS001 to KJS057.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  const student = students.find(s => s.id === studentId);
  if (!student) {
    candidateError.textContent = "Student ID not found.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  const position = positions.find(p => p.name === positionName);
  if (!position) {
    candidateError.textContent = "Position not found.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  const candidateIndex = position.candidates.indexOf(student.name);
  if (candidateIndex === -1) {
    candidateError.textContent = "Student is not a candidate for this position.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
    return;
  }

  position.candidates.splice(candidateIndex, 1);
  localStorage.setItem("positions", JSON.stringify(positions));
  document.getElementById("candidateId").value = "";
  candidateError.classList.add("hidden");
  candidateSuccess.textContent = "Candidate removed successfully!";
  candidateSuccess.classList.remove("hidden");
  setTimeout(() => candidateSuccess.classList.add("hidden"), 2000);
  updateCandidateList();
}

function clearAllCandidates() {
  if (!confirm("Are you sure you want to clear all candidates? This cannot be undone.")) {
    return;
  }

  positions.forEach(p => p.candidates = []);
  localStorage.setItem("positions", JSON.stringify(positions));
  updateCandidateList();
  updatePositionListAdmin();
  alert("All candidates cleared.");
}

function toggleVoting() {
  votingOpen = !votingOpen;
  localStorage.setItem("votingOpen", JSON.stringify(votingOpen));
  document.getElementById("votingToggleBtn").textContent = votingOpen ? "Close Voting" : "Open Voting";
  document.getElementById("votingStatus").textContent = votingOpen ? "Voting is open." : "Voting is closed. Tallies are visible.";
  updateTallyDisplay();
}

function updateTallyDisplay() {
  const tallyResults = document.getElementById("tallyResults");
  const tallyContainer = document.getElementById("tallyContainer");
  if (!votingOpen) {
    tallyResults.classList.remove("hidden");
    tallyContainer.innerHTML = positions.map(p => {
      const voteCounts = votes[p.name] || {};
      const totalVotes = Object.values(voteCounts).reduce((sum, count) => sum + count, 0);
      return `
        <div class="bg-gray-100 p-4 rounded">
          <h4 class="font-semibold">${p.name.replace(/_/g, ' ')}</h4>
          ${p.candidates.map(c => `
            <div class="flex justify-between">
              <span>${c}</span>
              <span>${voteCounts[c] || 0} votes (${totalVotes ? ((voteCounts[c] || 0) / totalVotes * 100).toFixed(1) : 0}%) ${totalVotes ? createBar((voteCounts[c] || 0) / totalVotes * 100) : ''}</span>
            </div>
          `).join("")}
        </div>
      `;
    }).join("");
  } else {
    tallyResults.classList.add("hidden");
  }
}

function createBar(percentage) {
  return `
    <div class="w-full bg-gray-200 rounded h-4 mt-1">
      <div class="bg-blue-500 h-4 rounded" style="width: ${percentage}%"></div>
    </div>
  `;
}

function saveWeights() {
  const studentVotes = parseInt(document.getElementById("weightStudentVotes").value);
  const academics = parseInt(document.getElementById("weightAcademics").value);
  const discipline = parseInt(document.getElementById("weightDiscipline").value);
  const clubs = parseInt(document.getElementById("weightClubs").value);
  const communityService = parseInt(document.getElementById("weightCommunityService").value);
  const teacher = parseInt(document.getElementById("weightTeacher").value);
  const leadership = parseInt(document.getElementById("weightLeadership").value);
  const publicSpeaking = parseInt(document.getElementById("weightPublicSpeaking").value);

  const total = studentVotes + academics + discipline + clubs + communityService + teacher + leadership + publicSpeaking;
  if (total !== 100 || isNaN(total)) {
    document.getElementById("weightsError").classList.remove("hidden");
    return;
  }

  weights = { studentVotes, academics, discipline, clubs, communityService, teacher, leadership, publicSpeaking };
  localStorage.setItem("weights", JSON.stringify(weights));
  document.getElementById("weightsError").classList.add("hidden");
  alert("Weights saved successfully!");
  computeResults();
}

function computeResults() {
  const resultsTable = document.getElementById("resultsTable");
  resultsTable.innerHTML = positions.map(p => {
    const voteCounts = votes[p.name] || {};
    const totalVotes = Object.values(voteCounts).reduce((sum, count) => sum + count, 0);
    const scores = p.candidates.map(c => {
      const m = metrics[c] || {};
      const voteScore = totalVotes ? (voteCounts[c] || 0) / totalVotes * 100 : 0;
      const finalScore = (
        (voteScore * weights.studentVotes) +
        ((m.academics || 0) * weights.academics) +
        ((m.discipline || 0) * weights.discipline) +
        ((m.clubs || 0) * weights.clubs) +
        ((m.communityService || 0) * weights.communityService) +
        ((m.teacher || 0) * weights.teacher) +
        ((m.leadership || 0) * weights.leadership) +
        ((m.publicSpeaking || 0) * weights.publicSpeaking)
      ) / 100;
      return { candidate: c, voteScore, finalScore, metrics: m };
    });
    scores.sort((a, b) => b.finalScore - a.finalScore);
    return `
      <div class="mb-4">
        <h3 class="text-lg font-semibold">${p.name.replace(/_/g, ' ')}</h3>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-gray-100">
              <th class="border p-2">Candidate</th>
              <th class="border p-2">Student Votes</th>
              <th class="border p-2">Academics</th>
              <th class="border p-2">Discipline</th>
              <th class="border p-2">Clubs</th>
              <th class="border p-2">Comm. Service</th>
              <th class="border p-2">Teacher</th>
              <th class="border p-2">Leadership</th>
              <th class="border p-2">Public Speaking</th>
              <th class="border p-2">Final Score</th>
            </tr>
          </thead>
          <tbody>
            ${scores.map(s => `
              <tr>
                <td class="border p-2">${s.candidate} (${students.find(st => st.name === s.candidate)?.id})</td>
                <td class="border p-2 text-right">${s.voteScore.toFixed(1)}%</td>
                <td class="border p-2 text-right">${s.metrics.academics || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.discipline || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.clubs || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.communityService || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.teacher || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.leadership || '-'}</td>
                <td class="border p-2 text-right">${s.metrics.publicSpeaking || '-'}</td>
                <td class="border p-2 text-right">${s.finalScore.toFixed(1)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }).join("");
}

function exportResults() {
  const csv = ["Position,Candidate,Student Votes,Academics,Discipline,Clubs,Community Service,Teacher,Leadership,Public Speaking,Final Score"];
  positions.forEach(p => {
    const voteCounts = votes[p.name] || {};
    const totalVotes = Object.values(voteCounts).reduce((sum, count) => sum + count, 0);
    p.candidates.forEach(c => {
      const m = metrics[c] || {};
      const voteScore = totalVotes ? (voteCounts[c] || 0) / totalVotes * 100 : 0;
      const finalScore = (
        (voteScore * weights.studentVotes) +
        ((m.academics || 0) * weights.academics) +
        ((m.discipline || 0) * weights.discipline) +
        ((m.clubs || 0) * weights.clubs) +
        ((m.communityService || 0) * weights.communityService) +
        ((m.teacher || 0) * weights.teacher) +
        ((m.leadership || 0) * weights.leadership) +
        ((m.publicSpeaking || 0) * weights.publicSpeaking)
      ) / 100;
      csv.push(`${p.name.replace(/_/g, ' ')},${c} (${students.find(s => s.name === c)?.id}),${voteScore.toFixed(1)}%,${m.academics || '-'},${m.discipline || '-'},${m.clubs || '-'},${m.communityService || '-'},${m.teacher || '-'},${m.leadership || '-'},${m.publicSpeaking || '-'},${finalScore.toFixed(1)}`);
    });
  });
  const blob = new Blob([csv.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "election_results.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function exportVotes() {
  const csv = ["Position,Voter Hash,Candidate"];
  Object.keys(votes).forEach(position => {
    Object.keys(votes[position]).forEach(candidate => {
      const count = votes[position][candidate];
      for (let i = 0; i < count; i++) {
        csv.push(`${position.replace(/_/g, ' ')},anonymous,${candidate}`);
      }
    });
  });
  const blob = new Blob([csv.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "votes_export.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function updatePin() {
  const newPin = document.getElementById("newPin").value;
  if (newPin.length < 4) {
    alert("PIN must be at least 4 characters.");
    return;
  }
  pin = newPin;
  localStorage.setItem("pin", pin);
  document.getElementById("newPin").value = "";
  alert("PIN updated successfully!");
}

function downloadBackup() {
  const backup = { students, teachers, positions, votes, metrics, weights, pin, votingOpen };
  const blob = new Blob([JSON.stringify(backup, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "election_backup.json";
  a.click();
  URL.revokeObjectURL(url);
}

function importBackup() {
  const fileInput = document.getElementById("importBackup");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file to import.");
    return;
  }
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const data = JSON.parse(e.target.result);
      students = data.students || generateStudents();
      teachers = data.teachers || [];
      positions = data.positions || generatePositionsWithCandidates();
      votes = data.votes || {};
      metrics = data.metrics || {};
      weights = data.weights || {
        studentVotes: 30,
        academics: 15,
        discipline: 10,
        clubs: 10,
        communityService: 5,
        teacher: 10,
        leadership: 10,
        publicSpeaking: 10
      };
      pin = data.pin || "1234";
      votingOpen = data.votingOpen !== false;
      localStorage.setItem("students", JSON.stringify(students));
      localStorage.setItem("teachers", JSON.stringify(teachers));
      localStorage.setItem("positions", JSON.stringify(positions));
      localStorage.setItem("votes", JSON.stringify(votes));
      localStorage.setItem("metrics", JSON.stringify(metrics));
      localStorage.setItem("weights", JSON.stringify(weights));
      localStorage.setItem("pin", pin);
      localStorage.setItem("votingOpen", JSON.stringify(votingOpen));
      updateAdminForm();
      computeResults();
      updateTallyDisplay();
      alert("Backup imported successfully!");
    } catch (error) {
      alert("Invalid backup file.");
    }
  };
  reader.readAsText(file);
}

function factoryReset() {
  if (!confirm("Are you sure you want to reset all data? This cannot be undone.")) {
    return;
  }
  students = generateStudents();
  teachers = [
    { username: "teacher7blue", password: "1234", grade: 7, class: "Blue", securityQuestion: "", securityAnswer: "" },
    { username: "teacher7red", password: "1234", grade: 7, class: "Red", securityQuestion: "", securityAnswer: "" },
    { username: "teacher7green", password: "1234", grade: 7, class: "Green", securityQuestion: "", securityAnswer: "" },
    { username: "teacher7yellow", password: "1234", grade: 7, class: "Yellow", securityQuestion: "", securityAnswer: "" },
    { username: "teacher7pink", password: "1234", grade: 7, class: "Pink", securityQuestion: "", securityAnswer: "" },
    { username: "teacher7magenta", password: "1234", grade: 7, class: "Magenta", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8blue", password: "1234", grade: 8, class: "Blue", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8red", password: "1234", grade: 8, class: "Red", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8green", password: "1234", grade: 8, class: "Green", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8yellow", password: "1234", grade: 8, class: "Yellow", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8pink", password: "1234", grade: 8, class: "Pink", securityQuestion: "", securityAnswer: "" },
    { username: "teacher8magenta", password: "1234", grade: 8, class: "Magenta", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9blue", password: "1234", grade: 9, class: "Blue", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9red", password: "1234", grade: 9, class: "Red", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9green", password: "1234", grade: 9, class: "Green", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9yellow", password: "1234", grade: 9, class: "Yellow", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9pink", password: "1234", grade: 9, class: "Pink", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9magenta", password: "1234", grade: 9, class: "Magenta", securityQuestion: "", securityAnswer: "" },
    { username: "teacher9purple", password: "1234", grade: 9, class: "Purple", securityQuestion: "", securityAnswer: "" }
  ];
  positions = generatePositionsWithCandidates();
  votes = {};
  metrics = {};
  weights = {
    studentVotes: 30,
    academics: 15,
    discipline: 10,
    clubs: 10,
    communityService: 5,
    teacher: 10,
    leadership: 10,
    publicSpeaking: 10
  };
  pin = "1234";
  votingOpen = true;
  localStorage.setItem("students", JSON.stringify(students));
  localStorage.setItem("teachers", JSON.stringify(teachers));
  localStorage.setItem("positions", JSON.stringify(positions));
  localStorage.setItem("votes", JSON.stringify(votes));
  localStorage.setItem("metrics", JSON.stringify(metrics));
  localStorage.setItem("weights", JSON.stringify(weights));
  localStorage.setItem("pin", pin);
  localStorage.setItem("votingOpen", JSON.stringify(votingOpen));
  document.getElementById("adminForm").classList.add("hidden");
  document.getElementById("adminPin").value = "";
  updateAdminForm();
  computeResults();
  updateTallyDisplay();
  alert("System reset to factory settings.");
}

// Initialize the page
showTab("register");
updateTallyDisplay();