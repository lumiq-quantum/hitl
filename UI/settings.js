const API = "http://localhost:8000"; // Update with your API URL

// --- Helper functions ---
function showMsg(msg, type='success') {
  let el = document.getElementById('msg');
  if (!el) {
    el = document.createElement('div');
    el.id = 'msg';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = type;
  setTimeout(() => { el.textContent = ""; }, 3000);
}
function parseJSONSafe(str) {
  try { return JSON.parse(str); } catch { return null; }
}

// Sidebar and panel loader
async function loadSidebarAndPanels() {
  // Load sidebar
  const sidebarRes = await fetch('sidebar.html');
  document.getElementById('sidebar').innerHTML = await sidebarRes.text();
  // Load panels
  const panels = [
    { id: 'channels', file: 'channels.html' },
    { id: 'users', file: 'users.html' },
    { id: 'user-channels', file: 'user_channels.html' }
  ];
  let html = '';
  for (const p of panels) {
    const res = await fetch(p.file);
    html += await res.text();
  }
  document.getElementById('settings-panels').innerHTML = html;
  showPanel('channels');
  console.log("CHECKKKKKK")
  setupChannelConfigValidation();
  // Load data after panels are loaded
  loadChannels();
  loadUsers();
  loadUserChannels();
}

function showPanel(panel) {
  document.querySelectorAll('.settings-panel').forEach(el => {
    el.style.display = 'none';
  });
  const el = document.getElementById('panel-' + panel);
  if (el) el.style.display = '';
  document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
  const link = Array.from(document.querySelectorAll('.sidebar a')).find(a => a.textContent.toLowerCase().includes(panel.replace('-', ' ')));
  if (link) link.classList.add('active');
}

// --- Place all previous JS logic for CRUD and mapping here (from the previous settings.html) ---
// For brevity, you can copy the JS logic for loading, creating, editing, deleting channels, users, user-channels, etc.
// and place it after the panel loader logic above.

// --- Channel config validation ---
const CHANNEL_CONFIG_FIELDS = {
  discord: ["bot_token", "guild_id"],
  gmail: ["client_id", "client_secret", "refresh_token"],
  "google chat": ["service_account_json", "space_id"],
  "microsoft outlook": ["client_id", "client_secret", "tenant_id", "refresh_token"],
  "microsoft teams": ["client_id", "client_secret", "tenant_id", "bot_id", "bot_password"],
  email: ["smtp_server", "smtp_port", "smtp_user", "smtp_password"],
  slack: ["bot_token", "channel_id"],
  telegram: ["bot_token", "chat_id"],
  whatsapp: ["api_key", "phone_number_id"]
};

function renderChannelConfigFields(type, config = {}) {
  const fields = CHANNEL_CONFIG_FIELDS[type] || [];
  const container = document.getElementById('channel-config-fields');
  if (!container) return;
  container.innerHTML = '';
  fields.forEach(field => {
    const label = document.createElement('label');
    label.textContent = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
    const input = document.createElement('input');
    input.type = 'text';
    input.id = `channel-config-${field}`;
    input.name = field;
    input.value = config[field] || '';
    input.required = true;
    container.appendChild(label);
    container.appendChild(input);
  });
}

function setupChannelConfigValidation() {
  const typeSelect = document.getElementById('channel-type');
  const form = document.getElementById('channel-form');
  if (!typeSelect || !form) return;

  typeSelect.addEventListener('change', function() {
    renderChannelConfigFields(typeSelect.value);
  });

  form.addEventListener('submit', function(e) {
    const type = typeSelect.value;
    const fields = CHANNEL_CONFIG_FIELDS[type] || [];
    const config = {};
    let missing = [];
    fields.forEach(field => {
      const val = document.getElementById(`channel-config-${field}`)?.value;
      if (!val) missing.push(field);
      config[field] = val || '';
    });
    if (missing.length) {
      e.preventDefault();
      alert('Missing required config fields: ' + missing.join(', '));
      return false;
    }
    // Set config as JSON string for backend
    form.config = config;
  }, true);
}

// Patch createOrUpdateChannel to use dynamic config fields and support update
async function createOrUpdateChannel(e) {
  e.preventDefault();
  const id = document.getElementById("channel-id").value;
  const name = document.getElementById("channel-name").value;
  const type = document.getElementById("channel-type").value;
  const fields = CHANNEL_CONFIG_FIELDS[type] || [];
  const config = {};
  fields.forEach(field => {
    config[field] = document.getElementById(`channel-config-${field}`)?.value || '';
  });
  const payload = { name, type, config };
  let method = id ? "PUT" : "POST";
  let url = `${API}/channels/` + (id ? id + "/" : "");
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    showMsg("Channel saved!");
    document.getElementById("channel-form").reset();
    renderChannelConfigFields(type); // clear fields
    loadChannels();
  } else {
    showMsg("Error: " + (await res.text()), "error");
  }
}

