document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // SHARED MARKDOWN PARSER HELPER
    // -------------------------------------------------------------
    function parseMarkdown(text) {
        if (!text) return '';
        
        let html = text
            // Escape HTML entities to prevent XSS
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Bullet list items
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            // Horizontal rule
            .replace(/^---$/gim, '<hr>')
            // Line breaks
            .replace(/\n$/gim, '<br>')
            .replace(/\n/g, '<br>');

        // Wrap consecutive li elements in ul
        html = html.replace(/(<li>.*<\/li>)+/gim, '<ul>$&</ul>');
        // Clean double ul tags
        html = html.replace(/<\/ul>\s*<ul>/g, '');
        
        return html;
    }

    // Determine current page context
    const pathParts = window.location.pathname.split('/');
    const isReportPage = pathParts.includes('report');
    const reportId = isReportPage ? pathParts[pathParts.indexOf('report') + 1] : null;

    // -------------------------------------------------------------
    // CUSTOM SCREEN POPUP MODAL ALERT
    // -------------------------------------------------------------
    const customModal = document.getElementById('custom-alert-modal');
    const customModalTitle = document.getElementById('custom-modal-title');
    const customModalMsg = document.getElementById('custom-modal-message');
    const customModalClose = document.getElementById('custom-modal-close-btn');

    function showCustomAlert(title, message) {
        if (customModal && customModalTitle && customModalMsg) {
            customModalTitle.textContent = title;
            customModalMsg.textContent = message;
            customModal.classList.add('active');
        } else {
            alert(`${title}\n\n${message}`);
        }
    }

    if (customModalClose) {
        customModalClose.addEventListener('click', () => {
            customModal.classList.remove('active');
        });
    }

    if (customModal) {
        customModal.addEventListener('click', (e) => {
            if (e.target === customModal) {
                customModal.classList.remove('active');
            }
        });
    }

    // -------------------------------------------------------------
    // SAFE FETCH HELPER (Handles 500 HTML or other non-JSON crashes)
    // -------------------------------------------------------------
    async function safeFetchJson(url, options) {
        try {
            const response = await fetch(url, options);
            const contentType = response.headers.get("content-type");
            
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const data = await response.json();
                if (!response.ok) {
                    return { success: false, error: data.error || `Server returned status ${response.status}` };
                }
                return data;
            } else {
                const text = await response.text();
                // Check if it is a Flask debug/error page
                let errMsg = `Internal Server Error (${response.status})`;
                if (text.includes('<title>')) {
                    const titleMatch = text.match(/<title>([\s\S]*?)<\/title>/);
                    if (titleMatch && titleMatch[1]) {
                        errMsg = titleMatch[1].trim();
                    }
                }
                return { success: false, error: errMsg };
            }
        } catch (err) {
            return { success: false, error: `Network connection error: ${err.message}` };
        }
    }

    // -------------------------------------------------------------
    // HOMEPAGE SLIDER CONTROLLER
    // -------------------------------------------------------------
    const slidesWrapper = document.getElementById('slides-wrapper');
    const btnNextSlide = document.getElementById('btn-next-slide');
    const btnPrevSlide = document.getElementById('btn-prev-slide');
    const tabSlide1 = document.getElementById('tab-slide-1');
    const tabSlide2 = document.getElementById('tab-slide-2');
    const navBtnStart = document.getElementById('nav-btn-start');

    function goToSlide(slideIndex) {
        if (!slidesWrapper) return;
        
        if (slideIndex === 1) {
            slidesWrapper.style.transform = 'translateX(0)';
            if (tabSlide1) tabSlide1.classList.add('active');
            if (tabSlide2) tabSlide2.classList.remove('active');
        } else if (slideIndex === 2) {
            slidesWrapper.style.transform = 'translateX(-50%)';
            if (tabSlide2) tabSlide2.classList.add('active');
            if (tabSlide1) tabSlide1.classList.remove('active');
        }
    }

    if (btnNextSlide) btnNextSlide.addEventListener('click', () => goToSlide(2));
    if (btnPrevSlide) btnPrevSlide.addEventListener('click', () => goToSlide(1));
    if (tabSlide1) tabSlide1.addEventListener('click', () => goToSlide(1));
    if (tabSlide2) tabSlide2.addEventListener('click', () => goToSlide(2));
    if (navBtnStart) navBtnStart.addEventListener('click', (e) => {
        e.preventDefault();
        goToSlide(2);
        const uploadSection = document.getElementById('upload-section');
        if (uploadSection) uploadSection.scrollIntoView({ behavior: 'smooth' });
    });


    // -------------------------------------------------------------
    // CHATBOT FLOATING WIDGET INJECTION & LOGIC
    // -------------------------------------------------------------
    let generalChatHistory = []; // Local history state for homepage general chat

    function injectChatbotWidget() {
        if (document.getElementById('chatbot-widget-trigger')) return;

        const widgetContainer = document.createElement('div');
        widgetContainer.id = 'chatbot-widget-container';
        widgetContainer.innerHTML = `
            <button id="chatbot-widget-trigger" class="chatbot-trigger" title="Open Medical Assistant">
                <span class="trigger-icon">💬</span>
                <span class="trigger-pulse"></span>
            </button>
            <div id="chatbot-widget-window" class="chatbot-window">
                <div class="chatbot-header">
                    <div class="chatbot-title">
                        <span class="chatbot-status-dot"></span>
                        <div>
                            <h4>Medical Assistant</h4>
                            <span id="chatbot-subtitle" class="chatbot-subtitle">Ready to help</span>
                        </div>
                    </div>
                    <button id="chatbot-close-btn" class="chatbot-close-btn" title="Close chat">&times;</button>
                </div>
                <div id="chatbot-messages" class="chatbot-messages">
                    <!-- Loaded dynamically -->
                </div>
                <div class="chatbot-input-area">
                    <input type="text" id="chatbot-input" placeholder="Ask a question about health..." autocomplete="off">
                    <button id="chatbot-send-btn" class="chatbot-send-btn" title="Send message">➔</button>
                </div>
            </div>
        `;
        document.body.appendChild(widgetContainer);
        setupChatbotListeners();
    }

    function openChatbotWidget() {
        const chatWindow = document.getElementById('chatbot-widget-window');
        if (chatWindow) {
            chatWindow.classList.add('active');
            const chatMessages = document.getElementById('chatbot-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            const chatInput = document.getElementById('chatbot-input');
            if (chatInput) {
                chatInput.focus();
            }
        }
    }

    function closeChatbotWidget() {
        const chatWindow = document.getElementById('chatbot-widget-window');
        if (chatWindow) {
            chatWindow.classList.remove('active');
        }
    }

    function setupChatbotListeners() {
        const trigger = document.getElementById('chatbot-widget-trigger');
        const closeBtn = document.getElementById('chatbot-close-btn');
        const chatWindow = document.getElementById('chatbot-widget-window');
        const chatInput = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send-btn');
        const chatMessages = document.getElementById('chatbot-messages');

        // Toggle widget open/close
        trigger.addEventListener('click', () => {
            if (chatWindow.classList.contains('active')) {
                closeChatbotWidget();
            } else {
                openChatbotWidget();
            }
        });

        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeChatbotWidget();
        });

        // Send chat event
        const handleSendMessage = async () => {
            const text = chatInput.value.trim();
            if (!text) return;

            appendChatBubble(text, 'user');
            chatInput.value = '';

            const typingBubble = appendChatBubble('Thinking...', 'bot typing');

            try {
                let result;
                if (reportId) {
                    // Send to report-based chatbot route
                    result = await safeFetchJson(`/report/${reportId}/chat/send`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    });
                } else {
                    // Send to general chatbot route on the home page, including local session history
                    result = await safeFetchJson('/api/chat/general', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text, history: generalChatHistory })
                    });
                    if (result.success) {
                        generalChatHistory.push({ sender: 'user', message: text });
                        generalChatHistory.push({ sender: 'bot', message: result.response });
                    }
                }

                typingBubble.remove();
                if (result.success) {
                    appendChatBubble(result.response, 'bot');
                } else {
                    appendChatBubble(`Error: ${result.error || 'Could not query assistant.'}`, 'bot');
                    showCustomAlert('Assistant Connection Issue', result.error || 'Could not query assistant.');
                }
            } catch (err) {
                typingBubble.remove();
                appendChatBubble(`Connection Error: ${err.message}`, 'bot');
                showCustomAlert('Network Error', err.message);
            }
        };

        sendBtn.addEventListener('click', handleSendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSendMessage();
            }
        });
    }

    function appendChatBubble(text, senderClass) {
        const chatMessages = document.getElementById('chatbot-messages');
        if (!chatMessages) return null;

        const bubble = document.createElement('div');
        bubble.className = `message ${senderClass}`;
        
        if (senderClass.includes('bot') && !senderClass.includes('typing')) {
            bubble.innerHTML = parseMarkdown(text);
        } else {
            bubble.textContent = text;
        }

        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return bubble;
    }

    async function loadChatbotContext() {
        injectChatbotWidget();
        const chatMessages = document.getElementById('chatbot-messages');
        const subtitle = document.getElementById('chatbot-subtitle');

        if (!chatMessages) return;
        chatMessages.innerHTML = ''; // Clear previous

        if (reportId) {
            // Report details are active
            subtitle.textContent = "Analyzing Active Report";
            
            // Set initial welcome greeting
            appendChatBubble("Hello! I have analyzed your medical report. Feel free to ask me questions like:\n\n* *'What does this WBC count mean?'*\n* *'Are my cholesterol levels high?'*\n* *'Explain the conclusion sentence.'*", "bot");
            
            // Fetch saved database chat history for this report
            try {
                const data = await safeFetchJson(`/api/report/${reportId}/chat/history`);
                if (data.success && data.history.length > 0) {
                    data.history.forEach(msg => {
                        appendChatBubble(msg.message, msg.sender);
                    });
                }
            } catch (err) {
                console.error("Failed to load chat history", err);
            }
        } else {
            // General home page
            subtitle.textContent = "General Assistant";
            appendChatBubble("Welcome to the **Medical Report Simplifier**! 🩺\n\nPlease upload a lab report, MRI scan, or clinical findings on the homepage. Once uploaded, I will analyze the specifics of your results.\n\nIn the meantime, feel free to ask me any general health questions here!", "bot");
        }
    }

    // Initialize the widget immediately on DOM load
    loadChatbotContext();

    // Setup redirect button triggers to toggle floating widget
    const reportChatTrigger = document.getElementById('btn-chat-trigger');
    const reportChatStart = document.getElementById('btn-chat-start');
    [reportChatTrigger, reportChatStart].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                openChatbotWidget();
            });
        }
    });


    // -------------------------------------------------------------
    // UPLOAD CONTROLLER (HOMEPAGE)
    // -------------------------------------------------------------
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileStatus = document.getElementById('file-status');
    const fileNameDisplay = document.getElementById('file-name');
    const fileSizeDisplay = document.getElementById('file-size');
    const btnRemove = document.getElementById('btn-remove');
    const btnSubmit = document.getElementById('btn-submit');
    const loaderWrapper = document.getElementById('loader-wrapper');
    const uploadForm = document.getElementById('upload-form');

    if (dropZone && fileInput) {
        // Drag-and-drop triggers & click selects
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, () => {
                dropZone.classList.remove('dragover');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileStatus(fileInput.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                updateFileStatus(fileInput.files[0]);
            }
        });

        if (btnRemove) {
            btnRemove.addEventListener('click', (e) => {
                e.stopPropagation();
                resetFileStatus();
            });
        }

        function updateFileStatus(file) {
            fileNameDisplay.textContent = file.name;
            const sizeInMb = (file.size / (1024 * 1024)).toFixed(2);
            fileSizeDisplay.textContent = `(${sizeInMb} MB)`;
            fileStatus.style.display = 'flex';
            btnSubmit.removeAttribute('disabled');
        }

        function resetFileStatus() {
            fileInput.value = '';
            fileStatus.style.display = 'none';
            btnSubmit.setAttribute('disabled', 'true');
        }

        if (uploadForm) {
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const file = fileInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);
                
                // Extract and append selected target output language
                const selectLangUpload = document.getElementById('select-lang-upload');
                if (selectLangUpload) {
                    formData.append('lang', selectLangUpload.value);
                }

                // Hide inputs, show loader
                dropZone.style.display = 'none';
                fileStatus.style.display = 'none';
                btnSubmit.style.display = 'none';
                loaderWrapper.style.display = 'flex';

                try {
                    const result = await safeFetchJson('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (result.success) {
                        window.location.href = `/report/${result.report_id}`;
                    } else {
                        showCustomAlert('File Processing Failed', result.error || 'Failed to process report.');
                        resetToUploadState();
                    }
                } catch (err) {
                    showCustomAlert('Network Error', 'An error occurred during upload: ' + err.message);
                    resetToUploadState();
                }
            });
        }

        function resetToUploadState() {
            dropZone.style.display = 'flex';
            fileStatus.style.display = 'none';
            btnSubmit.style.display = 'block';
            btnSubmit.setAttribute('disabled', 'true');
            loaderWrapper.style.display = 'none';
        }
    }


    // -------------------------------------------------------------
    // DYNAMIC REPORT DATA LOADING (REPORT PAGE)
    // -------------------------------------------------------------
    const selectTranslate = document.getElementById('select-translate');
    const reportBody = document.getElementById('report-body');
    const reportFilename = document.getElementById('report-filename');
    const reportDate = document.getElementById('report-date');

    if (reportId && reportBody) {
        // Fetch report details dynamically
        safeFetchJson(`/api/report/${reportId}`)
            .then(data => {
                if (data.success) {
                    const report = data.report;
                    // Populate details
                    reportFilename.textContent = report.filename;
                    reportDate.textContent = `Uploaded: ${report.created_at}`;
                    reportBody.innerHTML = parseMarkdown(report.simplified_text);

                    // Populate languages
                    if (selectTranslate && data.languages) {
                        selectTranslate.innerHTML = '';
                        for (const [code, name] of Object.entries(data.languages)) {
                            const opt = document.createElement('option');
                            opt.value = code;
                            opt.textContent = name;
                            if (code === 'en') opt.selected = true;
                            selectTranslate.appendChild(opt);
                        }
                        setupTranslationListener();
                    }
                } else {
                    displayReportError(data.error || "Could not retrieve report.");
                }
            })
            .catch(err => {
                displayReportError("Connection failure: " + err.message);
            });

        function displayReportError(msg) {
            reportBody.innerHTML = `
                <div class="report-error-card">
                    <h3>⚠️ Error Loading Report</h3>
                    <p>${msg}</p>
                    <a href="/" class="btn-primary" style="display: inline-block; margin-top: 1rem; text-decoration: none;">Return Home</a>
                </div>
            `;
            showCustomAlert('Load Failure', msg);
        }

        function setupTranslationListener() {
            selectTranslate.addEventListener('change', async () => {
                const langCode = selectTranslate.value;
                
                // Set loading state
                reportBody.style.opacity = '0.4';
                
                try {
                    const result = await safeFetchJson(`/report/${reportId}/translate`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ lang: langCode })
                    });
                    
                    if (result.success) {
                        // Update content and re-parse markdown
                        reportBody.innerHTML = parseMarkdown(result.translated_text);
                    } else {
                        showCustomAlert('Translation Failed', result.error || 'Failed to translate.');
                    }
                } catch (err) {
                    showCustomAlert('Network Error', 'Error processing translation: ' + err.message);
                } finally {
                    reportBody.style.opacity = '1';
                }
            });
        }

        // Setup Print and Download Button Listeners
        const printBtn = document.getElementById('btn-print-report');
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                window.print();
            });
        }

        const downloadBtn = document.getElementById('btn-download-report');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                const textContent = reportBody.innerText;
                const filename = (reportFilename.textContent || "Medical_Report").replace(/\s+/g, "_");
                const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `${filename}_Simplified.txt`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        }
    }
});
