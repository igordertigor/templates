{% if cookiecutter.add_frontend == "y" %}
import { Button, Container, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { getUser, login, logout } from "../auth/oidc";
{% if cookiecutter.add_strawberry == "n" %}
import { useCurrentUser } from "../api/users";
{% endif %}

export function Home() {
  const [email, setEmail] = useState<string | null>(null);
  {% if cookiecutter.add_strawberry == "n" %}
  const { data: currentUser, isLoading, error } = useCurrentUser();
  {% endif %}

  useEffect(() => {
    getUser().then((user) => setEmail(user?.profile.email ?? null));
  }, []);

  return (
    <Container mt="xl">
      <Title>{{ cookiecutter.project_name }}</Title>
      {email ? (
        <>
          <Text mt="md">Logged in as {email}</Text>
          {% if cookiecutter.add_strawberry == "n" %}
          {isLoading && <Text mt="md" c="dimmed">Loading user data...</Text>}
          {error && <Text mt="md" c="red">Error loading user data</Text>}
          {currentUser && (
            <Text mt="md" c="dimmed">
              User ID: {currentUser.id} | Active: {currentUser.is_active ? "Yes" : "No"}
            </Text>
          )}
          {% endif %}
          <Button mt="md" onClick={logout}>
            Log out
          </Button>
        </>
      ) : (
        <Button mt="md" onClick={login}>
          Log in
        </Button>
      )}
    </Container>
  );
}
{% endif %}
