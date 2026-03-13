// Add <script src="api.js"></script> in contacts.html BEFORE contacts.js

async function loadContacts() {
  const data = await getContacts();
  const list = document.getElementById("contactList");
  list.innerHTML = "";

  (data.contacts || []).forEach(c => {
    list.innerHTML += `
      <div class="contact">
        <div class="contact-info">
          <strong>${c.name}</strong>
          <span>${c.phone}</span>
        </div>
        <div class="actions">
          <a href="tel:${c.phone}"><button class="call"><i class="fa fa-phone"></i></button></a>
          <button class="delete" onclick="removeContact('${c.phone}')">
            <i class="fa fa-trash"></i>
          </button>
        </div>
      </div>`;
  });
}

async function addContact() {
  const name = document.getElementById("name").value;
  const phone = document.getElementById("phone").value;
  if (!name || !phone) { alert("Enter name and phone"); return; }
  await addContact(name, phone);
  document.getElementById("name").value = "";
  document.getElementById("phone").value = "";
  loadContacts();
}

async function removeContact(phone) {
  await deleteContact(phone);
  loadContacts();
}

loadContacts();