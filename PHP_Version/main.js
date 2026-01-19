const API_ENDPOINT = "api.php";
const classes = {
  7: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"],
  8: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"],
  9: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"]
};

async function showTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(tab => tab.classList.add("hidden"));
  document.getElementById(tabId).classList.remove("hidden");
  document.querySelectorAll(".tab-link").forEach(link => link.classList.remove("font-bold"));
  document.querySelector(`[data-tab="${tabId}"]`).classList.add("font-bold");
  if (tabId === "admin") await updateAdminForm();
  if (tabId === "results") await computeResults();
  if (tabId === "about") await updateWeightsList();
  if (tabId === "vote") await updateTallyDisplay();
}

document.querySelectorAll(".tab-link").forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    showTab(e.target.dataset.tab);
  });
});

async function showStudentName() {
  const id = document.getElementById("registerId").value.trim().toUpperCase();
  const registerName = document.getElementById("registerName");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_student&id=${encodeURIComponent(id)}`);
    const student = await response.json();
    registerName.value = student.success ? student.student.name : "";
  } catch (error) {
    console.error("Error fetching student:", error);
    registerName.value = "";
  }
}

async function registerStudent() {
  const id = document.getElementById("registerId").value.trim().toUpperCase();
  const password = document.getElementById("registerPassword").value;
  const question = document.getElementById("securityQuestion").value;
  const answer = document.getElementById("securityAnswer").value;
  const registerError = document.getElementById("registerError");
  const registerSuccess = document.getElementById("registerSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=register_student`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, password, security_question: question, security_answer: answer })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("registerId").value = "";
      document.getElementById("registerPassword").value = "";
      document.getElementById("registerName").value = "";
      document.getElementById("securityQuestion").value = "";
      document.getElementById("securityAnswer").value = "";
      registerError.classList.add("hidden");
      registerSuccess.classList.remove("hidden");
      setTimeout(() => registerSuccess.classList.add("hidden"), 2000);
    } else {
      registerError.textContent = result.message;
      registerError.classList.remove("hidden");
      registerSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error registering student:", error);
    registerError.textContent = "Error registering student.";
    registerError.classList.remove("hidden");
    registerSuccess.classList.add("hidden");
  }
}

async function changePassword() {
  const id = document.getElementById("changeId").value.trim().toUpperCase();
  const oldPassword = document.getElementById("oldPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const changeError = document.getElementById("changeError");
  const changeSuccess = document.getElementById("changeSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=change_student_password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, old_password: oldPassword, new_password: newPassword })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("changeId").value = "";
      document.getElementById("oldPassword").value = "";
      document.getElementById("newPassword").value = "";
      changeError.classList.add("hidden");
      changeSuccess.classList.remove("hidden");
      setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
    } else {
      changeError.textContent = result.message;
      changeError.classList.remove("hidden");
      changeSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error changing password:", error);
    changeError.textContent = "Error changing password.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
  }
}

async function showSecurityQuestion() {
  const id = document.getElementById("resetId").value.trim().toUpperCase();
  const resetQuestion = document.getElementById("resetQuestion");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_security_question&id=${encodeURIComponent(id)}`);
    const result = await response.json();
    resetQuestion.value = result.success && result.security_question ? result.security_question : "";
  } catch (error) {
    console.error("Error fetching security question:", error);
    resetQuestion.value = "";
  }
}

async function resetPassword() {
  const id = document.getElementById("resetId").value.trim().toUpperCase();
  const answer = document.getElementById("resetAnswer").value;
  const newPassword = document.getElementById("resetNewPassword").value;
  const resetError = document.getElementById("resetError");
  const resetSuccess = document.getElementById("resetSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=reset_student_password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, security_answer: answer, new_password: newPassword })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("resetId").value = "";
      document.getElementById("resetAnswer").value = "";
      document.getElementById("resetNewPassword").value = "";
      document.getElementById("resetQuestion").value = "";
      resetError.classList.add("hidden");
      resetSuccess.classList.remove("hidden");
      setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
    } else {
      resetError.textContent = result.message;
      resetError.classList.remove("hidden");
      resetSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error resetting password:", error);
    resetError.textContent = "Error resetting password.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
  }
}

async function validateVoter() {
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
  try {
    const response = await fetch(`${API_ENDPOINT}?action=validate_voter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: voterId, password: voterPassword })
    });
    const result = await response.json();
    if (result.success) {
      voterName.value = result.student.name;
      voterGrade.value = result.student.grade;
      voterClass.value = result.student.class;
      voteError.classList.add("hidden");
      await updatePositionDropdown(result.student);
    } else {
      voteError.textContent = result.message;
      voteError.classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error validating voter:", error);
    voteError.textContent = "Error validating voter.";
    voteError.classList.remove("hidden");
  }
}

