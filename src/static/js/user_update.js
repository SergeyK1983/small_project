"use strict";

document.addEventListener("DOMContentLoaded", () => {

    /* API */
    const USER_API_URL = "/auth/v1/user";
    const UPDATE_USER_API_URL = "/auth/v1/update-user";

    /* DOM */
    const form = document.getElementById("update-user-form");
    const submitButton = document.getElementById("submit-button");
    const errorState = document.getElementById("error-state");
    const errorMessage = document.getElementById("error-message");
    const successState = document.getElementById("success-state");
    const successMessage = document.getElementById("success-message");

    /* Fields */
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const firstNameInput = document.getElementById("first-name");
    const secondNameInput = document.getElementById("second-name");
    const lastNameInput = document.getElementById("last-name");

    /* Field errors */
    const usernameError = document.getElementById("username-error");
    const emailError = document.getElementById("email-error");
    const firstNameError = document.getElementById("first-name-error");
    const secondNameError = document.getElementById("second-name-error");
    const lastNameError = document.getElementById("last-name-error");

    /* Show error */
    function showError(message) {
        errorMessage.textContent = message;
        errorState.hidden = false;
        successState.hidden = true;
    }

    /* Hide error */
    function hideError() {
        errorState.hidden = true;
    }

    /* Show success */
    function showSuccess(message) {
        successMessage.textContent = message;
        successState.hidden = false;
        errorState.hidden = true;
    }

    /* Clear field errors */
    function clearFieldErrors() {
        usernameError.textContent = "";
        emailError.textContent = "";
        firstNameError.textContent = "";
        secondNameError.textContent = "";
        lastNameError.textContent = "";
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

    /* Load current user */
    async function loadUser() {
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

            /* Пользователь не авторизован */
            if (response.status === 401) {
                window.location.href = "/dev";
                return;
            }
            const data = await response.json();

            if (!response.ok) {
                showError(getApiErrorMessage(data));
                return;
            }

        } catch (error) {
            console.error("Load user error:", error);
            showError("Не удалось загрузить данные пользователя.");
        }
    }

    /* Build request body */
    function getFormData() {
        return {
            username: usernameInput.value.trim() || null,
            email: emailInput.value.trim() || null,
            first_name: firstNameInput.value.trim() || null,
            second_name: secondNameInput.value.trim() || null,
            last_name: lastNameInput.value.trim() || null
        };
    }

    /* Submit */
    form.addEventListener("submit", async (event) => {

        event.preventDefault();
        hideError();
        clearFieldErrors();

        submitButton.disabled = true;
        submitButton.textContent = "Сохранение...";

        const requestData = getFormData();

        try {
            const response = await fetch(
                UPDATE_USER_API_URL,
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

            /* Авторизация истекла или cookie отсутствует. */
            if (response.status === 401) {
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            /* Ошибка backend. */
            if (!response.ok) {
                showError(getApiErrorMessage(data));
                return;
            }

            /* Успешное обновление. */
            showSuccess("Данные успешно обновлены.");

            /* Через небольшую паузу возвращаемся в профиль. */
            setTimeout(() => {
                    window.location.href = "/dev/user";
                },
                500
            );

        } catch (error) {
            console.error("Update user error:", error);
            showError("Не удалось обновить данные.");

        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Сохранить изменения";
        }
    });

    /* Initial load */
    loadUser();

});
