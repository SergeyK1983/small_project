"use strict";


/* API endpoints */
const LOGIN_URL = "/auth/v1/login";
const SIGNUP_URL = "/auth/v1/signup";


/* Login elements */
const loginSection = document.getElementById("login-section");
const loginForm = document.getElementById("login-form");
const loginUsernameInput = document.getElementById("login-username");
const loginPasswordInput = document.getElementById("login-password");
const loginSubmitButton = document.getElementById("login-submit");
const loginError = document.getElementById("login-error");


/* Signup elements */
const signupSection = document.getElementById("signup-section");
const signupForm = document.getElementById("signup-form");
const signupUsernameInput = document.getElementById("signup-username");
const signupEmailInput = document.getElementById("signup-email");
const signupPasswordInput = document.getElementById("signup-password");
const signupSubmitButton = document.getElementById("signup-submit");
const signupError = document.getElementById("signup-error");
const signupSuccess = document.getElementById("signup-success");


/* Navigation buttons */
const showSignupButton = document.getElementById("show-signup-button");
const showLoginButton = document.getElementById("show-login-button");

/* Email validation */

function isEmail(value) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(value);
}


/* Display error */

function showError(element, message) {
    element.textContent = message;
    element.hidden = false;
}


/* Hide error */

function hideError(element) {
    element.textContent = "";
    element.hidden = true;
}


/* Switch to signup form */

showSignupButton.addEventListener("click", () => {
        hideError(loginError);

        loginSection.hidden = true;
        signupSection.hidden = false;

        signupUsernameInput.focus();
    }
);


/* Switch to login form */

showLoginButton.addEventListener("click", () => {
        hideError(signupError);
        hideError(signupSuccess);

        signupSection.hidden = true;
        loginSection.hidden = false;

        loginUsernameInput.focus();
    }
);


/* Login */

loginForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        hideError(loginError);

        const usernameOrEmail =
            loginUsernameInput.value.trim();

        const password =
            loginPasswordInput.value;


        /* Browser HTML validation */

        if (!usernameOrEmail) {
            showError(
                loginError,
                "Введите username или email."
            );

            return;
        }


        if (!password) {
            showError(
                loginError,
                "Введите пароль."
            );

            return;
        }


        /* Формируем JSON для backend. Email или username */

        const payload = {
            password: password
        };

        if (isEmail(usernameOrEmail)) {
            payload.email = usernameOrEmail;
        } else {
            payload.username = usernameOrEmail;
        }


        /* Блокируем кнопку, чтобы пользователь не отправил несколько запросов подряд. */
        loginSubmitButton.disabled = true;
        loginSubmitButton.textContent = "Вход...";

        try {
            const response = await fetch(
                LOGIN_URL,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify(payload)
                }
            );
            
            const data = await response.json();

            /* Ошибка backend. */
            if (!response.ok) {
                showError(
                    loginError,
                    getApiErrorMessage(data)
                );
                return;
            }

            /* Успешный вход. Токен в куке */
            window.location.href = "/dev/user";

        } catch (error) {
            console.error("Login error:", error);
            showError(loginError, "Не удалось выполнить вход. Попробуйте еще раз.");
        } finally {
            loginSubmitButton.disabled = false;
            loginSubmitButton.textContent = "Войти";
        }
    }
);

/* Signup */

signupForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        hideError(signupError);
        hideError(signupSuccess);


        const username = signupUsernameInput.value.trim();
        const email = signupEmailInput.value.trim();
        const password = signupPasswordInput.value;

        /* Дополнительная клиентская проверка. */

        if (!username) {
            showError(signupError, "Введите username.");
            return;
        }

        if (!email) {
            showError(signupError, "Введите email.");
            return;
        }

        if (!password) {
            showError(signupError, "Введите пароль.");
            return;
        }

        const payload = {
            username: username,
            email: email,
            password: password
        };


        signupSubmitButton.disabled = true;
        signupSubmitButton.textContent = "Регистрация...";

        try {
            const response = await fetch(
                SIGNUP_URL,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify(payload)
                }
            );

            const data = await response.json();

            if (!response.ok) {
                showError(
                    signupError,
                    getApiErrorMessage(data)
                );
                return;
            }

            /* Регистрация успешна. */
            signupForm.reset();
            signupSuccess.textContent = "Регистрация успешно завершена. Теперь войдите в систему.";
            signupSuccess.hidden = false;

        } catch (error) {
            console.error("Signup error:", error);
            showError(signupError, "Не удалось выполнить регистрацию. Попробуйте еще раз.");
        } finally {
            signupSubmitButton.disabled = false;
            signupSubmitButton.textContent = "Зарегистрироваться";
        }
    }
);


/*
 * Обработка JSON ошибок FastAPI / backend. 
 */

function getApiErrorMessage(data) {

    if (!data) {
        return "Произошла неизвестная ошибка.";
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {

        return data.detail
            .map(
                (error) => error.msg || "Ошибка валидации."
            )
            .join(" ");
    }

    if (typeof data.message === "string") {
        return data.message;
    }

    return "Произошла ошибка. Попробуйте еще раз.";
}
