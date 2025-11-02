// Generate a unique session ID
const SESSION_ID = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const generateMindmapBtn = document.getElementById('generateMindmapBtn');
const mindmapContainer = document.getElementById('mindmap');

// Chat functionality
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    messageInput.value = '';
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessageToChat('assistant', data.response);
        } else {
            addMessageToChat('assistant', 'Sorry, there was an error processing your message.');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'Sorry, there was an error connecting to the server.');
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = role === 'user' ? 'You' : 'AI Assistant';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function clearChat() {
    if (!confirm('Are you sure you want to clear the chat?')) return;

    try {
        await fetch(`/api/chat/${SESSION_ID}`, {
            method: 'DELETE'
        });

        chatMessages.innerHTML = '';
        mindmapContainer.innerHTML = '<div class="mindmap-placeholder">Chat with the AI, then click "Generate Mindmap" to visualize your conversation</div>';
    } catch (error) {
        console.error('Error clearing chat:', error);
    }
}

async function generateMindmap() {
    generateMindmapBtn.disabled = true;
    generateMindmapBtn.textContent = 'Generating...';
    mindmapContainer.classList.add('loading');

    try {
        const response = await fetch('/api/mindmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: SESSION_ID
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate mindmap');
        }

        const data = await response.json();
        renderMindmap(data.mindmap);
    } catch (error) {
        console.error('Error generating mindmap:', error);
        alert('Error generating mindmap. Make sure you have some chat messages first.');
    } finally {
        generateMindmapBtn.disabled = false;
        generateMindmapBtn.textContent = 'Generate Mindmap';
        mindmapContainer.classList.remove('loading');
    }
}

function renderMindmap(data) {
    // Clear previous mindmap
    mindmapContainer.innerHTML = '';

    // Set up dimensions
    const width = mindmapContainer.clientWidth;
    const height = mindmapContainer.clientHeight;

    // Create SVG
    const svg = d3.select('#mindmap')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g')
        .attr('transform', `translate(${width / 2},${height / 2})`);

    // Create tree layout
    const tree = d3.tree()
        .size([2 * Math.PI, Math.min(width, height) / 2 - 100])
        .separation((a, b) => (a.parent == b.parent ? 1 : 2) / a.depth);

    // Create hierarchy
    const root = d3.hierarchy(data);
    tree(root);

    // Add links
    g.selectAll('.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', d3.linkRadial()
            .angle(d => d.x)
            .radius(d => d.y));

    // Add nodes
    const node = g.selectAll('.node')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => `
            rotate(${d.x * 180 / Math.PI - 90})
            translate(${d.y},0)
        `);

    node.append('circle')
        .attr('r', d => d.depth === 0 ? 8 : 5);

    node.append('text')
        .attr('dy', '0.31em')
        .attr('x', d => d.x < Math.PI === !d.children ? 6 : -6)
        .attr('text-anchor', d => d.x < Math.PI === !d.children ? 'start' : 'end')
        .attr('transform', d => d.x >= Math.PI ? 'rotate(180)' : null)
        .text(d => {
            const maxLength = 30;
            return d.data.name.length > maxLength
                ? d.data.name.substring(0, maxLength) + '...'
                : d.data.name;
        })
        .clone(true).lower()
        .attr('stroke', 'white')
        .attr('stroke-width', 3);

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
            g.attr('transform', `translate(${width / 2},${height / 2}) ${event.transform}`);
        });

    svg.call(zoom);
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', clearChat);
generateMindmapBtn.addEventListener('click', generateMindmap);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Focus on input on load
messageInput.focus();