async function updatePositionDropdown(voter) {
  const votePositions = document.getElementById("votePositions");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_positions&grade=${voter.grade}&class=${encodeURIComponent(voter.class)}`);
    const positions = await response.json();
    votePositions.innerHTML = positions.map(p => `
      <div class="mb-4 flex items-center">
        <label class="w-1/3 text-gray-700 font-semibold">${p.name.replace(/_/g, ' ')}</label>
        <select id="voteCandidate_${p.id}" class="w-2/3 p-2 border rounded">
          <option value="">Select a candidate</option>
          ${p.candidates.filter(c => c !== voter.name).map(c => `<option value="${c}">${c}</option>`).join("")}
        </select>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error fetching positions:", error);
  }
}

async function submitVote() {
  const voterId = document.getElementById("voterId").value.trim().toUpperCase();
  const voterPassword = document.getElementById("voterPassword").value;
  const voteError = document.getElementById("voteError");
  try {
    const voterResponse = await fetch(`${API_ENDPOINT}?action=validate_voter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: voterId, password: voterPassword })
    });
    const voterResult = await voterResponse.json();
    if (!voterResult.success) {
      voteError.textContent = voterResult.message;
      voteError.classList.remove("hidden");
      return;
    }
    const voter = voterResult.student;
    const positionsResponse = await fetch(`${API_ENDPOINT}?action=get_positions&grade=${voter.grade}&class=${encodeURIComponent(voter.class)}`);
    const positions = await positionsResponse.json();
    const hash = btoa(voterId);
    let votesSubmitted = [];
    for (const p of positions) {
      const candidate = document.getElementById(`voteCandidate_${p.id}`).value;
      if (candidate) {
        votesSubmitted.push({ position_id: p.id, candidate, voter_hash: hash });
      }
    }
    if (votesSubmitted.length === 0) {
      voteError.textContent = "Please select at least one candidate.";
      voteError.classList.remove("hidden");
      return;
    }
    const response = await fetch(`${API_ENDPOINT}?action=submit_votes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ votes: votesSubmitted })
    });
    const result = await response.json();
    if (result.success) {
      alert("Votes submitted successfully!");
      voteError.classList.add("hidden");
      document.getElementById("voterId").value = "";
      document.getElementById("voterPassword").value = "";
      document.getElementById("voterName").value = "";
      document.getElementById("voterGrade").value = "";
      document.getElementById("voterClass").value = "";
      document.getElementById("votePositions").innerHTML = "";
      await updateTallyDisplay();
    } else {
      voteError.textContent = result.message;
      voteError.classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error submitting votes:", error);
    voteError.textContent = "Error submitting votes.";
    voteError.classList.remove("hidden");
  }
}

