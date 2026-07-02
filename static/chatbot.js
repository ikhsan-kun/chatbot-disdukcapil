/**
 * ==========================================================================
 * DISDUKCAPIL KOTA TEGAL - MODERN AI CHATBOT INTERACTIVE CONTROLLER (HYBRID DIRECT VIEW)
 * ==========================================================================
 */

// DOM Elements
const chatMessagesArea = document.getElementById("chatMessagesArea");
const chatSuggestionsArea = document.getElementById("chatSuggestionsArea");
const chatInputField = document.getElementById("chatInputField");
const btnResetChat = document.getElementById("btnResetChat");
const chatWelcomeMessage = document.getElementById("chatWelcomeMessage");

// Active menu state
let currentMenu = null;

// Mapping agar bubble user tidak cuma angka
const menuText = {
    "1": "1. KTP",
    "2": "2. Kartu Keluarga",
    "3": "3. KIA",
    "4": "4. Akta Kelahiran",
    "5": "5. Akta Kematian",
    "6": "6. Pindah Datang",
    "7": "7. Perkawinan / Perceraian",
    "8": "8. Pengakuan / Pengesahan Anak",
    "9": "9. Perubahan Nama",
    "10": "10. Dokumen Hilang / Rusak",

    "1.1": "1. Syarat membuat KTP baru",
    "1.2": "2. Syarat cetak ulang KTP rusak",
    "1.3": "3. Syarat cetak ulang KTP hilang",
    "1.4": "4. Prosedur pembuatan KTP",

    "2.1": "1. Syarat membuat KK baru",
    "2.2": "2. Syarat perubahan KK",
    "2.3": "3. Syarat cetak ulang KK hilang/rusak",
    "2.4": "4. Syarat perubahan KK karena kematian",
    "2.5": "5. Syarat perubahan KK karena kedatangan/pindahan",
    "2.6": "6. Syarat perubahan status pendidikan",
    "2.7": "7. Prosedur pembuatan KK",

    "3.1": "1. Syarat KIA usia 0-5 tahun",
    "3.2": "2. Syarat KIA usia 5-17 tahun",
    "3.3": "3. Prosedur pembuatan KIA",

    "4.1": "1. Syarat pembuatan Akta Kelahiran",
    "4.2": "2. Prosedur pembuatan Akta Kelahiran",

    "5.1": "1. Syarat pencatatan kematian",
    "5.2": "2. Prosedur pencatatan kematian",

    "6.1": "1. Syarat pindah datang antar daerah (SKDWNI)",
    "6.2": "2. Prosedur pindah datang antar daerah",
    "6.3": "3. Syarat membuat Surat Pindah ke Luar Negeri",
    "6.4": "4. Prosedur membuat Surat Pindah ke Luar Negeri",
    "6.5": "5. Syarat pindah datang dari luar negeri",
    "6.6": "6. Prosedur pindah datang dari luar negeri",

    "7.1": "1. Syarat pencatatan perkawinan",
    "7.2": "2. Prosedur pencatatan perkawinan",
    "7.3": "3. Syarat pencatatan perceraian",
    "7.4": "4. Prosedur pencatatan perceraian",

    "8.1": "1. Syarat pencatatan pengakuan anak",
    "8.2": "2. Prosedur pencatatan pengakuan anak",
    "8.3": "3. Syarat pencatatan pengesahan anak",
    "8.4": "4. Prosedur pencatatan pengesahan anak",
    "8.5": "5. Syarat pencatatan pengangkatan anak",
    "8.6": "6. Prosedur pencatatan pengangkatan anak",
    "8.7": "7. Syarat pencatatan pengakuan status kewarganegaraan",
    "8.8": "8. Prosedur pencatatan pengakuan status kewarganegaraan",

    "9.1": "1. Syarat perubahan nama",
    "9.2": "2. Prosedur perubahan nama",

    "10.1": "1. Syarat penerbitan kembali dokumen kependudukan karena hilang/rusak",
    "10.2": "2. Prosedur penerbitan kembali dokumen kependudukan",
    "10.3": "3. Syarat pencatatan peristiwa penting lainnya",
    "10.4": "4. Prosedur pencatatan peristiwa penting lainnya",

    "menu": "Menu utama",
    "0": "0. Kembali ke menu utama"
};

/**
 * 1. CHAT ACTIONS & STATE RESET
 */


