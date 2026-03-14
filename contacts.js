// contacts.js — connected to SOSConnect backend

async function loadContacts() {
  const list = document.getElementById("contactList");
  list.innerHTML = "<p style='color:white;'>Loading...</p>";

  try {
    const data = await getContacts();
    list.innerHTML = "";

    if (!data.contacts || data.contacts.length === 0) {
      list.innerHTML = "<p style='color:white;opacity:0.7;'>No contacts added yet.</p>";
      return;
    }

    data.contacts.forEach(c => {
      list.innerHTML += `
        <div class="contact">
          <div class="contact-info">
            <strong>${c.name}</strong>
            <span>${c.phone}</span>
          </div>
          <div class="actions">
            <a href="tel:${c.phone}">
              <button class="call"><i class="fa fa-phone"></i></button>
            </a>
            <button class="delete" onclick="removeContact('${c.phone}')">
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>`;
    });
  } catch (e) {
    list.innerHTML = "<p style='color:red;'>Error loading contacts.</p>";
  }
}

async function addContact() {
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();

  if (!name || !phone) {
    alert("Please enter name and phone number.");
    return;
  }

  // Add country code if missing
  const formattedPhone = phone.startsWith("+") ? phone : "+91" + phone;

  try {
    const result = await addContactAPI(name, formattedPhone);
    if (result.message) {
      document.getElementById("name").value = "";
      document.getElementById("phone").value = "";
      loadContacts();
    } else {
      alert("Error: " + (result.error || "Could not add contact"));
    }
  } catch (e) {
    alert("Error adding contact: " + e.message);
  }
}

async function removeContact(phone) {
  if (!confirm("Remove this contact?")) return;
  try {
    await deleteContact(phone);
    loadContacts();
  } catch (e) {
    alert("Error removing contact.");
  }
}

// Load contacts when page opens
loadContacts();
