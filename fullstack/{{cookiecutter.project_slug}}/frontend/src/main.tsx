{% if cookiecutter.add_frontend == "y" %}
import { MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import { ApolloProvider } from "@apollo/client";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router";
import { apolloClient } from "./apollo";
import { router } from "./router";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider>
      <ApolloProvider client={apolloClient}>
        <RouterProvider router={router} />
      </ApolloProvider>
    </MantineProvider>
  </StrictMode>
);
{% endif %}
