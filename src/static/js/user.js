"use strict";


document.addEventListener("DOMContentLoaded", () => {
    /* API */
    const USER_API_URL = "/auth/v1/user";
    const LOGOUT_API_URL = "/auth/v1/logout";
    const DELETE_USER_API_URL = "/auth/v1/delete-user";

    /* DOM */
    const loadingState =            document.getElementById("loading-state");
    const errorState =              document.getElementById("error-state");
    const userContent =             document.getElementById("user-content");
    const errorMessage =            document.getElementById("error-message");
    const welcomeMessage =          document.getElementById("welcome-message");
    const retryButton =             document.getElementById("retry-button");
    const logoutButton =            document.getElementById("logout-button");
    const deleteAccountButton =     document.getElementById("delete-account-button");
    const adminUsersLink =          document.getElementById("admin-users-link");

    /* User fields */
    const userId =              document.getElementById("user-id");
    const userUsername =        document.getElementById("user-username");
    const userEmail =           document.getElementById("user-email");
    const userFullName =        document.getElementById("user-full-name");
    const userFirstName =       document.getElementById("user-first-name");
    const userSecondName =      document.getElementById("user-second-name");
    const userLastName =        document.getElementById("user-last-name");
    const userActive =          document.getElementById("user-active");
    const userStaff =           document.getElementById("user-staff");
    const userSuperuser =       document.getElementById("user-superuser");


    /* Page state */
    function showState(state) {
        loadingState.hidden = state !== "loading";
        errorState.hidden = state !== "error";
        userContent.hidden = state !== "content";
    }

    /* API error */
    function getApiErrorMessage(data) {

        if (!data) {
            return "Произошла неизвестная ошибка.";
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


    /* Load user */
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

            /* Если авторизация отсутствует. */
            if (response.status === 401) {
                window.location.href = "/";
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                errorMessage.textContent = getApiErrorMessage(data);
                showState("error");
                return;
            }

            renderUser(data);
            showState("content");

        } catch (error) {
            console.error( "Load user error:", error);
            errorMessage.textContent = "Не удалось подключиться к серверу.";
            showState("error");
        }
    }

    /* Render user */
    function renderUser(user) {

        userId.textContent = user.id ?? "—";
        userUsername.textContent = user.username ?? "—";
        userEmail.textContent = user.email ?? "—";
        userFullName.textContent = user.full_name || "—";
        userFirstName.textContent = user.first_name || "—";
        userSecondName.textContent = user.second_name || "—";
        userLastName.textContent = user.last_name || "—";
        userActive.textContent = user.is_active ? "Да": "Нет";
        userStaff.textContent = user.is_staff ? "Да": "Нет";
        userSuperuser.textContent = user.is_superuser ? "Да": "Нет";

        welcomeMessage.textContent = `Добро пожаловать, ${user.username}!`;

        /* Показываем админскую ссылку только суперпользователю. */
        adminUsersLink.hidden = !user.is_superuser;
    }

    /*Retry*/
    retryButton.addEventListener("click", () => {
        loadUser();
    });

    /* Logout */
    logoutButton.addEventListener("click", async () => {
        logoutButton.disabled = true;
        logoutButton.textContent = "Выход...";
        
        try {
            const response = await fetch(
                LOGOUT_API_URL,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            if (response.ok) {
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            errorMessage.textContent = getApiErrorMessage(data);
            showState("error");

        } catch (error) {
            console.error("Logout error:", error);
            errorMessage.textContent = "Не удалось выполнить выход.";
            showState("error");

        } finally {
            logoutButton.disabled = false;
            logoutButton.textContent = "Выйти";
        }
    });

    /* Delete account */
    deleteAccountButton.addEventListener("click", async () => {
        const confirmed = window.confirm("Вы действительно хотите удалить аккаунт?");
        
        if (!confirmed) {
            return;
        }

        deleteAccountButton.disabled = true;
        deleteAccountButton.textContent = "Удаление...";

        try {
            const response = await fetch(
                DELETE_USER_API_URL,
                {
                    method: "DELETE",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            if (response.ok) {
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            window.alert(getApiErrorMessage(data));

        } catch (error) {
            console.error("Delete account error:", error);
            window.alert("Не удалось удалить аккаунт.");

        } finally {
            deleteAccountButton.disabled = false;
            deleteAccountButton.textContent = "Удалить аккаунт";
        }

    });

    /* Initial load */
    loadUser();
});
