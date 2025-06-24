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
let fullRawHistory = [];
let itemToDeleteIndex = null;
let activeConvoIndex = null; // Track which conversation is active

// Initialize marked.js options when DOM is loaded
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

// Dropdown functionality
function toggleDropdown() {
  dropdownMenu.classList.toggle("show");
}

// Close the dropdown if clicked outside
window.onclick = function(event) {
  if (!event.target.matches('.dropdown-button')) {
    if (dropdownMenu.classList.contains('show')) {
      dropdownMenu.classList.remove('show');
    }
  }
}

// Chat management
function newChat() {
  clearChatBox();
  activeConvoIndex = null; // Next message will create a new chat
  dropdownMenu.classList.remove('show');
}

function clearChatBox() {
  chatBox.innerHTML = '';
  messageInput.value = '';
  messageInput.focus();
}

// History management
function transformHistory(rawHistory) {
  fullRawHistory = rawHistory;
  return rawHistory.map(conversation => {
    const firstUserMsg = conversation.find(msg => msg.role === "user");
    return {
      user: firstUserMsg ? firstUserMsg.content : "(no user message)",
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

function displayChatByIndex(index) {
  const conversation = fullRawHistory[index];
  if (!conversation) return;

  chatBox.innerHTML = "";

  conversation.forEach(msg => {
    const role = msg.role === "assistant" ? "bot" : "user";
    addMessageToChat(role, msg.content, role === "bot");
  });

  chatBox.scrollTop = chatBox.scrollHeight;
  activeConvoIndex = index; // Track current selected conversation
}

function renderHistory(history) {
  const chatHistoryElement = document.getElementById("chat-history");
  chatHistoryElement.innerHTML = "";

  history.forEach((item, index) => {
    const li = document.createElement("li");
    const summary = createSummary(item.user);
    li.textContent = summary;
    li.dataset.index = index;
    li.title = item.user;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.setAttribute("aria-label", "Delete chat");
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      showDeleteConfirmation(index);
    };

    li.appendChild(deleteBtn);
    li.onclick = () => displayChatByIndex(index);

    chatHistoryElement.appendChild(li);
  });
}

// Modal functionality
function showDeleteConfirmation(index) {
  itemToDeleteIndex = index;
  confirmModal.classList.add("active");
}

function hideDeleteConfirmation() {
  confirmModal.classList.remove("active");
  itemToDeleteIndex = null;
}

async function deleteHistoryItem(index) {
  try {
    const res = await fetch(`/api/history/${index}`, {
      method: 'DELETE',
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.message || `Failed to delete: ${res.status}`);
    }

    clearChatBox();
    fetchHistory();

    // If we deleted the currently viewed conversation, reset activeConvoIndex
    if (activeConvoIndex === index) {
      activeConvoIndex = null;
    }

  } catch (error) {
    console.error("Error deleting history item:", error);
    alert(`Failed to delete history item: ${error.message}`);
  }
}

// Chat display functionality
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

// Message sending functionality
async function sendMessage() {
  const msg = messageInput.value;

  if (!msg.trim()) return;

  addMessageToChat('user', msg);
  messageInput.value = "";

  try {
    const payload = {
      message: msg
    };

    if (activeConvoIndex === null) {
      // New chat
      payload.new_session = true;
    } else {
      payload.convo_index = activeConvoIndex;
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

    // Update active index if new conversation was created
    if ('convo_index' in data) {
      activeConvoIndex = data.convo_index;
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

// UI functionality
function toggleHistory() {
  historyPanel.classList.toggle("expanded");
  mainContent.classList.toggle("with-expanded-history");
  dropdownContainer.classList.toggle("with-expanded-history");
}

// Event listeners
function setupEventListeners() {
  // Modal event listeners
  confirmDeleteBtn.addEventListener("click", () => {
    if (itemToDeleteIndex !== null) {
      deleteHistoryItem(itemToDeleteIndex);
    }
    hideDeleteConfirmation();
  });

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

// Initialize the application
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