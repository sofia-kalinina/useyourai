import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
} from 'amazon-cognito-identity-js';

const getUserPool = () =>
  new CognitoUserPool({
    UserPoolId: window.ENV?.COGNITO_USER_POOL_ID,
    ClientId: window.ENV?.COGNITO_CLIENT_ID,
  });

export const signUp = (email, password) =>
  new Promise((resolve, reject) => {
    getUserPool().signUp(email, password, [], null, (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });

export const confirmRegistration = (email, code) =>
  new Promise((resolve, reject) => {
    const user = new CognitoUser({ Username: email, Pool: getUserPool() });
    user.confirmRegistration(code, true, (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });

export const signIn = (email, password) =>
  new Promise((resolve, reject) => {
    const user = new CognitoUser({ Username: email, Pool: getUserPool() });
    const authDetails = new AuthenticationDetails({ Username: email, Password: password });
    user.authenticateUser(authDetails, {
      onSuccess: (session) => {
        const sub = session.getIdToken().payload.sub;
        resolve({ sub });
      },
      onFailure: reject,
    });
  });

export const signOut = () => {
  const user = getUserPool().getCurrentUser();
  if (user) user.signOut();
};

// Returns { sub } if a valid or refreshable session exists, rejects otherwise.
export const refreshSession = () =>
  new Promise((resolve, reject) => {
    const user = getUserPool().getCurrentUser();
    if (!user) { reject(new Error('No current user')); return; }
    user.getSession((err, session) => {
      if (err || !session?.isValid()) { reject(err || new Error('Invalid session')); return; }
      resolve({ sub: session.getIdToken().payload.sub });
    });
  });

// Returns the access token JWT string for the current session, or rejects.
export const getAccessToken = () =>
  new Promise((resolve, reject) => {
    const user = getUserPool().getCurrentUser();
    if (!user) { reject(new Error('No current user')); return; }
    user.getSession((err, session) => {
      if (err || !session?.isValid()) { reject(err || new Error('Invalid session')); return; }
      resolve(session.getAccessToken().getJwtToken());
    });
  });