// Patch editChannel to fill config fields
async function editChannel(id) {
  const res = await fetch(`${API}/channels/${id}`);
  const ch = await res.json();
  document.getElementById("channel-id").value = ch.id;
  document.getElementById("channel-name").value = ch.name;
  document.getElementById("channel-type").value = ch.type;
  renderChannelConfigFields(ch.type, ch.config || {});
}

// Patch createOrUpdateUser to support update
async function createOrUpdateUser(e) {
  e.preventDefault();
  const id = document.getElementById("user-id").value;
  const name = document.getElementById("user-name").value;
  const email = document.getElementById("user-email").value;
  const phone = document.getElementById("user-phone").value;
  const persona = document.getElementById("user-persona").value;
  const payload = { name, email, phone, persona };
  let method = id ? "PUT" : "POST";
  let url = `${API}/users/` + (id ? id + "/" : "");
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    showMsg("User saved!");
    document.getElementById("user-form").reset();
    loadUsers();
  } else {
    showMsg("Error: " + (await res.text()), "error");
  }
}

// Patch editUser to fill user fields
async function editUser(id) {
  const res = await fetch(`${API}/users/${id}`);
  const u = await res.json();
  document.getElementById("user-id").value = u.id;
  document.getElementById("user-name").value = u.name;
  document.getElementById("user-email").value = u.email || "";
  document.getElementById("user-phone").value = u.phone || "";
  document.getElementById("user-persona").value = u.persona || "";
}

// Patch createUserChannel to support update
async function createUserChannel(e) {
  e.preventDefault();
  const user_id = document.getElementById("map-user")?.value;
  const channel_id = document.getElementById("map-channel")?.value;
  const contactDetailsFields = document.querySelectorAll("#contact-details-fields input");
  const contact_details = {};
  contactDetailsFields.forEach(input => {
    contact_details[input.name] = input.value;
  });
  const is_preferred = document.getElementById("map-default")?.checked;

  if (!user_id || !channel_id) {
    alert("User and Channel must be selected.");
    return;
  }

  const payload = { user_id: Number(user_id), channel_id: Number(channel_id), contact_details, is_preferred };
  let method = "POST";
  let url = `${API}/user-channels/`;
  if (e.submitter && e.submitter.dataset.ucid) {
    method = "PUT";
    url = `${API}/user-channels/${e.submitter.dataset.ucid}`;
  }
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    showMsg("User mapped to channel!");
    loadUserChannels();
  } else if (res.status === 400) {
    const error = await res.json();
    alert(error.detail || "Validation error occurred.");
  } else {
    showMsg("Error: " + (await res.text()), "error");
  }
}

// Patch editUserChannel to fill mapping fields
async function editUserChannel(id) {
  const res = await fetch(`${API}/user-channels/${id}`);
  const uc = await res.json();
  document.getElementById("map-user").value = uc.user_id;
  document.getElementById("map-channel").value = uc.channel_id;
  document.getElementById("map-contact").value = JSON.stringify(uc.contact_details || {});
  document.getElementById("map-default").checked = !!uc.is_preferred;
  // Set update mode
  document.querySelector("#user-channel-form button[type='submit']").dataset.ucid = id;
}