async function updateTallyDisplay() {
  const tallyResults = document.getElementById("tallyResults");
  const tallyContainer = document.getElementById("tallyContainer");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=unlock_admin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: document.getElementById("adminPin").value })
    });
    const adminResult = await response.json();
    if (!adminResult.success || adminResult.voting_open) {
      tallyResults.classList.add("hidden");
      return;
    }
    tallyResults.classList.remove("hidden");
    const tallyResponse = await fetch(`${API_ENDPOINT}?action=get_tally`);
    const tally = await tallyResponse.json();
    tallyContainer.innerHTML = tally.map(t => `
      <div>
        <h4 class="font-semibold">${t.position.replace(/_/g, ' ')}</h4>
        <ul class="list-disc ml-6">
          ${t.votes.map(v => `<li>${v.candidate_name}: ${v.count} votes</li>`).join("")}
        </ul>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error updating tally:", error);
    tallyResults.classList.add("hidden");
  }
}

async function computeResults() {
  const resultsTable = document.getElementById("resultsTable");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_results`);
    const results = await response.json();
    resultsTable.innerHTML = results.map(r => `
      <div class="mb-4">
        <h3 class="text-lg font-semibold">${r.position.replace(/_/g, ' ')}</h3>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-gray-100">
              <th class="border p-2 text-left">Candidate</th>
              <th class="border p-2 text-right">Student Votes</th>
              <th class="border p-2 text-right">Academics</th>
              <th class="border p-2 text-right">Discipline</th>
              <th class="border p-2 text-right">Clubs</th>
              <th class="border p-2 text-right">Comm. Service</th>
              <th class="border p-2 text-right">Teacher</th>
              <th class="border p-2 text-right">Leadership</th>
              <th class="border p-2 text-right">Public Speaking</th>
              <th class="border p-2 text-right">Final Score</th>
            </tr>
          </thead>
          <tbody>
            ${r.results.map(c => `
              <tr>
                <td class="border p-2">${c.candidate}</td>
                <td class="border p-2 text-right">${c.student_votes}</td>
                <td class="border p-2 text-right">${c.academics}</td>
                <td class="border p-2 text-right">${c.discipline}</td>
                <td class="border p-2 text-right">${c.clubs}</td>
                <td class="border p-2 text-right">${c.community_service}</td>
                <td class="border p-2 text-right">${c.teacher}</td>
                <td class="border p-2 text-right">${c.leadership}</td>
                <td class="border p-2 text-right">${c.public_speaking}</td>
                <td class="border p-2 text-right">${c.final_score}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error computing results:", error);
    resultsTable.innerHTML = "<p class='text-red-500'>Error loading results.</p>";
  }
}

async function exportResults() {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=export_results`);
    const data = await response.json();
    if (!data.success) {
      alert("Error exporting results: " + data.message);
      return;
    }
    let csvContent = "Position,Candidate,Student Votes (%),Academics,Discipline,Clubs,Community Service,Teacher,Leadership,Public Speaking,Final Score\n";
    for (const [position, results] of Object.entries(data.results)) {
      results.forEach(r => {
        csvContent += `"${position.replace(/_/g, ' ')}","${r.Candidate}","${r['Student Votes (%)']}","${r.Academics}","${r.Discipline}","${r.Clubs}","${r['Community Service']}","${r.Teacher}","${r.Leadership}","${r['Public Speaking']}","${r['Final Score']}"\n`;
      });
    }
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "election_results.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error exporting results:", error);
    alert("Error exporting results.");
  }
}

async function loginTeacher() {
  const username = document.getElementById("teacherUsername").value.trim();
  const password = document.getElementById("teacherPassword").value;
  const teacherLoginError = document.getElementById("teacherLoginError");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=login_teacher`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("teacherForm").classList.remove("hidden");
      document.getElementById("teacherChangePassword").classList.remove("hidden");
      document.getElementById("teacherResetPassword").classList.remove("hidden");
      document.getElementById("teacherStudentManagement").classList.remove("hidden");
      await updateTeacherMetricsTable(result.teacher);
      teacherLoginError.classList.add("hidden");
    } else {
      teacherLoginError.textContent = result.message;
      teacherLoginError.classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error logging in teacher:", error);
    teacherLoginError.textContent = "Error logging in teacher.";
    teacherLoginError.classList.remove("hidden");
  }
}

