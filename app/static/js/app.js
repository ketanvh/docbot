document.addEventListener('DOMContentLoaded', function() {
    // Check if debug mode is enabled (passed from the server)
    const DEBUG = document.documentElement.getAttribute('data-debug') === 'True';
    
    // Debug logging function
    function debugLog(message) {
        if (DEBUG) {
            console.log(`DEBUG [Frontend]: ${message}`);
        }
    }
    
    debugLog("Application initialized");
    
    // DOM Elements
    const uploadForm = document.getElementById('upload-form');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const welcomeScreen = document.getElementById('welcome-screen');
    const chatScreen = document.getElementById('chat-screen');
    const addUrlBtn = document.getElementById('add-url-btn');
    const websitesContainer = document.getElementById('websites-container');
    const resetChatBtn = document.getElementById('reset-chat-btn');
    const fileUpload = document.getElementById('file-upload');
    const fileList = document.getElementById('file-list');
    const resourcesBar = document.getElementById('resources-bar');
    const clearMessagesBtn = document.getElementById('clear-history-btn');
    
    // Track uploaded resources
    let selectedFiles = new Map(); // Using Map to track selected files
    let uploadedWebsites = [];
    let uploadedFiles = [];
    
    debugLog("DOM elements initialized");
    
    // Initialize event listeners
    safeAddEventListener(uploadForm, 'submit', handleUpload);
    safeAddEventListener(chatForm, 'submit', handleChatSubmit);
    safeAddEventListener(addUrlBtn, 'click', addUrlInput);
    safeAddEventListener(resetChatBtn, 'click', resetChatToWelcome);
    safeAddEventListener(fileUpload, 'change', handleFileSelection);
    safeAddEventListener(clearMessagesBtn, 'click', clearMessagesOnly);
    
    // Add a clear files button
    const clearFilesBtn = document.createElement('button');
    clearFilesBtn.type = 'button';
    clearFilesBtn.className = 'btn btn-outline btn-sm';
    clearFilesBtn.innerHTML = '<i class="fas fa-times"></i> Clear Files';
    clearFilesBtn.style.marginLeft = '10px';
    if (fileUpload && fileUpload.parentNode) {
        fileUpload.parentNode.appendChild(clearFilesBtn);
    }
    safeAddEventListener(clearFilesBtn, 'click', clearSelectedFiles);
    
    // Add event listeners to existing URL inputs
    setupUrlInputs();
    
    debugLog("Event listeners initialized");
    
    /**
     * Safely add event listener with null checks
     */
    function safeAddEventListener(element, event, handler) {
        if (element) {
            element.addEventListener(event, handler);
            debugLog(`Event listener added for ${event} on ${element.id || 'unnamed element'}`);
        } else {
            debugLog(`Failed to add event listener: element not found`);
        }
    }
    
    /**
     * URL validation function to check if a string is a valid URL format
     */
    function isValidUrl(url) {
        try {
            // Try to create a new URL object
            const parsedUrl = new URL(url);
            // Make sure the protocol is http or https
            return ['http:', 'https:'].includes(parsedUrl.protocol);
        } catch (e) {
            return false;
        }
    }
    
    /**
     * Set up event listeners for URL inputs to show/hide remove buttons
     */
    function setupUrlInputs() {
        if (!websitesContainer) return;
        
        // Add input event listeners to all existing URL inputs
        const existingInputs = websitesContainer.querySelectorAll('.url-input');
        existingInputs.forEach(input => {
            // Create a container for each URL input if it doesn't exist
            if (!input.parentNode.classList.contains('url-input-container')) {
                const container = document.createElement('div');
                container.className = 'url-input-container';
                input.parentNode.insertBefore(container, input);
                container.appendChild(input);
            }
            
            // Add input event listener to show/hide remove button and validate URL
            input.addEventListener('input', function() {
                updateRemoveButton(input);
                validateUrl(input);
            });
            
            // Add blur event to validate URL when focus leaves the input
            input.addEventListener('blur', function() {
                validateUrl(input, true);
            });
            
            // Initial setup of remove button
            updateRemoveButton(input);
        });
        
        debugLog(`Set up ${existingInputs.length} URL input listeners`);
    }
    
    /**
     * Validate URL input and show visual feedback
     * @param {HTMLInputElement} input - The URL input element
     * @param {boolean} showError - Whether to show error UI for invalid URLs
     */
    function validateUrl(input, showError = false) {
        const value = input.value.trim();
        
        // Clear existing error messages
        const errorMsg = input.parentNode.querySelector('.url-error');
        if (errorMsg) {
            errorMsg.remove();
        }
        
        // Reset input styles
        input.style.borderColor = '';
        
        // Skip validation if empty
        if (!value) {
            return true;
        }
        
        // Validate URL format
        if (!isValidUrl(value)) {
            if (showError) {
                // Show error styling
                input.style.borderColor = 'var(--error-color)';
                
                // Add error message
                const errorElement = document.createElement('div');
                errorElement.className = 'url-error';
                errorElement.textContent = 'Please enter a valid URL (e.g., https://example.com)';
                errorElement.style.color = 'var(--error-color)';
                errorElement.style.fontSize = '12px';
                errorElement.style.marginTop = '4px';
                
                input.parentNode.appendChild(errorElement);
            }
            return false;
        }
        
        return true;
    }
    
    /**
     * Update the remove button for a URL input based on its value
     */
    function updateRemoveButton(input) {
        const container = input.parentNode;
        if (!container.classList.contains('url-input-container')) return;
        
        // Remove any existing button
        const existingBtn = container.querySelector('.remove-url-btn');
        if (existingBtn) {
            existingBtn.remove();
        }
        
        // Only add a remove button if the input has a value
        if (input.value.trim()) {
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-url-btn';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.onclick = function() {
                input.value = '';
                removeBtn.remove();
                
                // Clear any error messages
                const errorMsg = container.querySelector('.url-error');
                if (errorMsg) {
                    errorMsg.remove();
                }
                input.style.borderColor = '';
            };
            container.appendChild(removeBtn);
        }
    }
    
    /**
     * Handle file selection for display in UI
     */
    function handleFileSelection(e) {
        try {
            if (!fileList) return;
            
            const newFiles = Array.from(e.target.files || []);
            debugLog(`Selected ${newFiles.length} new files`);
            
            // Add new files to the Map of selected files
            newFiles.forEach(file => {
                // Use file name and size as a simple unique identifier
                const fileId = `${file.name}_${file.size}`;
                selectedFiles.set(fileId, file);
            });
            
            // Update the UI
            updateFileListUI();
            
            // Clear the file input to allow selecting the same file again if needed
            if (fileUpload) {
                fileUpload.value = '';
            }
        } catch (error) {
            console.error('Error handling file selection:', error);
            debugLog(`ERROR in handleFileSelection: ${error.message}`);
        }
    }
    
    /**
     * Update the UI to show all selected files
     */
    function updateFileListUI() {
        if (!fileList) return;
        
        // Clear the current list
        fileList.innerHTML = '';
        
        // Add each file with a remove button
        selectedFiles.forEach((file, fileId) => {
            const li = document.createElement('li');
            li.className = 'file-item';
            
            const fileNameSpan = document.createElement('span');
            fileNameSpan.textContent = file.name;
            li.appendChild(fileNameSpan);
            
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-file-btn';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.setAttribute('data-file-id', fileId);
            removeBtn.onclick = function() {
                selectedFiles.delete(fileId);
                updateFileListUI();
            };
            
            li.appendChild(removeBtn);
            fileList.appendChild(li);
            debugLog(`Added/updated file in UI: ${file.name}`);
        });
    }
    
    /**
     * Clear all selected files
     */
    function clearSelectedFiles(e) {
        if (e) e.preventDefault();
        selectedFiles.clear();
        updateFileListUI();
        debugLog("Cleared all selected files");
    }
    
    /**
     * Add a new URL input field
     */
    function addUrlInput(e) {
        try {
            if (e) e.preventDefault();
            if (!websitesContainer) return;
            
            // Create container div for the URL input and remove button
            const inputContainer = document.createElement('div');
            inputContainer.className = 'url-input-container';
            
            // Create input element
            const input = document.createElement('input');
            input.type = 'url';
            input.className = 'url-input';
            input.placeholder = 'https://example.com';
            inputContainer.appendChild(input);
            
            // Add the input event listener for remove button and URL validation
            input.addEventListener('input', function() {
                updateRemoveButton(input);
                validateUrl(input);
            });
            
            // Add blur event to validate URL when focus leaves the input
            input.addEventListener('blur', function() {
                validateUrl(input, true);
            });
            
            // Add the container to the websites container
            websitesContainer.appendChild(inputContainer);
            debugLog("Added new URL input field");
            
            // Focus on the new input
            input.focus();
            
        } catch (error) {
            console.error('Error adding URL input:', error);
            debugLog(`ERROR in addUrlInput: ${error.message}`);
        }
    }
    
    // Initialize remove buttons on any existing URL inputs
    function initializeExistingUrlInputs() {
        if (!websitesContainer) return;
        
        const existingInputs = Array.from(websitesContainer.querySelectorAll('.url-input'));
        
        // Skip if there's only one empty input
        if (existingInputs.length === 1 && (!existingInputs[0].value || existingInputs[0].value.trim() === '')) {
            return;
        }
        
        // Process each input
        existingInputs.forEach(input => {
            // Skip if it's already in a container with a remove button
            if (input.parentNode && input.parentNode.classList.contains('url-input-container')) {
                return;
            }
            
            // Create a container
            const container = document.createElement('div');
            container.className = 'url-input-container';
            
            // Replace the input with the container + input
            input.parentNode.insertBefore(container, input);
            container.appendChild(input);
            
            // Create a remove button
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-url-btn';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.onclick = function() {
                container.remove();
                debugLog("Removed URL input field");
            };
            container.appendChild(removeBtn);
        });
        
        debugLog("Initialized remove buttons for existing URL inputs");
    }
    
    // Call once at startup to add remove buttons to any existing URL inputs
    initializeExistingUrlInputs();
    
    /**
     * Handle upload form submission
     */
    async function handleUpload(e) {
        try {
            if (e) e.preventDefault();
            debugLog("Upload form submitted");
            
            // Get all website inputs
            const urlInputs = document.querySelectorAll('.url-input') || [];
            const urlsWithErrors = [];
            
            // Validate all URLs
            urlInputs.forEach((input, index) => {
                const value = input.value.trim();
                if (value && !validateUrl(input, true)) {
                    urlsWithErrors.push(index + 1);
                }
            });
            
            // If there are URL validation errors, stop submission
            if (urlsWithErrors.length > 0) {
                const errorMessage = `Please fix the invalid URL${urlsWithErrors.length > 1 ? 's' : ''} in field${urlsWithErrors.length > 1 ? 's' : ''} #${urlsWithErrors.join(', #')}`;
                alert(errorMessage);
                debugLog(`Upload stopped due to invalid URLs: ${errorMessage}`);
                return;
            }
            
            // Get valid URLs
            const validUrls = Array.from(urlInputs)
                .map(input => input.value.trim())
                .filter(url => url !== '');
            
            // Get files from our Map
            const files = Array.from(selectedFiles.values());
            
            // Store uploaded resources info
            uploadedFiles = files.map(file => file.name);
            uploadedWebsites = [...validUrls];
            
            debugLog(`Processing upload with ${files.length} files and ${validUrls.length} URLs`);
            
            const formData = new FormData();
            
            // Add files to form data
            files.forEach(file => {
                formData.append('files', file);
                debugLog(`Added file to form data: ${file.name}`);
            });
            
            // Add websites to form data
            validUrls.forEach(url => {
                formData.append('websites', url);
                debugLog(`Added website to form data: ${url}`);
            });
            
            // Add filenames and website URLs as metadata
            formData.append('filenames', JSON.stringify(uploadedFiles));
            formData.append('websiteUrls', JSON.stringify(uploadedWebsites));
            
            debugLog("Sending upload request to server");
            // Send to server
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            
            const result = await response.json();
            debugLog(`Upload response received: ${JSON.stringify(result)}`);
            
            if (result.status === 'success') {
                // Switch to chat interface
                showChatScreen();
                
                // Add system message with document details
                if (result.resources) {
                    addSystemMessage(result.resources);
                } else if (files.length > 0 || validUrls.length > 0) {
                    // Fallback if server doesn't provide formatted message
                    const filesList = uploadedFiles.length > 0 
                        ? `Files: ${uploadedFiles.join(', ')}` 
                        : '';
                    
                    const websitesList = uploadedWebsites.length > 0 
                        ? `Websites: ${uploadedWebsites.join(', ')}` 
                        : '';
                    
                    const resourceList = [filesList, websitesList].filter(item => item).join('\n');
                    addSystemMessage(`Processed resources:\n${resourceList}\n\nYou can now ask questions about their content.`);
                } else {
                    addSystemMessage("No documents uploaded. You can ask general questions.");
                }
            } else {
                throw new Error(result.message || 'Failed to process files/websites');
            }
        } catch (error) {
            console.error('Upload error:', error);
            debugLog(`ERROR in handleUpload: ${error.message}`);
            alert(`Error uploading files: ${error.message}`);
        }
    }
    
    /**
     * Handle chat submission
     */
    async function handleChatSubmit(e) {
        try {
            if (e) e.preventDefault();
            
            const query = userInput?.value?.trim();
            if (!query) return;
            
            debugLog(`Chat submission with query: ${query}`);
            
            // Clear input
            if (userInput) userInput.value = '';
            
            // Add user message
            addUserMessage(query);
            
            debugLog("Sending chat request to server");
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            
            const result = await response.json();
            debugLog("Chat response received from server");
            
            // Add assistant's response
            if (result.response) {
                addBotMessage(result.response);
            }
            
            // Handle clear command
            if (query.toLowerCase() === 'clear') {
                debugLog("Clear command detected, resetting to welcome screen");
                showWelcomeScreen();
            }
        } catch (error) {
            console.error('Chat error:', error);
            debugLog(`ERROR in handleChatSubmit: ${error.message}`);
            addSystemMessage(`Error: ${error.message}`, true);
        }
    }
    
    /**
     * Clear chat and return to welcome screen
     */
    function resetChatToWelcome() {
        try {
            debugLog("Reset chat button clicked");
            if (userInput) userInput.value = 'clear';
            handleChatSubmit();
        } catch (error) {
            console.error('Error resetting chat:', error);
            debugLog(`ERROR in resetChatToWelcome: ${error.message}`);
            showWelcomeScreen(); // Fallback to direct screen switch
        }
    }
    
    /**
     * Clears only the chat history while preserving uploaded resources
     */
    function clearMessagesOnly() {
        try {
            debugLog("Clear messages button clicked");
            
            // Clear chat messages from the UI
            if (chatHistory) {
                chatHistory.innerHTML = '';
            }
            
            if (userInput) {
                userInput.value = '';
            }
            
            // Send a request to the server to clear chat history from session
            fetch('/api/clear_messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                debugLog(`Server cleared chat messages: ${JSON.stringify(result)}`);
                // Add a system message indicating history was cleared but context is preserved
                addSystemMessage("Chat messages cleared. Your uploaded resources are still available for context.");
            })
            .catch(error => {
                console.error('Error clearing chat messages on server:', error);
                debugLog(`ERROR clearing chat messages on server: ${error.message}`);
                addSystemMessage(`Error clearing chat messages: ${error.message}`, true);
            });
            
            debugLog("Chat messages cleared, but preserved uploaded resources");
        } catch (error) {
            console.error('Error clearing chat messages:', error);
            debugLog(`ERROR in clearMessagesOnly: ${error.message}`);
        }
    }

    /**
     * Add a user message to the chat
     */
    function addUserMessage(text) {
        try {
            if (!chatHistory) return;
            
            debugLog(`Adding user message: ${text.substring(0, 30)}${text.length > 30 ? '...' : ''}`);
            
            const message = document.createElement('div');
            message.className = 'message user-message';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = text;
            
            message.appendChild(bubble);
            chatHistory.appendChild(message);
            
            scrollToBottom();
        } catch (error) {
            console.error('Error adding user message:', error);
            debugLog(`ERROR in addUserMessage: ${error.message}`);
        }
    }
    
    /**
     * Add a bot message to the chat
     */
    function addBotMessage(text) {
        try {
            if (!chatHistory) return;
            
            debugLog(`Adding bot message: ${text.substring(0, 30)}${text.length > 30 ? '...' : ''}`);
            
            const message = document.createElement('div');
            message.className = 'message bot-message';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            
            try {
                // Try to parse markdown
                bubble.innerHTML = marked.parse(text);
                debugLog("Markdown parsed successfully");
            } catch (markdownError) {
                console.error('Error parsing markdown:', markdownError);
                debugLog(`ERROR parsing markdown: ${markdownError.message}`);
                bubble.textContent = text;
            }
            
            message.appendChild(bubble);
            chatHistory.appendChild(message);
            
            scrollToBottom();
        } catch (error) {
            console.error('Error adding bot message:', error);
            debugLog(`ERROR in addBotMessage: ${error.message}`);
        }
    }
    
    /**
     * Add a system message to the chat
     */
    function addSystemMessage(text, isError = false) {
        try {
            if (!chatHistory) return;
            
            debugLog(`Adding system message: ${text.substring(0, 30)}${text.length > 30 ? '...' : ''}`);
            
            const message = document.createElement('div');
            message.className = 'message system-message';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            if (isError) bubble.style.backgroundColor = '#f8d7da';
            bubble.textContent = text;
            
            // Add a special class for processed resources messages
            if (text.includes('Processed resources:')) {
                bubble.className += ' resources-message';
                bubble.style.fontSize = '12px';
                bubble.style.padding = '4px 5px';
                bubble.style.backgroundColor = '#f0f7ff';
                bubble.style.borderLeft = '2px solid var(--primary-color)';
                bubble.style.color = '#555';
            }
            
            message.appendChild(bubble);
            chatHistory.appendChild(message);
            
            scrollToBottom();
        } catch (error) {
            console.error('Error adding system message:', error);
            debugLog(`ERROR in addSystemMessage: ${error.message}`);
        }
    }
    
    /**
     * Scroll chat history to bottom
     */
    function scrollToBottom() {
        try {
            if (chatHistory) {
                chatHistory.scrollTop = chatHistory.scrollHeight;
                debugLog("Scrolled chat to bottom");
            }
        } catch (error) {
            console.error('Error scrolling to bottom:', error);
            debugLog(`ERROR in scrollToBottom: ${error.message}`);
        }
    }
    
    /**
     * Show welcome screen, hide chat screen
     */
    function showWelcomeScreen() {
        try {
            debugLog("Showing welcome screen");
            if (welcomeScreen) welcomeScreen.style.display = 'flex';
            if (chatScreen) chatScreen.style.display = 'none';
            
            // Reset form and chat history
            if (uploadForm) uploadForm.reset();
            if (chatHistory) chatHistory.innerHTML = '';
            if (fileList) fileList.innerHTML = '';
            
            // Clear selected files
            selectedFiles.clear();
            
            // Reset website inputs
            if (websitesContainer) {
                websitesContainer.innerHTML = '';
                
                // Add a single URL input with container
                const inputContainer = document.createElement('div');
                inputContainer.className = 'url-input-container';
                
                const initialInput = document.createElement('input');
                initialInput.type = 'url';
                initialInput.className = 'url-input';
                initialInput.placeholder = 'https://example.com';
                
                inputContainer.appendChild(initialInput);
                websitesContainer.appendChild(inputContainer);
                
                // No remove button for the first empty input
            }
            
            debugLog("Welcome screen setup complete");
        } catch (error) {
            console.error('Error showing welcome screen:', error);
            debugLog(`ERROR in showWelcomeScreen: ${error.message}`);
        }
    }
    
    /**
     * Show chat screen, hide welcome screen
     */
    function showChatScreen() {
        try {
            debugLog("Showing chat screen");
            if (welcomeScreen) welcomeScreen.style.display = 'none';
            if (chatScreen) {
                chatScreen.style.display = 'flex';
            }
            debugLog("Chat screen shown");
            
            // Update resources bar when showing chat screen
            updateResourcesBar();
        } catch (error) {
            console.error('Error showing chat screen:', error);
            debugLog(`ERROR in showChatScreen: ${error.message}`);
        }
    }
    
    /**
     * Update the resources bar with uploaded files and websites
     */
    function updateResourcesBar() {
        try {
            if (!resourcesBar) return;
            
            debugLog("Updating resources bar");
            resourcesBar.innerHTML = '';
            
            // Create container for files
            if (uploadedFiles && uploadedFiles.length > 0) {
                const filesContainer = document.createElement('div');
                filesContainer.className = 'resource-item files';
                
                const filesIcon = document.createElement('i');
                filesIcon.className = 'fas fa-file-alt';
                filesContainer.appendChild(filesIcon);
                
                const filesTitle = document.createElement('span');
                filesTitle.className = 'resource-title';
                filesTitle.textContent = `Files (${uploadedFiles.length})`;
                filesContainer.appendChild(filesTitle);
                
                // Create list for files
                const filesList = document.createElement('ul');
                filesList.className = 'resource-files-list';
                
                // Add each file as a separate tag-like item
                uploadedFiles.forEach(file => {
                    const fileItem = document.createElement('li');
                    fileItem.className = 'resource-file-item';
                    fileItem.title = file; // Add full filename as tooltip
                    fileItem.textContent = file;
                    filesList.appendChild(fileItem);
                });
                
                filesContainer.appendChild(filesList);
                resourcesBar.appendChild(filesContainer);
            }
            
            // Create container for websites
            if (uploadedWebsites && uploadedWebsites.length > 0) {
                const websitesContainer = document.createElement('div');
                websitesContainer.className = 'resource-item websites';
                
                const websitesIcon = document.createElement('i');
                websitesIcon.className = 'fas fa-globe';
                websitesContainer.appendChild(websitesIcon);
                
                const websitesTitle = document.createElement('span');
                websitesTitle.className = 'resource-title';
                websitesTitle.textContent = `Websites (${uploadedWebsites.length})`;
                websitesContainer.appendChild(websitesTitle);
                
                // Create list for websites
                const websitesList = document.createElement('ul');
                websitesList.className = 'resource-files-list';
                
                // Add each website as a separate tag-like item
                uploadedWebsites.forEach(url => {
                    const websiteItem = document.createElement('li');
                    websiteItem.className = 'resource-file-item';
                    websiteItem.title = url; // Add full URL as tooltip
                    
                    // Try to show domain name only for cleaner display
                    try {
                        const urlObj = new URL(url);
                        websiteItem.textContent = urlObj.hostname;
                    } catch (e) {
                        websiteItem.textContent = url;
                    }
                    
                    websitesList.appendChild(websiteItem);
                });
                
                websitesContainer.appendChild(websitesList);
                resourcesBar.appendChild(websitesContainer);
            }
            
            // If no resources, hide the bar
            if ((uploadedFiles?.length || 0) === 0 && (uploadedWebsites?.length || 0) === 0) {
                resourcesBar.style.display = 'none';
            } else {
                resourcesBar.style.display = 'flex';
            }
            
            debugLog("Resources bar updated");
        } catch (error) {
            console.error('Error updating resources bar:', error);
            debugLog(`ERROR in updateResourcesBar: ${error.message}`);
        }
    }
});