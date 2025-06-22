// File: netlify/functions/search.js

const { MongoClient } = require('mongodb');

// Get our secret connection string from environment variables
const mongoUri = process.env.MONGO_URI;

exports.handler = async (event) => {
  // Get the search query from the URL (e.g., ?q=the_dark_knight)
  const query = event.queryStringParameters.q;

  if (!query) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Search query is required.' }),
    };
  }

  const client = new MongoClient(mongoUri);

  try {
    await client.connect();
    const database = client.db('link_database'); // You can name your database anything
    const collection = database.collection('links'); // And your collection anything

    // Perform a case-insensitive search
    const result = await collection.findOne({ 
      title: { $regex: new RegExp(`^${query}$`, 'i') } 
    });

    if (!result) {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: 'No results found.' }),
      };
    }

    return {
      statusCode: 200,
      body: JSON.stringify(result),
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to connect to or search the database.' }),
    };
  } finally {
    await client.close();
  }
};