async function updateTeacherMetricsTable(teacher) {
  const tableBody = document.getElementById("teacherMetricsTable");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_class_students&grade=${teacher.grade}&class=${encodeURIComponent(teacher.class)}`);
    const students = await response.json();
    tableBody.innerHTML = students.map(s => {
      const m = s.metrics || {};
      return `
        <tr>
          <td class="border p-2"><span title="ID: ${s.id}">${s.name}</span></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_academics" value="${m.academics || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_discipline" value="${m.discipline || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_clubs" value="${m.clubs || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_communityService" value="${m.community_service || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_teacher" value="${m.teacher || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_leadership" value="${m.leadership || ''}"></td>
          <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.name}_publicSpeaking" value="${m.public_speaking || ''}"></td>
        </tr>
      `;
    }).join("");
  } catch (error) {
    console.error("Error fetching class students:", error);
  }
}

async function saveTeacherMetrics() {
  const username = document.getElementById("teacherUsername").value.trim();
  try {
    const teacherResponse = await fetch(`${API_ENDPOINT}?action=get_teacher&username=${encodeURIComponent(username)}`);
    const teacher = await teacherResponse.json();
    if (!teacher.success) {
      document.getElementById("teacherSaveError").textContent = teacher.message;
      document.getElementById("teacherSaveError").classList.remove("hidden");
      return;
    }
    const studentsResponse = await fetch(`${API_ENDPOINT}?action=get_class_students&grade=${teacher.teacher.grade}&class=${encodeURIComponent(teacher.teacher.class)}`);
    const students = await studentsResponse.json();
    let hasInvalid = false;
    const metricsData = students.map(s => {
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
        }
        return { student_name: s.name, academics, discipline, clubs, community_service: communityService, teacher: teacherScore, leadership, public_speaking: publicSpeaking };
      }
      return null;
    }).filter(m => m);
    if (hasInvalid) {
      document.getElementById("teacherSaveError").classList.remove("hidden");
      return;
    }
    const response = await fetch(`${API_ENDPOINT}?action=save_metrics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ metrics: metricsData })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("teacherSaveError").classList.add("hidden");
      document.getElementById("teacherSaveStatus").classList.remove("hidden");
      setTimeout(() => document.getElementById("teacherSaveStatus").classList.add("hidden"), 2000);
      await computeResults();
    } else {
      document.getElementById("teacherSaveError").textContent = result.message;
      document.getElementById("teacherSaveError").classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error saving metrics:", error);
    document.getElementById("teacherSaveError").textContent = "Error saving metrics.";
    document.getElementById("teacherSaveError").classList.remove("hidden");
  }
}

async function changeTeacherPassword() {
  const username = document.getElementById("teacherUsername").value.trim();
  const oldPassword = document.getElementById("teacherOldPassword").value;
  const newPassword = document.getElementById("teacherNewPassword").value;
  const changeError = document.getElementById("teacherChangeError");
  const changeSuccess = document.getElementById("teacherChangeSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=change_teacher_password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, old_password: oldPassword, new_password: newPassword })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("teacherOldPassword").value = "";
      document.getElementById("teacherNewPassword").value = "";
      changeError.classList.add("hidden");
      changeSuccess.classList.remove("hidden");
      setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
    } else {
      changeError.textContent = result.message;
      changeError.classList.remove("hidden");
      changeSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error changing teacher password:", error);
    changeError.textContent = "Error changing password.";
    changeError.classList.remove("hidden");
    changeSuccess.classList.add("hidden");
  }
}

async function showTeacherSecurityQuestion() {
  const username = document.getElementById("teacherResetUsername").value.trim();
  const resetQuestion = document.getElementById("teacherResetQuestion");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_teacher_security_question&username=${encodeURIComponent(username)}`);
    const result = await response.json();
    resetQuestion.value = result.success && result.security_question ? result.security_question : "";
  } catch (error) {
    console.error("Error fetching teacher security question:", error);
    resetQuestion.value = "";
  }
}

async function resetTeacherPassword() {
  const username = document.getElementById("teacherResetUsername").value.trim();
  const answer = document.getElementById("teacherResetAnswer").value;
  const newPassword = document.getElementById("teacherResetNewPassword").value;
  const resetError = document.getElementById("teacherResetError");
  const resetSuccess = document.getElementById("teacherResetSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=reset_teacher_password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, security_answer: answer, new_password: newPassword })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("teacherResetUsername").value = "";
      document.getElementById("teacherResetAnswer").value = "";
      document.getElementById("teacherResetNewPassword").value = "";
      document.getElementById("teacherResetQuestion").value = "";
      resetError.classList.add("hidden");
      resetSuccess.classList.remove("hidden");
      setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
    } else {
      resetError.textContent = result.message;
      resetError.classList.remove("hidden");
      resetSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error resetting teacher password:", error);
    resetError.textContent = "Error resetting password.";
    resetError.classList.remove("hidden");
    resetSuccess.classList.add("hidden");
  }
}

async function addStudentToClass() {
  const teacherUsername = document.getElementById("teacherUsername").value.trim();
  const studentId = document.getElementById("studentIdManage").value.trim().toUpperCase();
  const studentName = document.getElementById("studentNameManage").value.trim();
  const studentManageError = document.getElementById("studentManageError");
  const studentManageSuccess = document.getElementById("studentManageSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=add_student_to_class`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ teacher_username: teacherUsername, student_id: studentId, student_name: studentName })
    });
    const result = await response.json();
    if (result.success) {
      const teacherResponse = await fetch(`${API_ENDPOINT}?action=get_teacher&username=${encodeURIComponent(teacherUsername)}`);
      const teacher = await teacherResponse.json();
      if (teacher.success) {
        await updateTeacherMetricsTable(teacher.teacher);
      }
      document.getElementById("studentIdManage").value = "";
      document.getElementById("studentNameManage").value = "";
      studentManageError.classList.add("hidden");
      studentManageSuccess.textContent = "Student added successfully!";
      studentManageSuccess.classList.remove("hidden");
      setTimeout(() => studentManageSuccess.classList.add("hidden"), 2000);
    } else {
      studentManageError.textContent = result.message;
      studentManageError.classList.remove("hidden");
      studentManageSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error adding student:", error);
    studentManageError.textContent = "Error adding student.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
  }
}

