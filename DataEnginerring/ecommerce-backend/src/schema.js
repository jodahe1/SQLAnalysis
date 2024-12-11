const { GraphQLSchema, GraphQLObjectType, GraphQLString } = require('graphql');

// Define the root query type
const RootQueryType = new GraphQLObjectType({
  name: 'RootQueryType',
  fields: {
    hello: {
      type: GraphQLString,
      resolve() {
        return 'Hello, world!';
      },
    },
  },
});

// Define the GraphQL schema
const schema = new GraphQLSchema({
  query: RootQueryType,
});

module.exports = schema;
