// File: netlify/functions/add.js

const { MongoClient } = require('mongodb');

const mongoUri = process.env.MONGO_URI;

exports.handler = async (event) => {
  // We only care about POST requests from Telegram
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const body = JSON.parse(event.body);
    const messageText = body.message.text || '';

    if (!messageText.startsWith('/add ')) {
      // If it's not our command, do nothing.
      return { statusCode: 200, body: 'OK' };
    }

    // --- Parsing the command ---
    // Format: /add Title | Link1, Link2, ...
    const commandBody = messageText.substring(5); // Remove '/add '
    const parts = commandBody.split('|');
    if (parts.length !== 2) throw new Error('Invalid format.');

    const title = parts[0].trim();
    const links = parts[1].split(',').map(link => link.trim());

    if (!title || links.length === 0) throw new Error('Title or links are missing.');
    // --- End of Parsing ---

    const client = new MongoClient(mongoUri);
    await client.connect();
    const database = client.db('link_database');
    const collection = database.collection('links');

    // Find the document with the matching title or create it if it doesn't exist.
    // Add the new links to the 'links' array without creating duplicates.
    await collection.updateOne(
      { title: { $regex: new RegExp(`^${title}$`, 'i') } }, // Case-insensitive title match
      { 
        $addToSet: { links: { $each: links } }, // Add links to the set
        $setOnInsert: { title: title } // Set the title only if creating a new document
      },
      { upsert: true } // This option creates the document if it doesn't exist
    );

    await client.close();

    // Respond to Telegram's server to let it know we received the message.
    return { statusCode: 200, body: 'OK' };

  } catch (error) {
    console.error('Error:', error);
    // Still return 200 so Telegram doesn't keep resending the message.
    return { statusCode: 200, body: 'Error processing command.' };
  }
};