async function removeStudentFromClass() {
  const teacherUsername = document.getElementById("teacherUsername").value.trim();
  const studentId = document.getElementById("studentIdManage").value.trim().toUpperCase();
  const studentManageError = document.getElementById("studentManageError");
  const studentManageSuccess = document.getElementById("studentManageSuccess");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=remove_student_from_class`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ teacher_username: teacherUsername, student_id: studentId })
    });
    const result = await response.json();
    if (result.success) {
      const teacherResponse = await fetch(`${API_ENDPOINT}?action=get_teacher&username=${encodeURIComponent(teacherUsername)}`);
      const teacher = await teacherResponse.json();
      if (teacher.success) {
        await updateTeacherMetricsTable(teacher.teacher);
      }
      document.getElementById("studentIdManage").value = "";
      document.getElementById("studentNameManage").value = "";
      studentManageError.classList.add("hidden");
      studentManageSuccess.textContent = "Student removed successfully!";
      studentManageSuccess.classList.remove("hidden");
      setTimeout(() => studentManageSuccess.classList.add("hidden"), 2000);
      await computeResults();
    } else {
      studentManageError.textContent = result.message;
      studentManageError.classList.remove("hidden");
      studentManageSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error removing student:", error);
    studentManageError.textContent = "Error removing student.";
    studentManageError.classList.remove("hidden");
    studentManageSuccess.classList.add("hidden");
  }
}

async function clearAllStudents() {
  if (!confirm("Are you sure you want to clear all students? This will remove all student data and cannot be undone.")) {
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=clear_all_students`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const result = await response.json();
    if (result.success) {
      const teacherUsername = document.getElementById("teacherUsername").value.trim();
      const teacherResponse = await fetch(`${API_ENDPOINT}?action=get_teacher&username=${encodeURIComponent(teacherUsername)}`);
      const teacher = await teacherResponse.json();
      if (teacher.success) {
        await updateTeacherMetricsTable(teacher.teacher);
      }
      document.getElementById("studentManageSuccess").textContent = "All students cleared and reset.";
      document.getElementById("studentManageSuccess").classList.remove("hidden");
      setTimeout(() => document.getElementById("studentManageSuccess").classList.add("hidden"), 2000);
      await computeResults();
    } else {
      document.getElementById("studentManageError").textContent = result.message;
      document.getElementById("studentManageError").classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error clearing students:", error);
    document.getElementById("studentManageError").textContent = "Error clearing students.";
    document.getElementById("studentManageError").classList.remove("hidden");
  }
}

