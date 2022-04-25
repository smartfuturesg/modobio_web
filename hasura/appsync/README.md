# AppSync configuration

The files in this directory define the setup of AppSync on AWS. AppSync connects DynamoDB to Hasura. In order to acchieve this, DynamoDB resolvers are created, which are connected to GraphQL queries and mutations. The GraphQL endpoint is then loaded in Hasura as a remote schema.

`DynamoDB -> resolver -> graphql -> Hasura remote schema`

At some point, the AppSync setup will be automated using the `aws` command line interface. For the time being this directory will just act as a repository for resolver and graphql code. This is necessary, since there is no way to back up the code entered through the AWS web console.

The API is written in GraphQL, the resolvers are written in Velocity Template Language (VTL).

# More information

- [AWS AppSync documentation](https://docs.aws.amazon.com/appsync/latest/devguide/what-is-appsync.html)
- [AWS CLI documentation](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/appsync/index.html)
- [GraphQL](https://graphql.org/)
- [VTL language](https://velocity.apache.org/engine/devel/user-guide.html)
