{% if cookiecutter.add_frontend == "y" %}
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { handleCallback } from "../auth/oidc";

export function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    handleCallback()
      .then(() => navigate("/"))
      .catch(console.error);
  }, [navigate]);

  return <p>Completing login…</p>;
}
{% endif %}
