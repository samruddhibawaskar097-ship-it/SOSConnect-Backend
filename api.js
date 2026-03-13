
const BASE_URL = "https://sos-connect.onrender.com";

let currentUID = localStorage.getItem("uid") || null;

function setUID(uid) {
  currentUID = uid;
  localStorage.setItem("uid", uid);
}

function getUID() {
  return currentUID;
}

async function registerUser(uid, name, email, phone) {
  const res = await fetch(`${BASE_URL}/api/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid, name, email, phone })
  });
  return res.json();
}

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

async function triggerSOS(latitude, longitude) {
  const res = await fetch(`${BASE_URL}/api/alerts/sos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID(), latitude, longitude })
  });
  return res.json();
}

async function getFirstAid(keyword) {
  const res = await fetch(`${BASE_URL}/api/alerts/firstaid`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword })
  });
  return res.json();
}

async function getTravelerInfo(countryCode, countryName) {
  const res = await fetch(`${BASE_URL}/api/alerts/traveler/info`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid: getUID(), country_code: countryCode, country_name: countryName })
  });
  return res.json();
}

async function getNearbyAll(latitude, longitude) {
  const res = await fetch(`${BASE_URL}/api/navigation/nearby/all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitude, longitude })
  });
  return res.json();
}

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