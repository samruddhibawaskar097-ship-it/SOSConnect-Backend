const BASE_URL = "https://sos-connect.onrender.com/";

// Store logged-in user's UID (set after login)
let currentUID = localStorage.getItem("uid") || null;

function setUID(uid) {
  currentUID = uid;
  localStorage.setItem("uid", uid);
}

function getUID() {
  return currentUID;
}

// ── USER ──────────────────────────────────────────

async function registerUser(uid, name, email, phone) {
  const res = await fetch(`${BASE_URL}/api/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid, name, email, phone })
  });
  return res.json();
}

// ── CONTACTS ──────────────────────────────────────

async function getContacts() {
  const res = await fetch(`${BASE_URL}/api/users/${getUID()}/contacts`);
  return res.json();
}

async function addContact(name, phone) {
  const res = await fetch(`${BASE_URL}/api/users/${getUID()}/contacts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, phone })
  });
  return res.json();
}

async function deleteContact(phone) {
  const res = await fetch(`${BASE_URL}/api/users/${getUID()}/contacts/${phone}`, {
    method: "DELETE"
  });
  return res.json();
}

// ── SOS ───────────────────────────────────────────

async function triggerSOS(latitude, longitude) {
  const res = await fetch(`${BASE_URL}/api/alerts/sos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID(), latitude, longitude })
  });
  return res.json();
}

// ── FIRST AID ─────────────────────────────────────

async function getFirstAid(keyword) {
  const res = await fetch(`${BASE_URL}/api/alerts/firstaid`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword })
  });
  return res.json();
}

// ── TRAVELER SAFETY ───────────────────────────────

async function getTravelerInfo(countryCode, countryName) {
  const res = await fetch(`${BASE_URL}/api/alerts/traveler/info`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID(), country_code: countryCode, country_name: countryName })
  });
  return res.json();
}

// ── NEARBY PLACES ─────────────────────────────────

async function getNearbyAll(latitude, longitude) {
  const res = await fetch(`${BASE_URL}/api/navigation/nearby/all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitude, longitude })
  });
  return res.json();
}

// ── VOICE CODE ────────────────────────────────────

async function saveVoiceCode(phrase) {
  const res = await fetch(`${BASE_URL}/api/users/${getUID()}/distress-phrase`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phrase })
  });
  return res.json();
}

async function matchVoiceCode(spoken) {
  const res = await fetch(`${BASE_URL}/api/users/${getUID()}/distress-phrase/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ spoken })
  });
  return res.json();
}

const sosButton = document.getElementById("sosButton");
const message = document.getElementById("sosMessage");
let timer;

sosButton.addEventListener("click", async function () {
  if (sosButton.classList.contains("deactivated")) return;
  sosButton.classList.add("deactivated");

  // Get location and trigger SOS
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;
    const result = await triggerSOS(lat, lon);
    console.log("SOS triggered:", result);
    alert(`SOS sent! ${result.contacts_notified} contacts notified.`);
  });

  let seconds = 30;
  message.innerText = "Deactivated after " + seconds + "s";
  timer = setInterval(() => {
    seconds--;
    message.innerText = "Deactivated after " + seconds + "s";
    if (seconds <= 0) {
      clearInterval(timer);
      sosButton.classList.remove("deactivated");
      message.innerText = "";
    }
  }, 1000);
});

async function detectCountry() {
  if (!navigator.geolocation) { info.innerHTML = "Location not supported."; return; }

  navigator.geolocation.getCurrentPosition(async (pos) => {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;

    // Reverse geocode to get country code (using free API)
    const geo = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
    const geoData = await geo.json();
    const countryCode = geoData.address.country_code.toUpperCase();
    const countryName = geoData.address.country;

    const data = await getTravelerInfo(countryCode, countryName);
    const e = data.emergency_info;

    info.innerHTML = `
      <b>${e.country}</b><br>
      🚔 Police: ${e.police}<br>
      🚑 Ambulance: ${e.ambulance}<br>
      🔥 Fire: ${e.fire}<br>
      💬 Phrase: <i>${e.emergency_phrase}</i>
    `;
  });
}

detectCountry();

async function askFirstAid() {
  const keyword = document.getElementById("firstAidInput").value;
  const data = await getFirstAid(keyword);
  const result = document.getElementById("firstAidResult");
  if (data.instructions) {
    result.innerHTML = `<b>${data.instructions.title}</b><br>` +
      data.instructions.steps.map((s, i) => `${i+1}. ${s}`).join("<br>");
  } else {
    result.innerHTML = "Not found. Try: cpr, bleeding, burn, choking";
  }
}

async function changePhrase() {
  const phrase = prompt("Enter new voice code phrase:");
  if (phrase) {
    const result = await saveVoiceCode(phrase);
    if (result.message) {
      document.getElementById("voicePhrase").innerText = phrase;
      alert("Voice code saved!");
    }
  }
}
