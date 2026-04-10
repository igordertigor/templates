{% if cookiecutter.add_frontend == "y" %}
import { UserManager, WebStorageStateStore } from "oidc-client-ts";

export const userManager = new UserManager({
  authority: import.meta.env.VITE_ZITADEL_DOMAIN,
  client_id: import.meta.env.VITE_ZITADEL_CLIENT_ID,
  redirect_uri: `${window.location.origin}/auth/callback`,
  post_logout_redirect_uri: window.location.origin,
  response_type: "code",
  scope: "openid email profile offline_access",
  userStore: new WebStorageStateStore({ store: window.localStorage }),
});

export const login = () => userManager.signinRedirect();
export const logout = () => userManager.signoutRedirect();
export const handleCallback = () => userManager.signinRedirectCallback();
export const getUser = () => userManager.getUser();
{% endif %}