async function unlockAdmin() {
  const enteredPin = document.getElementById("adminPin").value;
  try {
    const response = await fetch(`${API_ENDPOINT}?action=unlock_admin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: enteredPin })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("adminForm").classList.remove("hidden");
      document.getElementById("adminPinError").classList.add("hidden");
      document.getElementById("votingToggleBtn").textContent = result.voting_open ? "Close Voting" : "Open Voting";
      document.getElementById("votingStatus").textContent = result.voting_open ? "Voting is open." : "Voting is closed. Tallies are visible.";
      await updateAdminForm();
    } else {
      document.getElementById("adminPinError").textContent = result.message;
      document.getElementById("adminPinError").classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error unlocking admin:", error);
    document.getElementById("adminPinError").textContent = "Error unlocking admin.";
    document.getElementById("adminPinError").classList.remove("hidden");
  }
}

async function updateAdminForm() {
  try {
    const positionsResponse = await fetch(`${API_ENDPOINT}?action=get_all_positions`);
    const positions = await positionsResponse.json();
    const positionList = document.getElementById("positionList");
    positionList.innerHTML = positions.map(p => `
      <div class="flex justify-between items-center p-2 border-b">
        <span>${p.name.replace(/_/g, ' ')}</span>
        <button onclick="removePosition('${p.id}')" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Remove</button>
      </div>
    `).join("");
    const candidatePosition = document.getElementById("candidatePosition");
    candidatePosition.innerHTML = `<option value="">Select a position</option>` +
      positions.map(p => `<option value="${p.id}">${p.name.replace(/_/g, ' ')}</option>`).join("");
    await updateCandidateList();
    const teachersResponse = await fetch(`${API_ENDPOINT}?action=get_all_teachers`);
    const teachers = await teachersResponse.json();
    const teacherList = document.getElementById("teacherList");
    teacherList.innerHTML = teachers.map(t => `
      <div class="flex justify-between items-center p-2 border-b">
        <span>${t.username} (Grade ${t.grade} ${t.class})</span>
        <button onclick="removeTeacher('${t.username}')" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Remove</button>
      </div>
    `).join("");
    const weightsResponse = await fetch(`${API_ENDPOINT}?action=get_weights`);
    const weights = await weightsResponse.json();
    document.getElementById("weightStudentVotes").value = weights.student_votes;
    document.getElementById("weightAcademics").value = weights.academics;
    document.getElementById("weightDiscipline").value = weights.discipline;
    document.getElementById("weightClubs").value = weights.clubs;
    document.getElementById("weightCommunityService").value = weights.community_service;
    document.getElementById("weightTeacher").value = weights.teacher;
    document.getElementById("weightLeadership").value = weights.leadership;
    document.getElementById("weightPublicSpeaking").value = weights.public_speaking;
  } catch (error) {
    console.error("Error updating admin form:", error);
  }
}

async function addPosition() {
  const newPosition = document.getElementById("newPosition").value.trim();
  if (!newPosition) {
    alert("Please enter a position name.");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=add_position`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newPosition, scope: "school" })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("newPosition").value = "";
      await updateAdminForm();
      alert("Position added successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error adding position:", error);
    alert("Error adding position.");
  }
}

async function removePosition(positionId) {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=remove_position`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ position_id: positionId })
    });
    const result = await response.json();
    if (result.success) {
      await updateAdminForm();
      await computeResults();
      alert("Position removed successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error removing position:", error);
    alert("Error removing position.");
  }
}

async function addTeacher() {
  const input = document.getElementById("newTeacher").value.trim();
  const [username, grade, cls, password] = input.split(",");
  if (!username || !grade || !cls || !password) {
    alert("Please enter username, grade, class, and password (e.g., teacher7blue,7,Blue,1234).");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=add_teacher`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, grade: parseInt(grade), class: cls, password })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("newTeacher").value = "";
      await updateAdminForm();
      alert("Teacher added successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error adding teacher:", error);
    alert("Error adding teacher.");
  }
}

