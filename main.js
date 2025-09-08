// Import the functions you need from the Firebase SDKs
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-analytics.js";
import { getFirestore, doc, setDoc, getDocs, collection, deleteDoc } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-firestore.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBTJf7kM1cYEl6zr0M7qTLaKgZkB0vzflk",
  authDomain: "algocracy-elections.firebaseapp.com",
  projectId: "algocracy-elections",
  storageBucket: "algocracy-elections.firebasestorage.app",
  messagingSenderId: "1078178070639",
  appId: "1:1078178070639:web:df3d4ec409d458c16d0d9a",
  measurementId: "G-MGNXX46FGN"
};

// Initialize Firebase and Firestore
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);

// Data variables will now be fetched from Firestore
let teachers = [];
let students = [];
let positions = [];
let votes = {};
let metrics = {};
let weights = {};
let pin = "";
let votingOpen = true;

const VOTE_ENDPOINT = "";
const classes = {
  7: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta"],
  8: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta"],
  9: ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"]
};

// Helper function to generate students, teachers, etc.
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

function generateTeachers() {
  return [
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
}

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

// Initializing Firestore and migrating data from localStorage
async function initFirestore() {
  try {
    const studentsCol = await getDocs(collection(db, "students"));
    if (studentsCol.empty) {
      console.log("Migrating data from localStorage to Firestore...");
      const studentsToMigrate = generateStudents();
      const teachersToMigrate = generateTeachers();
      const positionsToMigrate = generatePositionsWithCandidates();
      const weightsToMigrate = {
        studentVotes: 30, academics: 15, discipline: 10, clubs: 10, communityService: 5, teacher: 10, leadership: 10, publicSpeaking: 10
      };
      const settingsToMigrate = {
        pin: "1234",
        votingOpen: true
      };

      for (const student of studentsToMigrate) {
        await setDoc(doc(db, "students", student.id), student);
      }
      for (const teacher of teachersToMigrate) {
        await setDoc(doc(db, "teachers", teacher.username), teacher);
      }
      await setDoc(doc(db, "positions", "data"), { positions: positionsToMigrate });
      await setDoc(doc(db, "weights", "data"), weightsToMigrate);
      await setDoc(doc(db, "settings", "data"), settingsToMigrate);
    }
    await fetchData();
  } catch (e) {
    console.error("Error initializing Firestore: ", e);
  }
}

async function fetchData() {
  try {
    students = (await getDocs(collection(db, "students"))).docs.map(doc => doc.data());
    teachers = (await getDocs(collection(db, "teachers"))).docs.map(doc => doc.data());
    const positionsDoc = await getDocs(collection(db, "positions"));
    positions = positionsDoc.docs[0].data().positions;
    const votesDocs = await getDocs(collection(db, "votes"));
    votes = votesDocs.docs.reduce((acc, doc) => {
      acc[doc.id] = doc.data();
      return acc;
    }, {});
    const metricsDocs = await getDocs(collection(db, "metrics"));
    metrics = metricsDocs.docs.reduce((acc, doc) => {
      acc[doc.id] = doc.data();
      return acc;
    }, {});
    const weightsDoc = await getDocs(collection(db, "weights"));
    weights = weightsDoc.docs[0].data();
    const settingsDoc = await getDocs(collection(db, "settings"));
    const settings = settingsDoc.docs[0].data();
    pin = settings.pin;
    votingOpen = settings.votingOpen;

    showTab("register");
  } catch (e) {
    console.error("Error fetching data from Firestore: ", e);
  }
}

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

async function registerStudent() {
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

  try {
    await setDoc(doc(db, "students", id), { ...student, password, securityQuestion: question, securityAnswer: answer });
    document.getElementById("registerId").value = "";
    document.getElementById("registerPassword").value = "";
    document.getElementById("registerName").value = "";
    document.getElementById("securityQuestion").value = "";
    document.getElementById("securityAnswer").value = "";
    registerError.classList.add("hidden");
    registerSuccess.classList.remove("hidden");
    setTimeout(() => registerSuccess.classList.add("hidden"), 2000);
    await fetchData();
  } catch (e) {
    registerError.textContent = "Error during registration: " + e.message;
    registerError.classList.remove("hidden");
  }
}

async function changePassword() {
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

  try {
    await setDoc(doc(db, "students", id), { ...student, password: newPassword });
    document.getElementById("changeId").value = "";
    document.getElementById("oldPassword").value = "";
    document.getElementById("newPassword").value = "";
    changeError.classList.add("hidden");
    changeSuccess.classList.remove("hidden");
    setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
    await fetchData();
  } catch (e) {
    changeError.textContent = "Error changing password: " + e.message;
    changeError.classList.remove("hidden");
  }
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

async function resetPassword() {
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

  try {
    await setDoc(doc(db, "students", id), { ...student, password: newPassword });
    document.getElementById("resetId").value = "";
    document.getElementById("resetAnswer").value = "";
    document.getElementById("resetNewPassword").value = "";
    document.getElementById("resetQuestion").value = "";
    resetError.classList.add("hidden");
    resetSuccess.classList.remove("hidden");
    setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
    await fetchData();
  } catch (e) {
    resetError.textContent = "Error resetting password: " + e.message;
    resetError.classList.remove("hidden");
  }
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

  votePositions.innerHTML = relevantPositions.map(p => {
    const hasVoted = localStorage.getItem(`vote_${btoa(voter.id)}_${p.name}`); // Check localStorage for old votes
    const disabled = hasVoted ? "disabled" : "";
    const options = p.candidates.filter(c => c !== voter.name).map(c =>
      `<option value="${c}">${c}</option>`
    ).join("");
    return `
      <div class="mb-4 flex items-center">
        <label class="w-1/3 text-gray-700 font-semibold">${p.name.replace(/_/g, ' ')}</label>
        <select id="voteCandidate_${p.name}" class="w-2/3 p-2 border rounded" ${disabled}>
          <option value="">Select a candidate</option>
          ${options}
        </select>
      </div>
    `;
  }).join("");
}

async function submitVote() {
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

  let votesSubmitted = 0;
  let hasError = false;

  const promises = relevantPositions.map(async p => {
    const candidate = document.getElementById(`voteCandidate_${p.name}`).value;
    if (candidate) {
      if (p.name.includes("Girl_Representative") && students.find(s => s.name === candidate)?.gender !== "F") {
        voteError.textContent = `Only female candidates can be selected for ${p.name.replace(/_/g, ' ')}.`;
        voteError.classList.remove("hidden");
        hasError = true;
        return;
      }

      const voteRef = doc(db, "votes", p.name);
      const voteData = (await getDocs(collection(db, "votes"))).docs.find(d => d.id === p.name)?.data() || {};
      if (voteData[voterId]) {
        voteError.textContent = `You have already voted for ${p.name.replace(/_/g, ' ')}.`;
        voteError.classList.remove("hidden");
        hasError = true;
        return;
      }

      await setDoc(voteRef, {
        ...voteData,
        [voterId]: { candidate, timestamp: new Date() }
      });
      votesSubmitted++;
    }
  });

  await Promise.all(promises);

  if (hasError) return;

  if (votesSubmitted === 0) {
    voteError.textContent = "Please select at least one candidate.";
    voteError.classList.remove("hidden");
    return;
  }

  await fetchData(); // Refresh data after submitting votes
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

async function loginTeacher() {
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
    const m = metrics[s.id] || {};
    return `
      <tr>
        <td class="border p-2"><span title="ID: ${s.id}">${s.name}</span></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_academics" value="${m.academics || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_discipline" value="${m.discipline || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_clubs" value="${m.clubs || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_communityService" value="${m.communityService || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_teacher" value="${m.teacher || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_leadership" value="${m.leadership || ''}"></td>
        <td class="border p-2"><input type="number" min="0" max="100" class="w-full p-1 border rounded" id="metric_${s.id}_publicSpeaking" value="${m.publicSpeaking || ''}"></td>
      </tr>
    `;
  }).join("");
}

async function saveTeacherMetrics() {
  const tableBody = document.getElementById("teacherMetricsTable");
  const teacher = teachers.find(t => t.username === document.getElementById("teacherUsername").value.trim());
  const classStudents = students.filter(s => s.grade === teacher.grade && s.class === teacher.class);
  let hasInvalid = false;

  const updates = {};
  classStudents.forEach(s => {
    const academics = parseInt(document.getElementById(`metric_${s.id}_academics`).value);
    const discipline = parseInt(document.getElementById(`metric_${s.id}_discipline`).value);
    const clubs = parseInt(document.getElementById(`metric_${s.id}_clubs`).value);
    const communityService = parseInt(document.getElementById(`metric_${s.id}_communityService`).value);
    const teacherScore = parseInt(document.getElementById(`metric_${s.id}_teacher`).value);
    const leadership = parseInt(document.getElementById(`metric_${s.id}_leadership`).value);
    const publicSpeaking = parseInt(document.getElementById(`metric_${s.id}_publicSpeaking`).value);

    if (!isNaN(academics) || !isNaN(discipline) || !isNaN(clubs) || !isNaN(communityService) || !isNaN(teacherScore) || !isNaN(leadership) || !isNaN(publicSpeaking)) {
      if (isNaN(academics) || isNaN(discipline) || isNaN(clubs) || isNaN(communityService) || isNaN(teacherScore) || isNaN(leadership) || isNaN(publicSpeaking) ||
          academics < 0 || academics > 100 || discipline < 0 || discipline > 100 || clubs < 0 || clubs > 100 || communityService < 0 || communityService > 100 || teacherScore < 0 || teacherScore > 100 || leadership < 0 || leadership > 100 || publicSpeaking < 0 || publicSpeaking > 100) {
        hasInvalid = true;
        return;
      }
      updates[s.id] = { academics, discipline, clubs, communityService, teacher: teacherScore, leadership, publicSpeaking };
    }
  });

  if (hasInvalid) {
    document.getElementById("teacherSaveError").classList.remove("hidden");
    return;
  }

  try {
    for (const id in updates) {
      await setDoc(doc(db, "metrics", id), updates[id]);
    }
    await fetchData();
    document.getElementById("teacherSaveError").classList.add("hidden");
    document.getElementById("teacherSaveStatus").classList.remove("hidden");
    setTimeout(() => document.getElementById("teacherSaveStatus").classList.add("hidden"), 2000);
    computeResults();
  } catch (e) {
    document.getElementById("teacherSaveError").textContent = "Error saving metrics: " + e.message;
    document.getElementById("teacherSaveError").classList.remove("hidden");
  }
}

async function changeTeacherPassword() {
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

  try {
    await setDoc(doc(db, "teachers", username), { ...teacher, password: newPassword });
    document.getElementById("teacherOldPassword").value = "";
    document.getElementById("teacherNewPassword").value = "";
    changeError.classList.add("hidden");
    changeSuccess.classList.remove("hidden");
    setTimeout(() => changeSuccess.classList.add("hidden"), 2000);
    await fetchData();
  } catch (e) {
    changeError.textContent = "Error changing password: " + e.message;
    changeError.classList.remove("hidden");
  }
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

async function resetTeacherPassword() {
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

  try {
    await setDoc(doc(db, "teachers", username), { ...teacher, password: newPassword });
    document.getElementById("teacherResetUsername").value = "";
    document.getElementById("teacherResetAnswer").value = "";
    document.getElementById("teacherResetNewPassword").value = "";
    document.getElementById("teacherResetQuestion").value = "";
    resetError.classList.add("hidden");
    resetSuccess.classList.remove("hidden");
    setTimeout(() => resetSuccess.classList.add("hidden"), 2000);
    await fetchData();
  } catch (e) {
    resetError.textContent = "Error resetting password: " + e.message;
    resetError.classList.remove("hidden");
  }
}

async function addStudentToClass() {
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

  const newStudent = { name: studentName, id: studentId, password: "1234", grade: teacher.grade, class: teacher.class, gender: "U", securityQuestion: "", securityAnswer: "" };

  try {
    await setDoc(doc(db, "students", newStudent.id), newStudent);
    await fetchData();
    updateTeacherMetricsTable(teacher);
    document.getElementById("studentIdManage").value = "";
    document.getElementById("studentNameManage").value = "";
    studentManageError.classList.add("hidden");
    studentManageSuccess.textContent = "Student added successfully!";
    studentManageSuccess.classList.remove("hidden");
    setTimeout(() => studentManageSuccess.classList.add("hidden"), 2000);
  } catch (e) {
    studentManageError.textContent = "Error adding student: " + e.message;
    studentManageError.classList.remove("hidden");
  }
}

function updateAdminForm() {
  document.getElementById("pin").value = pin;
  document.getElementById("votingOpen").checked = votingOpen;
  document.getElementById("weights-list").innerHTML = Object.entries(weights).map(([key, value]) => `
    <div class="mb-2">
      <label class="block text-gray-700 font-semibold">${key}</label>
      <input type="number" id="weight_${key}" class="w-full p-2 border rounded" value="${value}" min="0" max="100">
    </div>
  `).join("");
}

async function updateAdminSettings() {
  const newPin = document.getElementById("pin").value;
  const newVotingOpen = document.getElementById("votingOpen").checked;
  const newWeights = {};
  let totalWeight = 0;

  Object.keys(weights).forEach(key => {
    const value = parseInt(document.getElementById(`weight_${key}`).value);
    newWeights[key] = value;
    totalWeight += value;
  });

  if (totalWeight !== 100) {
    document.getElementById("adminError").textContent = "Total weights must equal 100%. Current total: " + totalWeight;
    document.getElementById("adminError").classList.remove("hidden");
    return;
  }

  try {
    await setDoc(doc(db, "weights", "data"), newWeights);
    await setDoc(doc(db, "settings", "data"), { pin: newPin, votingOpen: newVotingOpen });
    await fetchData();
    document.getElementById("adminError").classList.add("hidden");
    document.getElementById("adminSuccess").classList.remove("hidden");
    setTimeout(() => document.getElementById("adminSuccess").classList.add("hidden"), 2000);
    computeResults();
  } catch (e) {
    document.getElementById("adminError").textContent = "Error updating settings: " + e.message;
    document.getElementById("adminError").classList.remove("hidden");
  }
}

function updateTallyDisplay() {
  const tallyContainer = document.getElementById("tallyContainer");
  const tallyResults = document.getElementById("tallyResults");
  if (Object.keys(votes).length > 0) {
    tallyResults.classList.remove("hidden");
    tallyContainer.innerHTML = Object.entries(votes).map(([position, voteCounts]) => `
      <div>
        <h4 class="font-semibold">${position.replace(/_/g, ' ')}</h4>
        <ul class="list-disc ml-4">
          ${Object.entries(voteCounts).map(([candidate, count]) =>
            `<li>${candidate}: ${Object.keys(count).length} votes</li>`
          ).join("")}
        </ul>
      </div>
    `).join("");
  } else {
    tallyResults.classList.add("hidden");
  }
}

function computeResults() {
  const resultsTable = document.getElementById("resultsTable");
  const finalScores = {};
  const totalVotes = {};

  // Calculate total votes per position
  Object.entries(votes).forEach(([position, positionVotes]) => {
    totalVotes[position] = Object.keys(positionVotes).length;
  });

  // Calculate final score for each candidate
  positions.forEach(p => {
    p.candidates.forEach(candidateName => {
      const candidateId = students.find(s => s.name === candidateName)?.id;
      if (!finalScores[p.name]) finalScores[p.name] = {};
      
      const candidateMetrics = metrics[candidateId] || {};
      const voteCount = votes[p.name] ? Object.keys(votes[p.name]).filter(voterId => votes[p.name][voterId].candidate === candidateName).length : 0;
      const studentVotesPercentage = totalVotes[p.name] ? (voteCount / totalVotes[p.name]) * 100 : 0;

      const academics = candidateMetrics.academics || 0;
      const discipline = candidateMetrics.discipline || 0;
      const clubs = candidateMetrics.clubs || 0;
      const communityService = candidateMetrics.communityService || 0;
      const teacher = candidateMetrics.teacher || 0;
      const leadership = candidateMetrics.leadership || 0;
      const publicSpeaking = candidateMetrics.publicSpeaking || 0;

      const finalScore = (studentVotesPercentage * weights.studentVotes / 100) +
                         (academics * weights.academics / 100) +
                         (discipline * weights.discipline / 100) +
                         (clubs * weights.clubs / 100) +
                         (communityService * weights.communityService / 100) +
                         (teacher * weights.teacher / 100) +
                         (leadership * weights.leadership / 100) +
                         (publicSpeaking * weights.publicSpeaking / 100);

      finalScores[p.name][candidateName] = {
        finalScore: finalScore.toFixed(2),
        academics,
        discipline,
        clubs,
        communityService,
        teacher,
        leadership,
        publicSpeaking,
        studentVotesPercentage: studentVotesPercentage.toFixed(2),
      };
    });
  });

  // Sort candidates by final score and create the results table
  let tableHTML = "";
  Object.entries(finalScores).forEach(([position, candidates]) => {
    const sortedCandidates = Object.entries(candidates).sort((a, b) => b[1].finalScore - a[1].finalScore);
    tableHTML += `
      <div class="mb-4">
        <h3 class="text-xl font-semibold mb-2">${position.replace(/_/g, ' ')}</h3>
        <table class="min-w-full bg-white border">
          <thead>
            <tr>
              <th class="py-2 px-4 border-b">Candidate</th>
              <th class="py-2 px-4 border-b">Final Score</th>
              <th class="py-2 px-4 border-b">Student Votes %</th>
              <th class="py-2 px-4 border-b">Academics</th>
              <th class="py-2 px-4 border-b">Discipline</th>
              <th class="py-2 px-4 border-b">Clubs</th>
              <th class="py-2 px-4 border-b">Community Service</th>
              <th class="py-2 px-4 border-b">Teacher</th>
              <th class="py-2 px-4 border-b">Leadership</th>
              <th class="py-2 px-4 border-b">Public Speaking</th>
            </tr>
          </thead>
          <tbody>
            ${sortedCandidates.map(([name, scores]) => `
              <tr>
                <td class="py-2 px-4 border-b">${name}</td>
                <td class="py-2 px-4 border-b">${scores.finalScore}</td>
                <td class="py-2 px-4 border-b">${scores.studentVotesPercentage}</td>
                <td class="py-2 px-4 border-b">${scores.academics}</td>
                <td class="py-2 px-4 border-b">${scores.discipline}</td>
                <td class="py-2 px-4 border-b">${scores.clubs}</td>
                <td class="py-2 px-4 border-b">${scores.communityService}</td>
                <td class="py-2 px-4 border-b">${scores.teacher}</td>
                <td class="py-2 px-4 border-b">${scores.leadership}</td>
                <td class="py-2 px-4 border-b">${scores.publicSpeaking}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  });
  resultsTable.innerHTML = tableHTML;
}

function exportResults() {
  let csv = "Position,Candidate,Final Score,Student Votes %,Academics,Discipline,Clubs,Community Service,Teacher,Leadership,Public Speaking\n";

  Object.entries(finalScores).forEach(([position, candidates]) => {
    const sortedCandidates = Object.entries(candidates).sort((a, b) => b[1].finalScore - a[1].finalScore);
    sortedCandidates.forEach(([name, scores]) => {
      csv += `${position.replace(/_/g, ' ')},${name},${scores.finalScore},${scores.studentVotesPercentage},${scores.academics},${scores.discipline},${scores.clubs},${scores.communityService},${scores.teacher},${scores.leadership},${scores.publicSpeaking}\n`;
    });
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "election_results.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

async function exportVotes() {
  try {
    const votesDocs = await getDocs(collection(db, "votes"));
    const votesData = votesDocs.docs.map(doc => doc.data());
    const dataStr = JSON.stringify(votesData, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "votes.json";
    link.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert("Error exporting votes: " + e.message);
  }
}

async function downloadBackup() {
  try {
    const studentsData = (await getDocs(collection(db, "students"))).docs.map(doc => doc.data());
    const teachersData = (await getDocs(collection(db, "teachers"))).docs.map(doc => doc.data());
    const positionsData = (await getDocs(collection(db, "positions"))).docs[0].data().positions;
    const votesData = (await getDocs(collection(db, "votes"))).docs.reduce((acc, doc) => { acc[doc.id] = doc.data(); return acc; }, {});
    const metricsData = (await getDocs(collection(db, "metrics"))).docs.reduce((acc, doc) => { acc[doc.id] = doc.data(); return acc; }, {});
    const weightsData = (await getDocs(collection(db, "weights"))).docs[0].data();
    const settingsData = (await getDocs(collection(db, "settings"))).docs[0].data();

    const backupData = {
      students: studentsData,
      teachers: teachersData,
      positions: positionsData,
      votes: votesData,
      metrics: metricsData,
      weights: weightsData,
      settings: settingsData
    };

    const dataStr = JSON.stringify(backupData, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "algocracy_backup.json";
    link.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert("Error creating backup: " + e.message);
  }
}

async function importBackup() {
  const fileInput = document.getElementById("importBackup");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file to import.");
    return;
  }
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const backupData = JSON.parse(e.target.result);
      
      const collectionsToClear = ["students", "teachers", "positions", "votes", "metrics", "weights", "settings"];
      for (const col of collectionsToClear) {
        const docs = await getDocs(collection(db, col));
        for (const d of docs.docs) {
          await deleteDoc(doc(db, col, d.id));
        }
      }

      for (const student of backupData.students) {
        await setDoc(doc(db, "students", student.id), student);
      }
      for (const teacher of backupData.teachers) {
        await setDoc(doc(db, "teachers", teacher.username), teacher);
      }
      await setDoc(doc(db, "positions", "data"), { positions: backupData.positions });
      for (const position in backupData.votes) {
        await setDoc(doc(db, "votes", position), backupData.votes[position]);
      }
      for (const metricId in backupData.metrics) {
        await setDoc(doc(db, "metrics", metricId), backupData.metrics[metricId]);
      }
      await setDoc(doc(db, "weights", "data"), backupData.weights);
      await setDoc(doc(db, "settings", "data"), backupData.settings);

      alert("Backup imported successfully! The app will now reload.");
      location.reload();
    } catch (error) {
      alert("Error importing backup: " + error.message);
    }
  };
  reader.readAsText(file);
}


// Start the application
initFirestore();