// Reset percakapan, hapus history kecuali pesan selamat datang awal
function resetChat() {
    currentMenu = null;

    // Cari semua bubble dinamis (yang bukan welcome message)
    const bubbles = chatMessagesArea.querySelectorAll(".message-bubble-wrapper");
    bubbles.forEach(bubble => {
        if (bubble.id !== "chatWelcomeMessage") {
            bubble.remove();
        }
    });

    // Tampilkan kembali pesan awal
    if (chatWelcomeMessage) {
        chatWelcomeMessage.style.display = "flex";
    }

    // Scroll kembali ke atas
    chatMessagesArea.scrollTop = 0;

    // Kosongkan kolom input
    chatInputField.value = "";
    chatInputField.focus();
}

/**
 * 2. CHAT DISPATCH & API CALLS
 */

// Mengirim pesan dari input text bebas
function handleSendClick() {
    const message = chatInputField.value.trim();
    if (message === "") return;

    dispatchChatQuery(message);
    chatInputField.value = "";
}

// Mengirim pesan dari klik list 1-5 atau suggestion chips
function sendDirectQuery(queryText) {
    if (!queryText) return;
    dispatchChatQuery(queryText);
}

// Mengirim kueri ke API dan mengelola UI bubbles
async function dispatchChatQuery(messageText) {
    let apiMessage = messageText.trim().toLowerCase();
    let displayMessage = messageText;

    if (apiMessage === "menu" || apiMessage === "0") {
        currentMenu = null;
        displayMessage = menuText[apiMessage] || messageText;
    } else if (currentMenu === null) {
        const isMainMenuNum = /^(10|[1-9])$/.test(apiMessage);
        if (isMainMenuNum) {
            currentMenu = apiMessage;
            displayMessage = menuText[apiMessage] || messageText;
        } else if (menuText[apiMessage]) {
            displayMessage = menuText[apiMessage];
        }
    } else {
        const isSubMenuNum = /^\d+$/.test(apiMessage);
        if (isSubMenuNum) {
            const possibleCode = `${currentMenu}.${apiMessage}`;
            if (menuText[possibleCode]) {
                apiMessage = possibleCode;
                displayMessage = menuText[possibleCode];
            } else {
                const isMainMenuNum = /^(10|[1-9])$/.test(apiMessage);
                if (isMainMenuNum) {
                    currentMenu = apiMessage;
                    displayMessage = menuText[apiMessage] || messageText;
                } else {
                    displayMessage = menuText[apiMessage] || messageText;
                }
            }
        } else {
            if (menuText[apiMessage]) {
                displayMessage = menuText[apiMessage];
            }
        }
    }

    // 1. Tampilkan bubble pesan user di layar
    appendUserBubble(displayMessage);
    scrollToBottom();

    // 2. Tampilkan loading/typing indicator bot
    const typingBubble = showTypingIndicator();
    scrollToBottom();

    try {
        // Panggil endpoint FastAPI RAG
        const response = await fetch("/api/chatbot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: apiMessage })
        });

        if (!response.ok) {
            throw new Error("HTTP error " + response.status);
        }

        const data = await response.json();

        // 3. Hapus loading, tampilkan jawaban bot
        hideTypingIndicator(typingBubble);
        appendBotBubble(data.reply);

    } catch (error) {
        console.error("Error communicating with AI Chatbot:", error);
        hideTypingIndicator(typingBubble);
        appendBotBubble("Maaf, sepertinya asisten AI kami sedang sibuk atau koneksi terputus. Silakan coba tanyakan kembali beberapa saat lagi.");
    }

    scrollToBottom();
}

/**
 * 3. HTML INJECTIONS & MARKDOWN FORMATTER
 */

