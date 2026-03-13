function loadContacts(){

let contacts = JSON.parse(localStorage.getItem("contacts")) || [];

let list = document.getElementById("contactList");

list.innerHTML="";

contacts.forEach((c,index)=>{

list.innerHTML+=`

<div class="contact">

<div class="contact-info">

<strong>${c.name}</strong>

<span>${c.phone}</span>

</div>

<div class="actions">

<a href="tel:${c.phone}">
<button class="call"><i class="fa fa-phone"></i></button>
</a>

<button class="delete" onclick="deleteContact(${index})">
<i class="fa fa-trash"></i>
</button>

</div>

</div>

`;

});

}

function addContact(){

let name=document.getElementById("name").value;

let phone=document.getElementById("phone").value;

if(name=="" || phone==""){

alert("Enter name and phone");

return;

}

let contacts = JSON.parse(localStorage.getItem("contacts")) || [];

contacts.push({name,phone});

localStorage.setItem("contacts",JSON.stringify(contacts));

document.getElementById("name").value="";
document.getElementById("phone").value="";

loadContacts();

}

function deleteContact(index){

let contacts = JSON.parse(localStorage.getItem("contacts"));

contacts.splice(index,1);

localStorage.setItem("contacts",JSON.stringify(contacts));

loadContacts();

}

loadContacts();