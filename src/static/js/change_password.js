"use strict";

document.addEventListener("DOMContentLoaded", () => {

    /* API */
    const USER_API_URL = "/auth/v1/user";
    const CHANGE_PASSWORD_API_URL = "/auth/v1/change-password";

    /* DOM */
    const loadingState = document.getElementById("loading-state");
    const errorState = document.getElementById("error-state");
    const passwordContent = document.getElementById("password-content");
    const errorMessage = document.getElementById("error-message");
    const form = document.getElementById("change-password-form");
    const submitButton = document.getElementById("submit-button");

    /* Fields */
    const emailInput = document.getElementById("email");
    const passwordOldInput = document.getElementById("password-old");
    const passwordNewInput = document.getElementById("password-new");
    const passwordRepInput = document.getElementById("password-rep");

    /* Field errors */
    const emailError = document.getElementById("email-error");
    const passwordOldError = document.getElementById("password-old-error");
    const passwordNewError = document.getElementById("password-new-error");
    const passwordRepError = document.getElementById("password-rep-error");

    /* Page state */
    function showState(state) {
        loadingState.hidden = state !== "loading";
        errorState.hidden = state !== "error";
        passwordContent.hidden = state !== "content";
    }

    /* API error message */
    function getApiErrorMessage(data) {
        if (!data) {
            return ("Произошла неизвестная ошибка.");
        }

        if (typeof data.detail === "string") {
            return data.detail;
        }

        if (Array.isArray(data.detail)) {
            return data.detail
                .map(error => error.msg || "Ошибка валидации.")
                .join(" ");
        }

        if (typeof data.message === "string") {
            return data.message;
        }

        return (
            "Произошла ошибка. " +
            "Попробуйте еще раз."
        );
    }

    /* Clear field errors */
    function clearFieldErrors() {
        emailError.textContent = "";
        passwordOldError.textContent = "";
        passwordNewError.textContent = "";
        passwordRepError.textContent = "";
    }

    /* Load current user */
    async function loadUser() {
        showState("loading");

        try {
            const response = await fetch(
                USER_API_URL,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            /* Пользователь не авторизован. */
            if (response.status === 401) {
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                errorMessage.textContent = getApiErrorMessage(data);
                showState("error");
                return;
            }

            /* Email пользователя используем для запроса смены пароля. */
            emailInput.value = data.email ?? "";
            showState("content");

        } catch (error) {
            console.error("Load user error:", error);
            errorMessage.textContent = "Не удалось загрузить данные пользователя.";
            showState("error");
        }
    }

    /* Submit change password */
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearFieldErrors();

        /* Проверяем новые пароли до отправки на backend. */
        const passwordNew = passwordNewInput.value;
        const passwordRep = passwordRepInput.value;

        if (passwordNew !== passwordRep) {
            passwordRepError.textContent = "Новые пароли не совпадают.";
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Смена пароля...";

        const requestData = {
            email: emailInput.value.trim(),
            password_old: passwordOldInput.value,
            password_new: passwordNew,
            password_rep: passwordRep
        };

        try {
            const response = await fetch(
                CHANGE_PASSWORD_API_URL,
                {
                    method: "PATCH",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    credentials: "same-origin",
                    body: JSON.stringify(requestData)
                }
            );

            /* Авторизация отсутствует или токен истёк. */
            if (response.status === 401) {
                console.log("нет авторизации")
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            /* Backend вернул ошибку. */
            if (!response.ok) {
                errorMessage.textContent = getApiErrorMessage(data);
                showState("error");
                return;
            }

            /* Пароль успешно изменён. По требованиям backend: пользователь должен быть принудительно выведен. */
            window.location.href = "/dev";

        } catch (error) {
            console.error("Change password error:", error);
            errorMessage.textContent = "Не удалось изменить пароль.";
            showState("error");

        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Сменить пароль";
        }
    });

    /* Initial load */
    loadUser();

});
