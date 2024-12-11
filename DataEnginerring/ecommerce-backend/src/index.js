const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const mongoose = require('mongoose');
const schema = require('./schema');

// MongoDB connection URL (replace with your actual connection string)
const dbURI = 'your-mongo-db-connection-string-here';

mongoose.connect(dbURI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => {
    console.log('MongoDB connected');
  })
  .catch(err => {
    console.error('MongoDB connection error:', err);
  });

const app = express();

// GraphQL endpoint
app.use('/graphql', graphqlHTTP({
  schema,
  graphiql: true,  // Enable GraphiQL tool in the browser
}));

// Start the server
app.listen(4000, () => {
  console.log('Server running on http://localhost:4000/graphql');
});
