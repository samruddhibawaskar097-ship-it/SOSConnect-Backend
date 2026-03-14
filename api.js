// api.js — SOSConnect Backend API
const BASE_URL = "https://sos-connect.onrender.com/api";

// ── USER UID ──────────────────────────────────────
let currentUID = localStorage.getItem("uid") || "user001";

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

async function addContactAPI(name, phone) {
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
    body: JSON.stringify({
      uid: getUID(),
      latitude,
      longitude,
      type: "manual",
      message: "SOS triggered from app!"
    })
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

// ── DEAD MAN'S SWITCH ─────────────────────────────
async function startCheckinAPI(intervalMinutes = 30) {
  const res = await fetch(`${BASE_URL}/api/alerts/checkin/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID(), interval_minutes: intervalMinutes })
  });
  return res.json();
}

async function respondCheckin() {
  const res = await fetch(`${BASE_URL}/api/alerts/checkin/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID() })
  });
  return res.json();
}

async function verifyOTP(){
  const name = localStorage.getItem("userName");
  const phone = localStorage.getItem("userPhone");
  const uid = "user_" + phone.replace(/\D/g,"");
  setUID(uid);
  try { await registerUser(uid, name, uid+"@sosconnect.app", phone); } catch(e){}
  window.location.href = "dashboard.html";
}