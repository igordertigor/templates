{% if cookiecutter.add_frontend == "y" and cookiecutter.add_strawberry == "y" %}
import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { userManager } from "./auth/oidc";

const httpLink = createHttpLink({
  uri: "/graphql",
});

// Attach the access token from Authentik to every GraphQL request
const authLink = setContext(async (_, { headers }) => {
  const user = await userManager.getUser();
  return {
    headers: {
      ...headers,
      authorization: user?.access_token ? `Bearer ${user.access_token}` : "",
    },
  };
});

export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
{% endif %}