// Memformat teks mentah (raw text) menjadi HTML rapi (bold, bullet, dsb)
function formatMessageContent(rawText) {
    if (!rawText) return "";

    // Bersihkan karakter berlebih
    let text = rawText.trim();

    // 1. Format Bold (**bold text** atau *bold text*)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // 2. Format Bullet List (baris diawali "- " atau "* ")
    const lines = text.split("\n");
    let isInsideList = false;
    let listType = null; // 'ul' atau 'ol'
    let formattedHtml = "";

    lines.forEach(line => {
        const trimmedLine = line.trim();

        if (trimmedLine.startsWith("- ") || trimmedLine.startsWith("* ")) {
            if (!isInsideList || listType !== "ul") {
                if (isInsideList) {
                    formattedHtml += listType === "ul" ? "</ul>" : "</ol>";
                }
                formattedHtml += "<ul>";
                isInsideList = true;
                listType = "ul";
            }
            const liContent = trimmedLine.substring(2);
            formattedHtml += `<li>${liContent}</li>`;
        }
        // 3. Format Numbered List (baris diawali angka seperti "1. ", "2. ")
        else if (/^\d+\.\s/.test(trimmedLine)) {
            if (!isInsideList || listType !== "ol") {
                if (isInsideList) {
                    formattedHtml += listType === "ul" ? "</ul>" : "</ol>";
                }
                formattedHtml += "<ol>";
                isInsideList = true;
                listType = "ol";
            }
            const liContent = trimmedLine.replace(/^\d+\.\s/, "");
            formattedHtml += `<li>${liContent}</li>`;
        }
        else {
            if (isInsideList) {
                formattedHtml += listType === "ul" ? "</ul>" : "</ol>";
                isInsideList = false;
                listType = null;
            }

            if (trimmedLine !== "") {
                formattedHtml += `<p>${trimmedLine}</p>`;
            } else {
                formattedHtml += "<br>";
            }
        }
    });

    if (isInsideList) {
        formattedHtml += listType === "ul" ? "</ul>" : "</ol>";
    }

    return formattedHtml;
}

// Menambahkan bubble pesan user
function appendUserBubble(text) {
    const bubbleWrapper = document.createElement("div");
    bubbleWrapper.className = "message-bubble-wrapper user";

    bubbleWrapper.innerHTML = `
        <div class="message-bubble-body">
            <div class="message-avatar-circle">👤</div>
            <div class="message-content-box">
                <p>${escapeHtml(text)}</p>
            </div>
        </div>
    `;

    chatMessagesArea.appendChild(bubbleWrapper);
}

// Menambahkan bubble pesan asisten bot
function appendBotBubble(text) {
    const bubbleWrapper = document.createElement("div");
    bubbleWrapper.className = "message-bubble-wrapper bot";

    const formattedHtml = formatMessageContent(text);

    bubbleWrapper.innerHTML = `
        <div class="message-bubble-body">
            <div class="message-avatar-circle">🤖</div>
            <div class="message-content-box">
                ${formattedHtml}
            </div>
        </div>
    `;

    chatMessagesArea.appendChild(bubbleWrapper);
}

// Tampilkan bouncing typing dots bot
function showTypingIndicator() {
    const bubbleWrapper = document.createElement("div");
    bubbleWrapper.className = "message-bubble-wrapper bot";
    bubbleWrapper.id = "temp-typing-indicator";

    bubbleWrapper.innerHTML = `
        <div class="message-bubble-body">
            <div class="message-avatar-circle">🤖</div>
            <div class="message-content-box">
                <div class="typing-dots-modern">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;

    chatMessagesArea.appendChild(bubbleWrapper);
    return bubbleWrapper;
}

// Sembunyikan typing indicator
function hideTypingIndicator(element) {
    if (element) {
        element.remove();
    } else {
        const temp = document.getElementById("temp-typing-indicator");
        if (temp) temp.remove();
    }
}

// Helper auto-scroll ke bawah chat area
function scrollToBottom() {
    chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;
}

// Helper sanitasi teks input
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * 4. EVENT LISTENERS INITIALIZATION
 */
document.addEventListener("DOMContentLoaded", () => {
    // Koneksikan Enter key pada kolom input
    if (chatInputField) {
        chatInputField.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleSendClick();
            }
        });
    }

    // Modal Tutorial Logic
    const tutorialModal = document.getElementById("chatbotTutorialModal");
    const btnDismissTutorial = document.getElementById("btnDismissTutorial");

    if (tutorialModal && btnDismissTutorial) {
        // Tampilkan modal secara langsung saat halaman dibuka
        tutorialModal.classList.add("show");

        // Ketika tombol "Oke" diklik, sembunyikan modal dan fokus ke input chat
        btnDismissTutorial.addEventListener("click", () => {
            tutorialModal.classList.remove("show");
            if (chatInputField) {
                chatInputField.focus();
            }
        });

        // Opsional: Klik di luar kartu modal untuk menutup (opsi kenyamanan tambahan)
        tutorialModal.addEventListener("click", (e) => {
            if (e.target === tutorialModal) {
                tutorialModal.classList.remove("show");
                if (chatInputField) {
                    chatInputField.focus();
                }
            }
        });
    } else {
        // Fallback autofocus jika modal tidak ditemukan
        if (chatInputField) {
            chatInputField.focus();
        }
    }
});