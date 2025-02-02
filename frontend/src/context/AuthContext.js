import React, { createContext, useState, useContext, useEffect } from 'react';
import Keycloak from 'keycloak-js';

const AuthContext = createContext(null);

const keycloak = new Keycloak({
  url: process.env.REACT_APP_KEYCLOAK_URL,
  realm: process.env.REACT_APP_KEYCLOAK_REALM,
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID
});

export const AuthProvider = ({ children }) => {
  const [initialized, setInitialized] = useState(false);
  const [token, setToken] = useState(null);

  useEffect(() => {
    keycloak.init({
      onLoad: 'check-sso',
      silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html'
    }).then(authenticated => {
      if (authenticated) {
        setToken(keycloak.token);
        // 设置token刷新
        setInterval(() => {
          keycloak.updateToken(70).then((refreshed) => {
            if (refreshed) {
              setToken(keycloak.token);
            }
          }).catch(() => {
            console.error('Failed to refresh token');
          });
        }, 60000);
      }
      setInitialized(true);
    });
  }, []);

  const login = () => {
    keycloak.login();
  };

  const logout = () => {
    keycloak.logout();
  };

  const value = {
    token,
    login,
    logout,
    isAuthenticated: !!token,
    initialized
  };

  if (!initialized) {
    return <div>Loading...</div>;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
