{% if cookiecutter.add_frontend == "y" %}
import { MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
{% if cookiecutter.add_strawberry == "y" %}
import { ApolloProvider } from "@apollo/client";
import { apolloClient } from "./apollo";
{% else %}
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { queryClient } from "./query-client";
{% endif %}
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router";
import { router } from "./router";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider>
      {% if cookiecutter.add_strawberry == "y" %}
      <ApolloProvider client={apolloClient}>
        <RouterProvider router={router} />
      </ApolloProvider>
      {% else %}
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
      {% endif %}
    </MantineProvider>
  </StrictMode>
);
{% endif %}
