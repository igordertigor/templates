{% if cookiecutter.add_frontend == "y" %}
import { createBrowserRouter } from "react-router";
import { AuthCallback } from "./pages/AuthCallback";
import { Home } from "./pages/Home";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/auth/callback",
    element: <AuthCallback />,
  },
]);
{% endif %}
