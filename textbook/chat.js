export function createChatInterface({
  apiUrl,
  instructions,
  firstMessage,
  bossImage = 'img/environ_minister.jpg',
  bossName = 'Minister Reed',
  maxTokens = 100
}) {
  let messageCount = 0;
  let messages = [
    { role: "system", content: instructions },
    { role: "assistant", content: firstMessage }
  ];

  async function sendOpenAIRequest(prompt) { 

    try {
      messages.push({ role: "user", content: prompt });

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: "gpt-4o",
          messages: messages,
          temperature: 1,
          max_tokens: maxTokens,
          top_p: 1,
          frequency_penalty: 0,
          presence_penalty: 0
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const assistantResponse = data.choices[0].message.content;
      messages.push({ role: "assistant", content: assistantResponse });

      return assistantResponse;
    } catch (error) {
      console.error("Error:", error);
      throw error;
    }
  }

  function createChatMessageHTML(content, isBoss) {
    return `
      <div class="chat-message ${isBoss ? 'boss-message' : 'user-message'}">
        ${isBoss ? `<div class="chat-avatar" style="background-image: url('${bossImage}')"></div>` : ''}
        <div class="chat-message-content">
          <div class="chat-sender-name">${isBoss ? bossName : 'You'}</div>
          <div>${content}</div>
        </div>
      </div>
    `;
  }

  const container = document.createElement('div');
  container.innerHTML = `
    <div id="chat-container">
      <div class="highlight-line"></div>
      <div id="chat-display"></div>
      <textarea id="user-input" placeholder="Enter your message here"></textarea>
      <button id="submit-button">Send Message</button>
    </div>
  `;

  const chatDisplay = container.querySelector('#chat-display');
  const userInput = container.querySelector('#user-input');
  const submitButton = container.querySelector('#submit-button');

  chatDisplay.innerHTML += createChatMessageHTML(firstMessage, true);

  async function handleSubmit() {
    const prompt = userInput.value;
    if (prompt.trim() === '') return;
    messageCount++;
    chatDisplay.innerHTML += createChatMessageHTML(prompt, false);
    userInput.value = '';
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
    try {
      const response = await sendOpenAIRequest(prompt);
      chatDisplay.innerHTML += createChatMessageHTML(response, true);
    } catch (error) {
      chatDisplay.innerHTML += createChatMessageHTML("Error: " + error.message, true);
    }
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
  }

  submitButton.onclick = handleSubmit;
  userInput.addEventListener('keypress', e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSubmit()));

  chatDisplay.scrollTop = chatDisplay.scrollHeight;
  return container;
}