async function removeTeacher(username) {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=remove_teacher`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });
    const result = await response.json();
    if (result.success) {
      await updateAdminForm();
      alert("Teacher removed successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error removing teacher:", error);
    alert("Error removing teacher.");
  }
}

async function updateCandidateList() {
  const positionId = document.getElementById("candidatePosition").value;
  const candidateList = document.getElementById("candidateList");
  if (!positionId) {
    candidateList.innerHTML = "";
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_candidates&position_id=${positionId}`);
    const result = await response.json();
    if (result.success) {
      candidateList.innerHTML = result.candidates.length > 0 ? `
        <h5 class="font-semibold">Candidates:</h5>
        <ul class="list-disc ml-6">
          ${result.candidates.map(c => `<li>${c}</li>`).join("")}
        </ul>
      ` : "<p>No candidates for this position.</p>";
    } else {
      candidateList.innerHTML = "<p>Error loading candidates.</p>";
    }
  } catch (error) {
    console.error("Error updating candidate list:", error);
    candidateList.innerHTML = "<p>Error loading candidates.</p>";
  }
}

async function addCandidate() {
  const positionId = document.getElementById("candidatePosition").value;
  const studentId = document.getElementById("candidateId").value.trim().toUpperCase();
  const candidateError = document.getElementById("candidateError");
  const candidateSuccess = document.getElementById("candidateSuccess");
  if (!positionId || !studentId) {
    candidateError.textContent = "Please select a position and enter a student ID.";
    candidateError.classList.remove("hidden");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=add_candidate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ position_id: positionId, student_id: studentId })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("candidateId").value = "";
      candidateError.classList.add("hidden");
      candidateSuccess.textContent = "Candidate added successfully!";
      candidateSuccess.classList.remove("hidden");
      setTimeout(() => candidateSuccess.classList.add("hidden"), 2000);
      await updateCandidateList();
      await computeResults();
    } else {
      candidateError.textContent = result.message;
      candidateError.classList.remove("hidden");
      candidateSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error adding candidate:", error);
    candidateError.textContent = "Error adding candidate.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
  }
}

async function removeCandidate() {
  const positionId = document.getElementById("candidatePosition").value;
  const studentId = document.getElementById("candidateId").value.trim().toUpperCase();
  const candidateError = document.getElementById("candidateError");
  const candidateSuccess = document.getElementById("candidateSuccess");
  if (!positionId || !studentId) {
    candidateError.textContent = "Please select a position and enter a student ID.";
    candidateError.classList.remove("hidden");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=remove_candidate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ position_id: positionId, student_id: studentId })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("candidateId").value = "";
      candidateError.classList.add("hidden");
      candidateSuccess.textContent = "Candidate removed successfully!";
      candidateSuccess.classList.remove("hidden");
      setTimeout(() => candidateSuccess.classList.add("hidden"), 2000);
      await updateCandidateList();
      await computeResults();
    } else {
      candidateError.textContent = result.message;
      candidateError.classList.remove("hidden");
      candidateSuccess.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error removing candidate:", error);
    candidateError.textContent = "Error removing candidate.";
    candidateError.classList.remove("hidden");
    candidateSuccess.classList.add("hidden");
  }
}

async function clearAllCandidates() {
  if (!confirm("Are you sure you want to clear all candidates? This will remove all candidates and votes.")) {
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=clear_all_candidates`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const result = await response.json();
    if (result.success) {
      await updateAdminForm();
      await computeResults();
      alert("All candidates and votes cleared successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error clearing candidates:", error);
    alert("Error clearing candidates.");
  }
}

async function toggleVoting() {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=toggle_voting`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: document.getElementById("adminPin").value })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("votingToggleBtn").textContent = result.voting_open ? "Close Voting" : "Open Voting";
      document.getElementById("votingStatus").textContent = result.voting_open ? "Voting is open." : "Voting is closed. Tallies are visible.";
      await updateTallyDisplay();
      alert(`Voting ${result.voting_open ? "opened" : "closed"} successfully!`);
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error toggling voting:", error);
    alert("Error toggling voting.");
  }
}

