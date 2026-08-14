/**
 * History page JavaScript
 * Handles chat history display, search, and filtering
 */

const state = {
    allChats: [],
    filteredChats: [],
    searchQuery: '',
    filter: 'all'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAllChats();
    setupEventListeners();
});

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const filterSelect = document.getElementById('filterSelect');
    const btnClear = document.getElementById('btnClearHistory');

    searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value.toLowerCase();
        filterChats();
    });

    filterSelect.addEventListener('change', (e) => {
        state.filter = e.target.value;
        filterChats();
    });

    btnClear.addEventListener('click', clearAllHistory);
}

function loadAllChats() {
    try {
        const stored = localStorage.getItem('umbuzo_chat_history');
        if (stored) {
            state.allChats = JSON.parse(stored);
            state.filteredChats = [...state.allChats];
            renderChats();
        } else {
            showEmptyState();
        }
    } catch (e) {
        console.error('Error loading chats:', e);
        showEmptyState();
    }
}

function filterChats() {
    let filtered = [...state.allChats];

    // Search filter
    if (state.searchQuery) {
        filtered = filtered.filter(chat => 
            chat.title.toLowerCase().includes(state.searchQuery) ||
            chat.conversation.some(msg => 
                msg.content.toLowerCase().includes(state.searchQuery)
            )
        );
    }

    // Date filter
    if (state.filter !== 'all') {
        const now = new Date();
        filtered = filtered.filter(chat => {
            const chatDate = new Date(chat.timestamp);
            const diff = now - chatDate;
            const days = diff / (1000 * 60 * 60 * 24);

            switch (state.filter) {
                case 'today':
                    return days < 1;
                case 'week':
                    return days < 7;
                case 'month':
                    return days < 30;
                default:
                    return true;
            }
        });
    }

    state.filteredChats = filtered;
    renderChats();
}

function renderChats() {
    const historyList = document.getElementById('historyList');
    const emptyState = document.getElementById('emptyState');

    if (!historyList) return;

    if (state.filteredChats.length === 0) {
        historyList.innerHTML = '';
        showEmptyState();
        return;
    }

    hideEmptyState();

    // Sort by timestamp (newest first)
    const sorted = [...state.filteredChats].sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
    );

    historyList.innerHTML = sorted.map(chat => {
        const date = new Date(chat.timestamp);
        const dateStr = formatDate(date);
        const preview = getChatPreview(chat);

        return `
            <div class="history-item-card" onclick="openChat('${chat.id}')">
                <div class="history-item-title">${escapeHtml(chat.title)}</div>
                <div class="history-item-preview">${escapeHtml(preview)}</div>
                <div class="history-item-meta">
                    <span>${dateStr}</span>
                    <span>${chat.conversation.length} messages</span>
                </div>
            </div>
        `;
    }).join('');
}

function getChatPreview(chat) {
    const firstUserMsg = chat.conversation.find(m => m.role === 'user');
    return firstUserMsg ? firstUserMsg.content.substring(0, 100) : 'No messages';
}

function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    
    return date.toLocaleDateString();
}

function openChat(chatId) {
    // Save chat ID and redirect to main page
    localStorage.setItem('umbuzo_load_chat_id', chatId);
    window.location.href = 'index.html';
}

function clearAllHistory() {
    if (!confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        return;
    }

    localStorage.removeItem('umbuzo_chat_history');
    state.allChats = [];
    state.filteredChats = [];
    renderChats();
    showEmptyState();
}

function showEmptyState() {
    const emptyState = document.getElementById('emptyState');
    if (emptyState) emptyState.style.display = 'block';
}

function hideEmptyState() {
    const emptyState = document.getElementById('emptyState');
    if (emptyState) emptyState.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
