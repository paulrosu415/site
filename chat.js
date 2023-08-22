// chat.js

// Simulăm un ID de utilizator pentru acest exemplu
const userId = 'user123';

// Funcția pentru trimiterea unui mesaj
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;
    
    if (message.trim() === '') {
        return;
    }
    
    // Simulăm trimiterea mesajului către server
    console.log(`User ${userId} sent message: ${message}`);
    
    // Aici puteți adăuga cod pentru a trimite mesajul către serverul dvs. într-o bază de date sau alt serviciu
}

// Funcția pentru afișarea mesajului în chat
function displayMessage(message) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.textContent = message;
    chatContainer.appendChild(messageElement);
}

// Funcția pentru gestionarea formularului de trimitere a mesajului
document.getElementById('message-form').addEventListener('submit', function(event) {
    event.preventDefault();
    sendMessage();
    document.getElementById('message-input').value = ''; // Goliți câmpul de mesaj după trimitere
});

// Afișăm un mesaj de bun venit în chat
displayMessage('Welcome to the chat!');