async function saveWeights() {
  const weights = {
    student_votes: parseInt(document.getElementById("weightStudentVotes").value),
    academics: parseInt(document.getElementById("weightAcademics").value),
    discipline: parseInt(document.getElementById("weightDiscipline").value),
    clubs: parseInt(document.getElementById("weightClubs").value),
    community_service: parseInt(document.getElementById("weightCommunityService").value),
    teacher: parseInt(document.getElementById("weightTeacher").value),
    leadership: parseInt(document.getElementById("weightLeadership").value),
    public_speaking: parseInt(document.getElementById("weightPublicSpeaking").value)
  };
  const total = Object.values(weights).reduce((sum, w) => sum + (w || 0), 0);
  if (total !== 100) {
    document.getElementById("weightsError").classList.remove("hidden");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=save_weights`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(weights)
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("weightsError").classList.add("hidden");
      await updateWeightsList();
      await computeResults();
      alert("Weights saved successfully!");
    } else {
      document.getElementById("weightsError").textContent = result.message;
      document.getElementById("weightsError").classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error saving weights:", error);
    document.getElementById("weightsError").textContent = "Error saving weights.";
    document.getElementById("weightsError").classList.remove("hidden");
  }
}

async function updateWeightsList() {
  const weightsList = document.getElementById("weightsList");
  try {
    const response = await fetch(`${API_ENDPOINT}?action=get_weights`);
    const weights = await response.json();
    weightsList.innerHTML = `
      <li>Student Votes: ${weights.student_votes}%</li>
      <li>Academics: ${weights.academics}%</li>
      <li>Discipline: ${weights.discipline}%</li>
      <li>Clubs: ${weights.clubs}%</li>
      <li>Community Service: ${weights.community_service}%</li>
      <li>Teacher: ${weights.teacher}%</li>
      <li>Leadership: ${weights.leadership}%</li>
      <li>Public Speaking: ${weights.public_speaking}%</li>
    `;
  } catch (error) {
    console.error("Error updating weights list:", error);
    weightsList.innerHTML = "<li>Error loading weights.</li>";
  }
}

async function updatePin() {
  const newPin = document.getElementById("newPin").value;
  if (!newPin) {
    alert("Please enter a new PIN.");
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=update_pin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ old_pin: document.getElementById("adminPin").value, new_pin: newPin })
    });
    const result = await response.json();
    if (result.success) {
      document.getElementById("adminPin").value = newPin;
      document.getElementById("newPin").value = "";
      alert("PIN updated successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error updating PIN:", error);
    alert("Error updating PIN.");
  }
}

async function exportVotes() {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=export_votes`);
    const data = await response.json();
    if (!data.success) {
      alert("Error exporting votes: " + data.message);
      return;
    }
    let csvContent = "Position,Candidate,Voter Hash\n";
    for (const vote of data.votes) {
      csvContent += `"${vote.position.replace(/_/g, ' ')}","${vote.candidate}","${vote.voter_hash}"\n`;
    }
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "election_votes.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error exporting votes:", error);
    alert("Error exporting votes.");
  }
}

async function downloadBackup() {
  try {
    const response = await fetch(`${API_ENDPOINT}?action=download_backup`);
    const data = await response.json();
    if (!data.success) {
      alert("Error downloading backup: " + data.message);
      return;
    }
    const blob = new Blob([JSON.stringify(data.backup, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "election_backup.json";
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error downloading backup:", error);
    alert("Error downloading backup.");
  }
}

async function importBackup() {
  const fileInput = document.getElementById("importBackup");
  if (!fileInput.files.length) {
    alert("Please select a backup file to import.");
    return;
  }
  const file = fileInput.files[0];
  const reader = new FileReader();
  reader.onload = async function(e) {
    try {
      const backupData = JSON.parse(e.target.result);
      const response = await fetch(`${API_ENDPOINT}?action=import_backup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ backup: backupData })
      });
      const result = await response.json();
      if (result.success) {
        await updateAdminForm();
        await computeResults();
        alert("Backup imported successfully!");
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error("Error importing backup:", error);
      alert("Error importing backup.");
    }
  };
  reader.readAsText(file);
}

async function factoryReset() {
  if (!confirm("Are you sure you want to perform a factory reset? This will wipe all data and cannot be undone.")) {
    return;
  }
  try {
    const response = await fetch(`${API_ENDPOINT}?action=factory_reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: document.getElementById("adminPin").value })
    });
    const result = await response.json();
    if (result.success) {
      await updateAdminForm();
      await computeResults();
      alert("Factory reset completed successfully!");
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error performing factory reset:", error);
    alert("Error performing factory reset.");
  }
}