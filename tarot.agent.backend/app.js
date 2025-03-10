const express = require('express');
const fetch = require('node-fetch'); // Ensure you have node-fetch installed
const crypto = require('crypto');
const app = express();
const redis = require('redis');
const FormData = require('form-data');

// Generate a new secret each time the app starts
const TELEGRAM_SECRET = crypto.randomBytes(32).toString('hex');
const TELERGAM_WEBHOOK_URL = `https://tarot.soniclords.com/api/telegram/hook`;

const redisClient = redis.createClient({
    host: '127.0.0.1',
    port: 6379
});
// Connect to the KeyDB/Redis server
redisClient.on('error', (err) => console.error('Redis/KeyDB Client Error', err));
redisClient.connect();
app.use(express.json());

// Single page route at "/"
app.get('/', (req, res) => {
    res.send('Welcome to tairot agent homepage!');
});

// /api router with a POST /hello-world route
const apiRouter = express.Router();

// Helper function to format seconds into hours, minutes, and seconds
function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    let parts = [];
    if (h > 0) parts.push(`${h} ${h === 1 ? 'hour' : 'hours'}`);
    if (m > 0) parts.push(`${m} ${m === 1 ? 'minute' : 'minutes'}`);
    if (s > 0 || parts.length === 0) parts.push(`${s} ${s === 1 ? 'second' : 'seconds'}`);
    return parts.join(', ');
}

// A helper function to check if the user is allowed to trigger a reading.
const checkRateLimit = async (userId) => {
    const key = `telegram_user:${userId}`;
    // Check if the key exists
    const exists = await redisClient.exists(key);
    if (!exists) {
        // Key doesn't exist, so we set it with a 1-hour expiration (3600 seconds)
        const one_second = 1;
        const one_hour = 3600;
        const one_day = 86400;
        const half_a_day = 43200;
        await redisClient.setEx(key, half_a_day, '1');
        return true; // Allowed
    } else {
        // Get the remaining time-to-live in seconds
        const ttl = await redisClient.ttl(key);
        return ttl; // Return the remaining seconds the user must wait
    }
};

const tarotCommand = async ({ user_id, chat_id, username, isGroup }) => {
    // Check if the user is allowed to trigger a new reading
    const rateLimitResult = await checkRateLimit(user_id);
    if (rateLimitResult !== true) {
        // Convert the remaining seconds into a human readable string
        const humanReadableTime = formatTime(rateLimitResult);

        // Compose a message that mentions the user if the command came from a group
        const message = isGroup
            ? `@${username} please wait ${humanReadableTime} before requesting another reading.`
            : `Please wait ${humanReadableTime} before requesting another reading.`;

        // Determine the target chat: use the group chat ID if in a group, else the user's ID
        const targetChatId = isGroup ? chat_id : user_id;
        await callAgentAction('http://localhost:8000/agent/action', {
            connection: "telegram",
            action: "send-message",
            params: [`${targetChatId}`, message]
        }, "POST");
        return;
    }


    // Notify the user that the reading is starting
    const startMessage = isGroup
        ? `@${username} Performing your reading... please wait...`
        : `Performing your reading... please wait...`;
    const targetChatId = isGroup ? chat_id : user_id;
    await callAgentAction('http://localhost:8000/agent/action', {
        connection: "telegram",
        action: "send-message",
        params: [`${targetChatId}`, startMessage]
    }, "POST");

    // Process tarot reading asynchronously
    callAgentAction('http://localhost:8000/agent/action', {
        connection: "tarot-reader",
        action: "perform-reading",
        params: []
    }).then(async response => {
        console.log(response);
        const { status, result } = response;
        if (status !== 'success') {
            console.error("Something went wrong...");
            return;
        }
        const { image_url, reading_long, reading_short, prompt } = result;
        // let imageBuffer;
        const resultMessage = isGroup
            ? `@${username} ${reading_long}`
            : `${reading_long}`;
        const yourDivination = isGroup
            ? `@${username}`
            : ``;

        await callAgentAction('http://localhost:8000/agent/action', {
            connection: "telegram",
            action: "send-message",
            params: [`${targetChatId}`, resultMessage]
        }, "POST");
        // First, send the reading text message
        await callAgentAction('http://localhost:8000/agent/action', {
            connection: "telegram",
            action: "send-message-with-image",
            params: [`${targetChatId}`, yourDivination, image_url]
        }, "POST");
        console.log({ prompt });
    }).catch(err => {
        console.error('Error processing tarot reading:', err);
    });
}

apiRouter.post('/telegram/hook', (req, res) => {
    // Check for secret token in the headers
    const secret = req.headers['x-telegram-bot-api-secret-token'];
    if (secret !== process.env.TELEGRAM_SECRET) {
        return res.status(403).json({ error: 'Unauthorized' });
    }

    // Use req.body as the update
    const update = req.body;
    console.log('Telegram Hook Received:', update);

    // Immediately acknowledge the update to Telegram
    res.json({ status: 'ok' });

    // Process the update asynchronously
    if (update.message && update.message.text) {
        const { text, entities, from, chat } = update.message;
        // Look for a bot_command entity
        if (entities && entities.length > 0) {
            const commandEntity = entities.find(entity => entity.type === 'bot_command');
            if (commandEntity) {
                const command = text.substring(commandEntity.offset, commandEntity.offset + commandEntity.length);
                console.log('Received command:', command);
                // Check if command starts with /tarot, regardless of what follows
                if (command.startsWith('/tarot')) {
                    // Determine if the command is coming from a group
                    const isGroup = chat.type === 'group' || chat.type === 'supergroup';
                    // Pass additional context: chat_id for group responses and username for mentions
                    tarotCommand({
                        user_id: from.id,
                        chat_id: chat.id,
                        username: from.username, // or use from.first_name if username is not set
                        isGroup
                    });
                }
            }
        }
    }
});

app.use('/api', apiRouter);

// Function to call the external POST route using node-fetch
const callAgentAction = async (url, body, method = "POST") => {
    try {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (method === "POST") {
            options["body"] = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log('Called', url, 'successfully.', body);
        const json = await response.json();
        return json;
    } catch (error) {
        console.error('Error calling', url, ':', error);
        return {}
    }
};

const PORT = process.env.PORT || 3000;

// Start the server and call the external route on startup
const server = app.listen(PORT, async () => {
    console.log(`Server is listening on port ${PORT}`);
    await callAgentAction('http://localhost:8000/agents/tarot-reader/load', {});
    await callAgentAction('http://localhost:8000/connections/goat/status', {}, "GET");
    await callAgentAction('http://localhost:8000/connections/telegram/status', {}, "GET");
    await callAgentAction('http://localhost:8000/agent/action', {
        connection: "telegram",
        action: "set-webhook",
        params: [TELERGAM_WEBHOOK_URL, TELEGRAM_SECRET, "message"]
    });
    await callAgentAction('http://localhost:8000/agent/start', {});
});

// Graceful shutdown: call the external route and then shut down the server
const gracefulShutdown = async () => {
    console.log('Server is shutting down...');
    // /agents/{name}/load 
    await callAgentAction('http://localhost:8000/agent/stop', {});
    await callAgentAction('http://localhost:8000/agent/action', {
        connection: "telegram",
        action: "delete-webhook",
        params: []
    }).finally(() => {
        server.close(() => {
            console.log('Server closed.');
            process.exit(0);
        });
    })
};

// Listen for termination signals (e.g., Ctrl+C or a kill command)
process.on('SIGINT', gracefulShutdown);
process.on('SIGTERM', gracefulShutdown);