// --- Load Channels ---
async function loadChannels() {
  const res = await fetch(`${API}/channels/`);
  const data = await res.json();
  const tbody = document.querySelector("#channels-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  data.forEach(ch => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${ch.name}</td>
      <td>${ch.type}</td>
      <td><pre>${JSON.stringify(ch.config, null, 1)}</pre></td>
      <td class="actions">
        <button onclick="editChannel(${ch.id})">Edit</button>
        <button class="danger" onclick="deleteChannel(${ch.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
  // For mapping
  const sel = document.getElementById("map-channel");
  if (sel) sel.innerHTML = '<option value="">Select</option>' + data.map(ch => `<option value="${ch.id}" data-type="${ch.type}">${ch.name} (${ch.type})</option>`).join('');
}

// --- Load Users ---
async function loadUsers() {
  const res = await fetch(`${API}/users/`);
  const data = await res.json();
  const tbody = document.querySelector("#users-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  data.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.name}</td>
      <td>${u.email || ""}</td>
      <td>${u.phone || ""}</td>
      <td>${u.persona || ""}</td>
      <td class="actions">
        <button onclick="editUser(${u.id})">Edit</button>
        <button class="danger" onclick="deleteUser(${u.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
  // For mapping
  const sel = document.getElementById("map-user");
  if (sel) sel.innerHTML = '<option value="">Select</option>' + data.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
}

// --- Load User Channels ---
async function loadUserChannels() {
  const res = await fetch(`${API}/user-channels/`);
  const data = await res.json();
  const tbody = document.querySelector("#user-channels-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  data.forEach(uc => {
    const def = uc.is_preferred ? '<span class="default">Yes</span>' : '';
    const contact = JSON.stringify(uc.contact_details || {});
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${uc.user_id}</td>
      <td>${uc.channel_id}</td>
      <td><pre>${contact}</pre></td>
      <td>${def}</td>
      <td class="actions">
        <button onclick="editUserChannel(${uc.id})">Edit</button>
        <button onclick="deleteUserChannel(${uc.id})">Delink</button>
        <button onclick="setDefaultUserChannel(${uc.id})">Set Default</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// --- Delete User ---
async function deleteUser(id) {
  if (!confirm("Delete this user?")) return;
  const res = await fetch(`${API}/users/${id}`, { method: "DELETE" });
  if (res.ok) {
    showMsg("User deleted!");
    loadUsers();
  } else {
    showMsg("Error: " + (await res.text()), "error");
  }
}

// --- Delete Channel ---
async function deleteChannel(id) {
  if (!confirm("Delete this channel?")) return;
  const res = await fetch(`${API}/channels/${id}`, { method: "DELETE" });
  if (res.ok) {
    showMsg("Channel deleted!");
    loadChannels();
  } else {
    showMsg("Error: " + (await res.text()), "error");
  }
}

// --- Contact details fields mapping ---
const CONTACT_DETAILS_FIELDS = {
  email: ["email"],
  phone: ["phone_number"],
  slack: ["slack_id"],
  telegram: ["telegram_id"],
  whatsapp: ["whatsapp_number"],
};

function renderContactDetailsFields(channelType, contactDetails = {}) {
  const fields = CONTACT_DETAILS_FIELDS[channelType] || [];
  // debugger
  const container = document.getElementById('contact-details-fields');
  if (!container) return;
  container.innerHTML = '';
  fields.forEach(field => {
    const label = document.createElement('label');
    label.textContent = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
    const input = document.createElement('input');
    input.type = 'text';
    input.id = `contact-detail-${field}`;
    input.name = field;
    input.value = contactDetails[field] || '';
    input.required = true;
    container.appendChild(label);
    container.appendChild(input);
  });
}

// Update setupChannelConfigValidation to handle contact details
function setupUserChannelConfigValidation() {
  const channelSelect = document.getElementById('map-channel');
  if (!channelSelect) return;

  channelSelect.addEventListener('change', function() {
    console.log("Channel changed", channelSelect);
    const selectedOption = channelSelect.options[channelSelect.selectedIndex];
    const selectedChannelType = selectedOption?.getAttribute('data-type'); // Get the type from the data attribute
    renderContactDetailsFields(selectedChannelType);
  });
}

// Call setupUserChannelConfigValidation on page load
window.addEventListener('DOMContentLoaded', () => {
  loadSidebarAndPanels().then(() => {
    setTimeout(() => {
      setupChannelConfigValidation();
      setupUserChannelConfigValidation();
      const channelForm = document.getElementById("channel-form");
      if (channelForm) {
        const typeSelect = document.getElementById("channel-type");
        renderChannelConfigFields(typeSelect.value); // Initial render
      }
    }, 100);
  });
});
