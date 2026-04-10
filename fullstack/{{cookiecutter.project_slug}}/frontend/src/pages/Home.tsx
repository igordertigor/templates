{% if cookiecutter.add_frontend == "y" %}
import { Button, Container, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { getUser, login, logout } from "../auth/oidc";

export function Home() {
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    getUser().then((user) => setEmail(user?.profile.email ?? null));
  }, []);

  return (
    <Container mt="xl">
      <Title>{{ cookiecutter.project_name }}</Title>
      {email ? (
        <>
          <Text mt="md">Logged in as {email}</Text>
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
