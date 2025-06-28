// DOM elements
const historyPanel = document.getElementById("history-panel");
const mainContent = document.getElementById("main-content");
const dropdownContainer = document.getElementById("dropdown-container");
const toggleButton = document.getElementById("toggle-button");
const confirmModal = document.getElementById("confirm-modal");
const confirmDeleteBtn = document.getElementById("confirm-delete");
const cancelDeleteBtn = document.getElementById("cancel-delete");
const messageInput = document.getElementById("message");
const chatBox = document.getElementById("chat");
const dropdownMenu = document.getElementById("dropdown-menu");

// Global variables
let fullRawHistory = []; // [{ conversation_id, messages }]
let itemToDeleteConversationId = null;
let activeConvoId = null; // Track which conversation is active

function initializeMarked() {
  marked.setOptions({
    highlight: function(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    breaks: true,
    gfm: true,
  });
}

function toggleDropdown() {
  dropdownMenu.classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches('.dropdown-button')) {
    if (dropdownMenu.classList.contains('show')) {
      dropdownMenu.classList.remove('show');
    }
  }
}

function newChat() {
  clearChatBox();
  activeConvoId = null;
  dropdownMenu.classList.remove('show');
}

function clearChatBox() {
  chatBox.innerHTML = '';
  messageInput.value = '';
  messageInput.focus();
}

// ----------- HISTORY MANAGEMENT ---------
function transformHistory(rawHistory) {
  // rawHistory: [{conversation_id, messages: [...]}, ...]
  fullRawHistory = rawHistory;
  return rawHistory.map(convo => {
    const firstUserMsg = convo.messages.find(msg => msg.role === "user");
    return {
      user: firstUserMsg ? firstUserMsg.content : "(no user message)",
      conversation_id: convo.conversation_id
    };
  });
}

async function fetchHistory() {
  try {
    const res = await fetch("/api/history");
    if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);

    const rawHistory = await res.json();
    const history = transformHistory(rawHistory);
    renderHistory(history);
  } catch (error) {
    console.error("Error fetching history:", error);
  }
}

function createSummary(text, maxLength = 15) {
  if (!text) return "Chat";
  text = text.replace(/<[^>]*>/g, '');
  text = text.trim();
  if (text.length <= maxLength) {
    return text;
  } else {
    return text.substring(0, maxLength) + "...";
  }
}

function displayChatByConversationId(conversation_id) {
  const conversationObj = fullRawHistory.find(c => c.conversation_id === conversation_id);
  if (!conversationObj) return;

  chatBox.innerHTML = "";

  conversationObj.messages.forEach(msg => {
    const role = msg.role === "assistant" ? "bot" : "user";
    addMessageToChat(role, msg.content, role === "bot");
  });

  chatBox.scrollTop = chatBox.scrollHeight;
  activeConvoId = conversation_id;
}

function renderHistory(history) {
  const chatHistoryElement = document.getElementById("chat-history");
  chatHistoryElement.innerHTML = "";

  history.forEach((item) => {
    const li = document.createElement("li");
    const summary = createSummary(item.user);
    li.textContent = summary;
    li.title = item.user;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.setAttribute("aria-label", "Delete chat");
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      showDeleteConfirmation(item.conversation_id);
    };

    li.appendChild(deleteBtn);
    li.onclick = () => displayChatByConversationId(item.conversation_id);

    chatHistoryElement.appendChild(li);
  });
}

// ----------- MODAL / DELETE -----------
function showDeleteConfirmation(conversation_id) {
  itemToDeleteConversationId = conversation_id;
  confirmModal.classList.add("active");
}

function hideDeleteConfirmation() {
  confirmModal.classList.remove("active");
  itemToDeleteConversationId = null;
}

confirmDeleteBtn.addEventListener("click", () => {
  if (itemToDeleteConversationId !== null) {
    deleteHistoryItem(itemToDeleteConversationId);
  }
  hideDeleteConfirmation();
});

async function deleteHistoryItem(conversation_id) {
  try {
    const res = await fetch(`/api/history/${conversation_id}`, {
      method: 'DELETE',
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.message || `Failed to delete: ${res.status}`);
    }

    clearChatBox();
    fetchHistory();

    if (activeConvoId === conversation_id) {
      activeConvoId = null;
    }

  } catch (error) {
    console.error("Error deleting history item:", error);
    alert(`Failed to delete history item: ${error.message}`);
  }
}

// ----------- CHAT DISPLAY -------------
function addMessageToChat(role, content, parseMarkdown = false) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;

  // Add header with role label
  const headerDiv = document.createElement('div');
  headerDiv.className = 'message-header';
  headerDiv.textContent = role === 'user' ? 'You:' : 'AI:';
  messageDiv.appendChild(headerDiv);

  // Add content
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';

  if (parseMarkdown) {
    contentDiv.innerHTML = marked.parse(content);
  } else {
    contentDiv.textContent = content;
  }

  messageDiv.appendChild(contentDiv);
  chatBox.appendChild(messageDiv);

  // Apply syntax highlighting to code blocks
  document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
  });
}

// ----------- MESSAGE SENDING ---------
async function sendMessage() {
  const msg = messageInput.value;

  if (!msg.trim()) return;

  addMessageToChat('user', msg);
  messageInput.value = "";

  try {
    const payload = {
      message: msg
    };

    if (activeConvoId === null) {
      payload.new_session = true;
    } else {
      payload.convo_index = activeConvoId;
    }

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    const data = await res.json();

    addMessageToChat('bot', data.response, true);
    chatBox.scrollTop = chatBox.scrollHeight;

    if ('convo_index' in data) {
      activeConvoId = data.convo_index;
    }

    fetchHistory();

  } catch (error) {
    console.error("Error sending message:", error);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'message bot';
    errorDiv.innerHTML = `<div class="message-header">AI:</div>
                        <div class="message-content" style="color: #f87171;">
                          <b>Error:</b> Failed to get response. Please try again.
                        </div>`;
    chatBox.appendChild(errorDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

// ----------- UI -------------
function toggleHistory() {
  historyPanel.classList.toggle("expanded");
  mainContent.classList.toggle("with-expanded-history");
  dropdownContainer.classList.toggle("with-expanded-history");
}

function setupEventListeners() {
  cancelDeleteBtn.addEventListener("click", hideDeleteConfirmation);

  // Close modal if clicking outside of it
  confirmModal.addEventListener("click", (e) => {
    if (e.target === confirmModal) {
      hideDeleteConfirmation();
    }
  });

  // Handle Enter key to send messages
  messageInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });

  // Handle Escape key to close modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && confirmModal.classList.contains("active")) {
      hideDeleteConfirmation();
    }
  });

  // Auto-resize textarea based on content
  messageInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
  });
}

window.onload = function() {
  initializeMarked();
  setupEventListeners();
  fetchHistory();

  marked.setOptions({
    renderer: new marked.Renderer(),
    highlight: function(code, language) {
      if (language && hljs.getLanguage(language)) {
        return hljs.highlight(code, { language }).value;
      }
      return hljs.highlightAuto(code).value;
    },
    pedantic: false,
    gfm: true,
    breaks: true,
    sanitize: false,
    smartypants: false,
    xhtml: false
  });
};